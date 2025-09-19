
# Quick Start Guide

## 🚀 Get Started in 3 Steps

### 1. Setup Environment
**Option A: Automatic (Windows)**
```bash
start.bat
```

**Option B: Manual Setup**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Start the Application
```bash
python run.py
```

### 3. Open Your Browser
Go to: **http://localhost:5000**

## 📋 What You Need

- **Python 3.8+**
- **AI Model Server** (e.g., Ollama with Llama3)
- **PDF files** with student results

## 🎯 How to Use

1. **Upload PDF**: Drag & drop or click to select
2. **Set Endpoint**: Enter your AI model URL (default: `http://localhost:11434/api/generate`)
3. **Extract**: Click "Extract Results" and wait
4. **Download**: Get your CSV file when done

## 🔧 Troubleshooting

**Test your installation:**
```bash
python test_installation.py
```

**Common issues:**
- Make sure your AI model server is running
- Check that PDF files are under 16MB
- Ensure PDF text is selectable (not scanned images)

## 📁 Project Structure
```
webprojectAI/
├── app.py              # Main application
├── run.py              # Startup script
├── start.bat           # Windows batch file
├── test_installation.py # Test script
├── requirements.txt    # Dependencies
├── templates/          # Web interface
├── uploads/           # Temporary files
└── outputs/           # Generated CSVs
```

## 🆘 Need Help?

Check the full `README.md` for detailed documentation and troubleshooting tips.
