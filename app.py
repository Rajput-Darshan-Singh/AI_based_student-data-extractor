
from flask import Flask, request, jsonify, render_template, send_file, flash, redirect, url_for
import os
import tempfile
import uuid
from werkzeug.utils import secure_filename
import fitz  # PyMuPDF
import requests
import json
import re
import time
import pandas as pd
from word2number import w2n
import threading
import queue


app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'pdf'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Global variables for processing status
processing_status = {}
processing_queue = queue.Queue()
download_status = {}  # Track download status for each task

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ---------------- Helper functions (from your original code) ----------------

def clean_total_marks(total):
    """
    Cleans total marks string into an integer if possible.
    Handles numbers, numbers with commas, and words (e.g., 'Four Hundred Fifteen').
    """
    if total is None:
        return None
    if isinstance(total, (int, float)):
        return int(total)

    if isinstance(total, str):
        s = total.strip()
        if not s:
            return None
        # Remove commas and non-digit extras
        s_clean = re.sub(r"[^\w\s]", "", s)
        try:
            return int(s_clean)
        except ValueError:
            try:
                return w2n.word_to_num(s_clean.lower())
            except Exception:
                return None
    return None

def fallback_total_marks(page, page_text):
    """
    Robust fallback: search page lines/blocks for 'Total Marks' phrasing,
    prefer the 'in words' value, otherwise pick the most-likely numeric (last number on the line).
    """
    # 1) Try line-by-line search using page dict (keeps visual order)
    try:
        pdict = page.get_text("dict", flags=fitz.TEXTFLAGS_TEXT)
        lines = []
        for block in pdict.get("blocks", []):
            for line in block.get("lines", []):
                line_text = "".join([span.get("text", "") for span in line.get("spans", [])]).strip()
                if line_text:
                    lines.append(line_text)
    except Exception:
        lines = page_text.splitlines()

    for idx, line in enumerate(lines):
        low = line.lower()
        if "total marks" in low:
            # combine with next line if it likely contains the value
            context = line
            if idx + 1 < len(lines):
                context = context + " " + lines[idx + 1]

            # 1A. Look for "(in words): <words>" or "in words : <words>"
            m_words = re.search(r"in\s+words[^\w\-]*[:\-]?\s*([a-z\s\-]+)", context, re.IGNORECASE)
            if m_words:
                words = m_words.group(1).strip()
                try:
                    return w2n.word_to_num(words.lower())
                except Exception:
                    # fall through to numeric attempt
                    pass

            # 1B. If no word-form, try to find numeric groups in the same line/context.
            nums = re.findall(r"\d{1,4}", context)
            if nums:
                # Choose the most likely candidate:
                # - prefer the last number on the line (observed pattern: total max appears first)
                try:
                    return int(nums[-1])
                except Exception:
                    pass

    # 2) Global page-text fallback: try to match "Total Marks Obtained (in words): <words>"
    m_global_words = re.search(r"Total\s+Marks\s+Obtained.*?in\s+words[^\w\-]*[:\-]?\s*([A-Za-z\s\-]+)",
                               page_text, re.IGNORECASE | re.DOTALL)
    if m_global_words:
        try:
            return w2n.word_to_num(m_global_words.group(1).strip().lower())
        except Exception:
            pass

    # 3) As last resort, find any occurrence of "Total" followed by numbers and pick last numeric token on that line
    m_lines = page_text.splitlines()
    for line in m_lines[::-1]:  # search from bottom up (total lines often near bottom)
        if "total" in line.lower():
            nums = re.findall(r"\d{1,4}", line)
            if nums:
                try:
                    return int(nums[-1])
                except Exception:
                    continue

    return None

def find_label_variants(name_label_variants):
    patterns = []
    for nl in name_label_variants:
        p = rf"\b{re.escape(nl)}\s*[:\-]?\s*(.+)"
        patterns.append(re.compile(p, re.IGNORECASE))
    return patterns

def extract_father_mother_names(page):
    father = None
    mother = None
    pdict = page.get_text("dict", flags=fitz.TEXTFLAGS_TEXT)
    for block in pdict.get("blocks", []):
        for line in block.get("lines", []):
            line_text = "".join([span["text"] for span in line.get("spans", [])]).strip()
            if not line_text:
                continue
            m = re.search(r"Father\s*Name\s*[:\-]\s*(.+)", line_text, re.IGNORECASE)
            if m:
                father = m.group(1).strip()
            m2 = re.search(r"Mother\s*Name\s*[:\-]\s*(.+)", line_text, re.IGNORECASE)
            if m2:
                mother = m2.group(1).strip()
            if father and mother:
                break
        if father and mother:
            break
    return father, mother

