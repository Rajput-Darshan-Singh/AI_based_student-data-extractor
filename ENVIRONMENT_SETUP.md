# Environment Setup Guide

This guide will help you set up a proper Python virtual environment for the PDF Result Extractor project.

## 🎯 Why Use Virtual Environment?

- **Isolation**: Keeps project dependencies separate from system Python
- **Reproducibility**: Ensures consistent environment across different machines
- **Clean Management**: Easy to install, update, and remove packages
- **No Conflicts**: Prevents version conflicts between different projects

## 🚀 Quick Setup (Recommended)

### Option 1: Automatic Setup (Windows)
Simply double-click `start.bat` - it will handle everything automatically!

### Option 2: Manual Setup

#### Step 1: Create Virtual Environment
```bash
# Navigate to project directory
cd D:\project\webprojectAI

# Create virtual environment
python -m venv venv
```

#### Step 2: Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

#### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 4: Start Application
```bash
python run.py
```

## 🔧 Detailed Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (usually comes with Python)

### Step-by-Step Process

1. **Open Command Prompt/Terminal**
   - Windows: Press `Win + R`, type `cmd`, press Enter
   - Navigate to your project directory: `cd D:\project\webprojectAI`

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   ```
   This creates a new folder called `venv` with a clean Python environment.

3. **Activate Virtual Environment**
   
   **Windows:**
   ```bash
   venv\Scripts\activate
   ```
   
   **Linux/Mac:**
   ```bash
   source venv/bin/activate
   ```
   
   You should see `(venv)` at the beginning of your command prompt.

4. **Upgrade pip (Optional but Recommended)**
   ```bash
   python -m pip install --upgrade pip
   ```

5. **Install Project Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

6. **Verify Installation**
   ```bash
   python test_installation.py
   ```

7. **Start the Application**
   ```bash
   python run.py
   ```

## 📋 What Gets Installed

The following packages will be installed in your virtual environment:

- **Flask 3.1.2**: Web framework for the application
- **PyMuPDF 1.26.4**: PDF processing library
- **requests 2.32.5**: HTTP library for API calls
- **pandas 2.3.2**: Data manipulation and CSV export
- **word2number 1.1**: Convert words to numbers
- **Werkzeug 3.1.3**: WSGI toolkit (Flask dependency)

## 🛠️ Troubleshooting

### Common Issues

#### 1. "python is not recognized"
- **Solution**: Install Python from [python.org](https://python.org)
- Make sure to check "Add Python to PATH" during installation

#### 2. "Permission denied" on Windows
- **Solution**: Run Command Prompt as Administrator
- Or use PowerShell instead of Command Prompt

#### 3. PyMuPDF installation fails
- **Solution**: The batch file uses pre-compiled wheels to avoid this issue
- If manual installation fails, try: `pip install --only-binary=all PyMuPDF`

#### 4. Virtual environment not activating
- **Solution**: Make sure you're in the correct directory
- Check that the `venv` folder exists
- Try using the full path: `D:\project\webprojectAI\venv\Scripts\activate`

### Verification Commands

Check if virtual environment is active:
```bash
# Should show the path to your venv
echo %VIRTUAL_ENV%
```

Check installed packages:
```bash
pip list
```

Test the application:
```bash
python test_installation.py
```

## 🔄 Daily Usage

### Starting the Application
1. Open Command Prompt/Terminal
2. Navigate to project: `cd D:\project\webprojectAI`
3. Activate environment: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Linux/Mac)
4. Start app: `python run.py`

### Stopping the Application
- Press `Ctrl + C` in the terminal
- Or close the terminal window

### Deactivating Virtual Environment
```bash
deactivate
```

## 📁 Project Structure with Virtual Environment

```
webprojectAI/
├── venv/                    # Virtual environment (don't edit)
│   ├── Scripts/            # Windows activation scripts
│   ├── Lib/                # Python packages
│   └── pyvenv.cfg          # Environment configuration
├── app.py                  # Main application
├── run.py                  # Startup script
├── start.bat              # Windows batch file
├── requirements.txt       # Dependencies list
├── templates/             # Web interface
├── uploads/               # Temporary files
└── outputs/               # Generated CSVs
```

## 💡 Best Practices

1. **Always activate virtual environment** before working on the project
2. **Never commit the venv folder** to version control
3. **Update requirements.txt** when adding new packages: `pip freeze > requirements.txt`
4. **Use the batch file** for easy startup on Windows
5. **Test installation** regularly with `python test_installation.py`

## 🆘 Getting Help

If you encounter issues:

1. **Check the troubleshooting section** above
2. **Run the test script**: `python test_installation.py`
3. **Verify Python version**: `python --version`
4. **Check virtual environment**: `echo %VIRTUAL_ENV%`
5. **Review error messages** carefully for specific guidance

## 🔄 Updating Dependencies

To update all packages to their latest versions:
```bash
# Activate virtual environment first
venv\Scripts\activate

# Update pip
python -m pip install --upgrade pip

# Update all packages
pip install --upgrade -r requirements.txt

# Update requirements.txt with new versions
pip freeze > requirements.txt
```

## 🗑️ Cleanup

To remove the virtual environment and start fresh:
```bash
# Deactivate first
deactivate

# Remove the venv folder
rmdir /s venv  # Windows
rm -rf venv    # Linux/Mac

# Then follow setup steps again
```

This ensures you have a clean, isolated environment for your PDF Result Extractor project!
