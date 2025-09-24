# PDF Result Extractor

A professional web application that extracts student result data from PDF documents using AI-powered text processing. The application provides a modern, user-friendly interface for uploading PDF files and downloading the extracted data as CSV files.

## Features

- 🧠 **AI-Powered Extraction**: Uses advanced AI models to accurately extract student information
- 📄 **PDF Processing**: Handles complex PDF layouts and formats
- 📊 **CSV Export**: Exports extracted data in a clean, structured CSV format
- 🎨 **Modern UI**: Professional, responsive design with drag-and-drop functionality
- ⚡ **Real-time Progress**: Live progress tracking during processing


## Why this project?
My professor once mentioned how tedious it was to create semester divisions—she had to manually enter each student’s details into Excel and then sort them. To simplify this process and save her time, I built this project.


## Extracted Data Fields

The application extracts the following information from student result PDFs:

- **Name**: Student's full name
- **Registration**: Registration number
- **Total Marks**: Total marks obtained
- **SGPA**: Semester Grade Point Average
- **Grade**: Overall grade

## Prerequisites

Before running the application, ensure you have:

1. **Python 3.8+** installed on your system
2. **AI Model Endpoint**: A running AI model server (e.g., Ollama with Llama3)
3. **Required Python packages** (install via requirements.txt)

## Installation

1. **Clone or download** this project to your local machine

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up AI Model** (if using Ollama):
   ```bash
   # Install Ollama (if not already installed)
   # Download and run Llama3 model
   ollama pull llama3
   ollama serve
   ```

## Usage

### Starting the Application

1. **Run the Flask application**:
   ```bash
   python app.py
   ```

2. **Open your web browser** and navigate to:
   ```
   http://localhost:5000
   ```

### Using the Web Interface

1. **Upload PDF**: 
   - Drag and drop your PDF file onto the upload area, or
   - Click the upload area to browse and select a file

2. **Configure Endpoint**:
   - Enter your AI model endpoint URL (default: `http://localhost:11434/api/generate`)
   - This should point to your running AI model server

3. **Process**:
   - Click "Extract Results" to start processing
   - Monitor the real-time progress bar
   - Wait for processing to complete

4. **Download Results**:
   - Once complete, click "Download CSV" to get your results
   - The CSV file will contain all extracted student data

### API Endpoints

The application also provides REST API endpoints:

- `POST /upload` - Upload and start processing a PDF file
- `GET /status/<task_id>` - Check processing status
- `GET /download/<filename>` - Download processed CSV file
- `GET /cleanup/<task_id>` - Clean up temporary files

## Configuration

### Model Endpoint

The application supports various AI model endpoints. Configure your endpoint URL in the web interface or modify the default in `app.py`:

```python
model_endpoint = "http://localhost:11434/api/generate"  # Ollama default
```

### File Limits

- **Maximum file size**: 16MB
- **Supported formats**: PDF only
- **Processing timeout**: Varies based on PDF size and complexity

## File Structure

```
webprojectAI/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/
│   └── index.html        # Web interface template
├── static/               # Static assets (CSS, JS, images)
├── uploads/              # Temporary uploaded files
└── outputs/              # Generated CSV files
```

## Troubleshooting

### Common Issues

1. **"Model endpoint not responding"**:
   - Ensure your AI model server is running
   - Check the endpoint URL is correct
   - Verify the model is loaded and accessible

2. **"File upload failed"**:
   - Check file size (must be under 16MB)
   - Ensure file is a valid PDF
   - Check available disk space

3. **"Processing stuck"**:
   - Large PDFs may take several minutes
   - Check server logs for errors
   - Try with a smaller PDF first

4. **"No data extracted"**:
   - Verify PDF contains student result data
   - Check if PDF text is selectable (not scanned image)
   - Try different AI model parameters

### Performance Tips

- **Smaller files process faster**: Consider splitting large PDFs
- **Good internet connection**: Required for AI model communication
- **Sufficient RAM**: Large PDFs require more memory
- **SSD storage**: Faster file I/O operations

## Development

### Running in Development Mode

```bash
# Enable debug mode
export FLASK_ENV=development
python app.py
```

### Customizing Extraction

To modify the extraction logic, edit the helper functions in `app.py`:

- `clean_total_marks()`: Clean and parse total marks
- `extract_father_mother_names()`: Extract parent names
- `select_final_name()`: Choose the best student name
- `merge_students()`: Merge duplicate entries

### Adding New Fields

To extract additional fields:

1. Update the AI prompt in `extract_with_improved()`
2. Modify the JSON parsing logic
3. Update the CSV export columns
4. Add validation in helper functions

## Security Considerations

- Files are processed locally and not stored permanently
- Automatic cleanup removes temporary files
- No sensitive data is logged or transmitted
- File uploads are validated for type and size

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or contributions:

1. Check the troubleshooting section above
2. Review the code comments for implementation details
3. Test with sample PDFs to verify functionality
4. Ensure all dependencies are properly installed

## Changelog

### Version 1.0.0
- Initial release
- PDF upload and processing
- AI-powered data extraction
- CSV export functionality
- Modern web interface
- Real-time progress tracking