def extract_name_from_lines(page, name_label_patterns, father_name=None, mother_name=None):
    pdict = page.get_text("dict", flags=fitz.TEXTFLAGS_TEXT)
    flattened = []
    for block in pdict.get("blocks", []):
        for line in block.get("lines", []):
            text_line = "".join([span["text"] for span in line.get("spans", [])]).strip()
            if text_line:
                ys = [span["bbox"][1] for span in line["spans"]]
                y = min(ys) if ys else None
                flattened.append((text_line, y))
    flattened = sorted(flattened, key=lambda x: (x[1] if x[1] is not None else 0))
    for idx, (ln_text, y) in enumerate(flattened):
        for pat in name_label_patterns:
            if re.search(rf"\b{pat.pattern.split(r'\s*[:\-]?')[0]}\b", ln_text, re.IGNORECASE):
                m = pat.search(ln_text)
                if m and m.group(1).strip():
                    candidate = m.group(1).strip()
                    if father_name and candidate.lower() == father_name.lower():
                        return None
                    if mother_name and candidate.lower() == mother_name.lower():
                        return None
                    return candidate
                if idx + 1 < len(flattened):
                    next_text, _y2 = flattened[idx+1]
                    if next_text.strip():
                        candidate = next_text.strip()
                        if father_name and candidate.lower() == father_name.lower():
                            return None
                        if mother_name and candidate.lower() == mother_name.lower():
                            return None
                        return candidate
    return None

def extract_name_from_blocks(page, name_label_patterns, father_name=None, mother_name=None):
    blocks = page.get_text("blocks", sort=True)
    for (x0, y0, x1, y1, block_text, block_no, block_type) in blocks:
        if block_type != 0:
            continue
        text = block_text.strip()
        if not text:
            continue
        for pat in name_label_patterns:
            m = pat.search(text)
            if m and m.group(1).strip():
                candidate = m.group(1).strip().split("\n")[0].strip()
                if father_name and candidate.lower() == father_name.lower():
                    continue
                if mother_name and candidate.lower() == mother_name.lower():
                    continue
                return candidate
    return None

def sanitize_model_name(model_name, page_text, father_name=None, mother_name=None):
    if not model_name:
        return None
    mn = model_name.strip()
    if not mn:
        return None
    if father_name and mn.lower() == father_name.lower():
        return None
    if mother_name and mn.lower() == mother_name.lower():
        return None
    lower = page_text.lower()
    for label in ["father name", "mother name", "parent", "guardian"]:
        p1 = rf"{label}\s*[:\-]?\s*{re.escape(mn.lower())}"
        p2 = rf"{re.escape(mn.lower())}\s*[:\-]?\s*{label}"
        if re.search(p1, lower) or re.search(p2, lower):
            return None
    parts = mn.split()
    if len(parts) < 2:
        return None
    if any(char.isdigit() for char in mn):
        return None
    return mn

def select_final_name(page, model_name, name_label_patterns, father_name=None, mother_name=None, page_text=None):
    name_cand = extract_name_from_lines(page, name_label_patterns, father_name, mother_name)
    if name_cand:
        return name_cand
    name_cand = extract_name_from_blocks(page, name_label_patterns, father_name, mother_name)
    if name_cand:
        return name_cand
    safe = sanitize_model_name(model_name, page_text, father_name, mother_name)
    if safe:
        return safe
    return ""

def merge_students(data):
    merged = {}
    for entry in data:
        reg = entry.get("Registration", "").strip()
        if not reg:
            continue
        if reg not in merged:
            merged[reg] = entry.copy()
        else:
            for key in ["Name", "TotalMarks", "SGPA", "Grade"]:
                if not merged[reg].get(key) and entry.get(key):
                    merged[reg][key] = entry[key]
    all_names = {e["Registration"]: e["Name"] for e in data if e.get("Name")}
    for reg, entry in merged.items():
        if not entry.get("Name") and reg in all_names:
            entry["Name"] = all_names[reg]
    return list(merged.values())

# ---------------- Main extraction function ----------------

def extract_with_improved(pdf_path, model_endpoint_url, task_id, name_label_variants=None):
    if name_label_variants is None:
        name_label_variants = ["Student Name", "Name of Student", "Name"]
    name_label_patterns = find_label_variants(name_label_variants)

    try:
        processing_status[task_id] = {"status": "processing", "progress": 0, "message": "Starting PDF processing..."}
        print(f"Starting processing for task {task_id}")
        print(f"PDF path: {pdf_path}")
        print(f"Model endpoint: {model_endpoint_url}")
        
        doc = fitz.open(pdf_path)
        results = []
        total_pages = len(doc)
        start_time = time.time()
        print(f"PDF opened successfully. Total pages: {total_pages}")

        for page_num in range(total_pages):
            page = doc.load_page(page_num)
            elapsed = time.time() - start_time
            avg = elapsed / (page_num + 1)
            remaining = avg * (total_pages - (page_num + 1))
            progress = int((page_num + 1) / total_pages * 100)
            
            processing_status[task_id] = {
                "status": "processing", 
                "progress": progress, 
                "message": f"Processing page {page_num+1}/{total_pages} — approx {remaining:.1f}s remaining"
            }

            page_text = page.get_text("text", sort=True)
            father_name, mother_name = extract_father_mother_names(page)

            prompt = f"""
You are an assistant that extracts student result details from text.
Extract the following fields only:
- Name
- Registration No
- Total Marks Obtained
- SGPA
- Grade

Important:
- If a "Student Name" (or similar student name label) is present in the page, that must be used for the Name.
- If it is NOT present, do NOT use "Father Name" or "Mother Name" as the student Name.
- Return output as JSON ONLY in this format:
{{
    "Name": "",
    "Registration": "",
    "TotalMarks": "",
    "SGPA": "",
    "Grade": ""
}}

Text (page {page_num+1}):
{page_text}
"""
            print(f"Processing page {page_num+1}/{total_pages}...")
            try:
                resp = requests.post(
                    model_endpoint_url,
                    json={"model": "llama3", "prompt": prompt, "stream": False},
                    timeout=30
                )
                
                if resp.status_code != 200:
                    print(f"AI model request failed with status {resp.status_code}: {resp.text}")
                    model_json = {}
                else:
                    model_raw = resp.json().get("response", "")
                    print(f"AI model response received for page {page_num+1}")
                    
                    try:
                        m = re.search(r"\{.*\}", model_raw, re.DOTALL)
                        if m:
                            model_json = json.loads(m.group())
                            print(f"Successfully parsed JSON for page {page_num+1}: {model_json}")
                        else:
                            print(f"No JSON found in response for page {page_num+1}")
                            model_json = {}
                    except Exception as e:
                        print(f"JSON parse error on page {page_num+1}: {e}")
                        print(f"Raw response: {model_raw[:200]}...")
                        model_json = {}
                        
            except requests.exceptions.RequestException as e:
                print(f"Request error on page {page_num+1}: {e}")
                model_json = {}
            except Exception as e:
                print(f"Unexpected error on page {page_num+1}: {e}")
                model_json = {}

            # clean + fallback for Total Marks
            tm = clean_total_marks(model_json.get("TotalMarks", ""))
            if tm is None:
                tm = fallback_total_marks(page, page_text)
            if tm is not None:
                model_json["TotalMarks"] = tm

            model_name = model_json.get("Name", "").strip()
            final_name = select_final_name(page, model_name, name_label_patterns,
                                           father_name=father_name, mother_name=mother_name,
                                           page_text=page_text)

            entry = {
                "Name": final_name,
                "Registration": model_json.get("Registration", "").strip(),
                "TotalMarks": model_json.get("TotalMarks", ""),
                "SGPA": model_json.get("SGPA", "").strip(),
                "Grade": model_json.get("Grade", "").strip()
            }
            results.append(entry)




        doc.close()
        print(f"PDF processing completed. Total results collected: {len(results)}")
        
        processing_status[task_id] = {"status": "processing", "progress": 90, "message": "Merging results..."}
        
        cleaned = merge_students(results)
        print(f"Results merged. Final count: {len(cleaned)}")
        
        # Save to CSV
        df = pd.DataFrame(cleaned)
        df = df[["Name", "Registration", "TotalMarks", "SGPA", "Grade"]]
        output_filename = f"results_{task_id}.csv"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        print(f"Saving CSV file to: {output_path}")
        print(f"DataFrame shape: {df.shape}")
        print(f"DataFrame columns: {df.columns.tolist()}")
        
        df.to_csv(output_path, index=False)
        
        # Verify file was created
        if os.path.exists(output_path):
            print(f"CSV file created successfully: {output_path}")
        else:
            print(f"ERROR: CSV file was not created: {output_path}")
        
        processing_status[task_id] = {
            "status": "completed", 
            "progress": 100, 
            "message": "Processing completed successfully!",
            "output_file": output_filename,
            "records_count": len(cleaned)
        }
        
    except Exception as e:
        print(f"CRITICAL ERROR in processing task {task_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        
        processing_status[task_id] = {
            "status": "error", 
            "progress": 0, 
            "message": f"Error processing PDF: {str(e)}"
        }

# ---------------- Flask Routes ----------------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    model_endpoint = request.form.get('model_endpoint', 'http://localhost:11434/api/generate')
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        # Clean up old files before starting new upload
        try:
            # Clean old upload files
            for filename in os.listdir(app.config['UPLOAD_FOLDER']):
                if filename.endswith('.pdf'):
                    try:
                        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    except OSError as e:
                        print(f"Error removing old upload file: {e}")
            
            # Keep only the last 5 CSV result files
            csv_files = [f for f in os.listdir(app.config['OUTPUT_FOLDER']) if f.endswith('.csv')]
            csv_files.sort(key=lambda x: os.path.getmtime(os.path.join(app.config['OUTPUT_FOLDER'], x)))
            if len(csv_files) > 5:
                for old_file in csv_files[:-5]:  # Remove all but the 5 most recent files
                    try:
                        os.remove(os.path.join(app.config['OUTPUT_FOLDER'], old_file))
                    except OSError as e:
                        print(f"Error removing old CSV file: {e}")
        except Exception as e:
            print(f"Error during cleanup: {e}")
        
        filename = secure_filename(file.filename)
        task_id = str(uuid.uuid4())
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{task_id}_{filename}")
        file.save(file_path)
        
        # Clear old status entries
        old_tasks = [k for k in processing_status.keys()]
        for old_task in old_tasks:
            if old_task != task_id:
                processing_status.pop(old_task, None)
                download_status.pop(old_task, None)
        
        # Start processing in background thread
        thread = threading.Thread(target=extract_with_improved, args=(file_path, model_endpoint, task_id))
        thread.start()
        
        return jsonify({'task_id': task_id, 'message': 'File uploaded and processing started'})
    
    return jsonify({'error': 'Invalid file type. Please upload a PDF file.'}), 400

@app.route('/status/<task_id>')
def get_status(task_id):
    if task_id in processing_status:
        return jsonify(processing_status[task_id])
    else:
        return jsonify({'error': 'Task not found'}), 404

@app.route('/download/<filename>')
def download_file(filename):
    max_retries = 5
    retry_delay = 1  # seconds
    
    task_id = filename.replace('results_', '').replace('.csv', '')
    if task_id:
        download_status[task_id] = 'pending'
    
    for attempt in range(max_retries):
        try:
            file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
            print(f"Attempting to download file (attempt {attempt + 1}/{max_retries}): {file_path}")
            
            if not os.path.exists(file_path):
                if attempt < max_retries - 1:
                    print(f"File not found, waiting {retry_delay} seconds before retry...")
                    time.sleep(retry_delay)
                    continue
                
                print(f"File not found after {max_retries} attempts: {file_path}")
                output_files = os.listdir(app.config['OUTPUT_FOLDER'])
                print(f"Available files in outputs: {output_files}")
                if task_id:
                    download_status[task_id] = 'failed'
                return jsonify({'error': f'File not found: {filename}. Available files: {output_files}'}), 404
            
            return send_file(file_path, as_attachment=True)
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Download attempt {attempt + 1} failed: {str(e)}, retrying...")
                time.sleep(retry_delay)
                continue
            print(f"Download failed after {max_retries} attempts: {str(e)}")
            if task_id:
                download_status[task_id] = 'failed'
            return jsonify({'error': f'Download failed: {str(e)}'}), 500

@app.route('/confirm-download/<task_id>')
def confirm_download(task_id):
    """Confirm that a download has been completed successfully"""
    try:
        download_status[task_id] = 'completed'
        return jsonify({'message': 'Download confirmed'})
    except Exception as e:
        return jsonify({'error': f'Failed to confirm download: {str(e)}'}), 500

@app.route('/debug')
def debug_info():
    """Debug endpoint to check processing status and files"""
    debug_info = {
        "processing_tasks": list(processing_status.keys()),
        "output_files": os.listdir(app.config['OUTPUT_FOLDER']) if os.path.exists(app.config['OUTPUT_FOLDER']) else [],
        "upload_files": os.listdir(app.config['UPLOAD_FOLDER']) if os.path.exists(app.config['UPLOAD_FOLDER']) else [],
        "output_folder": app.config['OUTPUT_FOLDER'],
        "upload_folder": app.config['UPLOAD_FOLDER']
    }
    return jsonify(debug_info)

@app.route('/test-csv')
def create_test_csv():
    """Create a test CSV file to verify download functionality"""
    try:
        import pandas as pd
        
        # Create sample data
        test_data = [
            {"Name": "John Doe", "Registration": "12345", "TotalMarks": 85, "SGPA": "8.5", "Grade": "A"},
            {"Name": "Jane Smith", "Registration": "12346", "TotalMarks": 92, "SGPA": "9.2", "Grade": "A+"},
            {"Name": "Bob Johnson", "Registration": "12347", "TotalMarks": 78, "SGPA": "7.8", "Grade": "B+"}
        ]
        
        df = pd.DataFrame(test_data)
        test_filename = "test_results.csv"
        test_path = os.path.join(app.config['OUTPUT_FOLDER'], test_filename)
        
        df.to_csv(test_path, index=False)
        
        return jsonify({
            "message": "Test CSV created successfully",
            "filename": test_filename,
            "download_url": f"/download/{test_filename}",
            "data": test_data
        })
    except Exception as e:
        return jsonify({"error": f"Failed to create test CSV: {str(e)}"}), 500

@app.route('/test-ai')
def test_ai_connection():
    """Test AI model connection"""
    try:
        model_endpoint = "http://localhost:11434/api/generate"
        test_prompt = """
You are an assistant that extracts student result details from text.
Extract the following fields only:
- Name
- Registration No
- Total Marks Obtained
- SGPA
- Grade

Return output as JSON ONLY in this format:
{
    "Name": "",
    "Registration": "",
    "TotalMarks": "",
    "SGPA": "",
    "Grade": ""
}

Text: Student Name: John Doe, Registration: 12345, Total Marks: 85, SGPA: 8.5, Grade: A
"""
        
        resp = requests.post(
            model_endpoint,
            json={"model": "llama3", "prompt": test_prompt, "stream": False},
            timeout=30
        )
        
        if resp.status_code == 200:
            result = resp.json()
            return jsonify({
                "status": "success",
                "ai_response": result.get("response", ""),
                "status_code": resp.status_code
            })
        else:
            return jsonify({
                "status": "error",
                "message": f"AI model returned status {resp.status_code}",
                "response": resp.text
            }), 500
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"AI connection failed: {str(e)}"
        }), 500

@app.route('/cleanup/<task_id>')
def cleanup_files(task_id):
    try:
        # Only clean up files if we have a completed status and confirmed download
        if task_id not in processing_status or processing_status[task_id].get('status') != 'completed':
            return jsonify({'error': 'Task not ready for cleanup'}), 400

        # Check download status
        if task_id not in download_status or download_status[task_id] != 'completed':
            return jsonify({'error': 'Download not confirmed, skipping cleanup'}), 400

        # Clean up uploaded file
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            if filename.startswith(task_id):
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                try:
                    os.remove(file_path)
                except OSError as e:
                    print(f"Error removing upload file: {e}")
        
        # Clean up output file
        output_file = processing_status[task_id].get('output_file')
        if output_file:
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_file)
            try:
                if os.path.exists(output_path):
                    os.remove(output_path)
            except OSError as e:
                print(f"Error removing output file: {e}")
        
        # Clean up status entries
        del processing_status[task_id]
        del download_status[task_id]
        
        return jsonify({'message': 'Files cleaned up successfully'})
    except Exception as e:
        print(f"Cleanup error: {str(e)}")
        return jsonify({'error': f'Cleanup failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
