# 📦 Installation Guide
## *Setting Up Local AI Operator - Step by Step*

<div align="center">

![Installation](https://img.shields.io/badge/Installation-Guide-blue?style=for-the-badge&logo=windows-terminal)
![Requirements](https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge&logo=python)
![Ollama](https://img.shields.io/badge/Ollama-Required-orange?style=for-the-badge&logo=docker)

*Complete setup in under 10 minutes*

[← Back to Project](PROJECT.md) • [Next: Usage Examples →](USAGE.md)

</div>

---

## 🎯 **System Requirements**

### 💻 **Hardware**
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 10GB free space
- **Processor**: Modern CPU (works on most laptops/desktops)

### 🖥️ **Software**
- **Operating System**: Windows 10/11, macOS, Linux
- **Python**: Version 3.8 or higher
- **Internet**: Required only for initial setup (then fully offline!)

---

## 🚀 **Quick Start (3 Steps)**

```bash
# Step 1: Clone and setup
git clone <your-repo-url>
cd local-ai-operator
python -m venv venv

# Step 2: Install dependencies
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Step 3: Start AI engine
ollama run gemma4

# Step 4: Launch application
streamlit run app.py
```

**🎉 You're done! Local AI Operator is now running offline.**

---

## 📋 **Detailed Installation Steps**

### **Step 1: Download the Project**

```bash
# Clone the repository
git clone https://github.com/yourusername/local-ai-operator.git
cd local-ai-operator
```

**Alternative**: Download ZIP from GitHub and extract.

---

### **Step 2: Python Environment Setup**

#### **Windows**
```powershell
# Create virtual environment
python -m venv venv

# Activate environment
venv\Scripts\activate

# Verify Python version
python --version  # Should show 3.8+
```

#### **macOS/Linux**
```bash
# Create virtual environment
python3 -m venv venv

# Activate environment
source venv/bin/activate

# Verify Python version
python --version  # Should show 3.8+
```

---

### **Step 3: Install Dependencies**

```bash
# Install all required packages
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed streamlit pandas python-docx PyPDF2 pillow pytesseract pdf2image requests openpyxl matplotlib reportlab seaborn numpy scipy
```

**Troubleshooting:**
- If installation fails, try: `pip install --upgrade pip`
- For Windows: Ensure you have Visual Studio Build Tools if compilation errors occur

---

### **Step 4: Install Ollama (AI Engine)**

#### **Download Ollama**
1. Visit: https://ollama.com
2. Download for your operating system
3. Install the application

#### **Verify Installation**
```bash
# Check if Ollama is installed
ollama --version
```

---

### **Step 5: Download Gemma 4 Model**

```bash
# Pull the Gemma 4 model (this may take a few minutes)
ollama run gemma4
```

**First run will:**
- Download the Gemma 4 model (~4-5GB)
- Set up the local AI engine
- May take 5-10 minutes depending on internet speed

**Alternative model:**
```bash
# For lighter weight (if needed)
ollama run gemma4:e2b
```

---

### **Step 6: Launch the Application**

```bash
# Make sure you're in the project directory
cd local-ai-operator

# Activate virtual environment (if not already)
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Start the application
streamlit run app.py
```

**Expected result:**
- Browser opens automatically
- Local AI Operator interface loads
- **🎉 You're now running AI completely offline!**

---

## 🔧 **Configuration Options**

### **Custom Ollama Settings**

Edit `app.py` to change the model:

```python
# Change this line for different models
MODEL = "gemma4"  # or "gemma4:e2b" for smaller version
```

### **Port Configuration**

```bash
# Run on custom port
streamlit run app.py --server.port 8502
```

---

## 🧪 **Testing Your Installation**

### **Test 1: Basic Chat**
1. Open the application
2. Select "General Assistant" mode
3. Type: "Hello, can you help me?"
4. Expected: AI responds with greeting

### **Test 2: Data Analysis**
1. Select "Smart Tools" → "Excel Analysis (PDF report)"
2. Upload any Excel/CSV file
3. Expected: AI generates analysis and PDF report

### **Test 3: Image Analysis**
1. Upload a clear photo (plant, injury, or scene)
2. Select appropriate mode (Health/Agriculture)
3. Expected: AI analyzes and provides insights

---

## 🚨 **Troubleshooting Guide**

### **"Command not found: ollama"**
```bash
# Windows: Add Ollama to PATH
# Or use full path: C:\Users\YourName\AppData\Local\Programs\Ollama\ollama.exe

# macOS/Linux: Check installation
which ollama
```

### **"Model not found" Error**
```bash
# Re-download the model
ollama pull gemma4

# List available models
ollama list
```

### **Streamlit won't start**
```bash
# Check Python path
python -c "import streamlit; print('OK')"

# Try different port
streamlit run app.py --server.port 8502
```

### **Import errors**
```bash
# Reinstall requirements
pip install -r requirements.txt --force-reinstall

# Check for missing dependencies
pip list | grep -E "(streamlit|pandas|reportlab)"
```

### **Memory issues**
- Close other applications
- Use `gemma4:e2b` instead of full `gemma4`
- Ensure 8GB+ RAM available

---

## 📱 **Mobile/Tablet Usage**

Local AI Operator works on:
- **Android devices** with Termux
- **iOS devices** with a-Shell
- **Tablets** via browser access

**Setup on mobile:**
1. Install Ollama mobile app (if available)
2. Use cloud-hosted version or
3. Access via local network from desktop

---

## 🔄 **Updating the System**

```bash
# Update Ollama
ollama pull gemma4  # Gets latest version

# Update dependencies
pip install -r requirements.txt --upgrade

# Update application
git pull origin main
```

---

## 🌐 **Offline Operation Verification**

Once set up, test complete offline functionality:

1. **Disconnect internet**
2. **Restart application**: `streamlit run app.py`
3. **Test all features**:
   - Chat conversations
   - File uploads and analysis
   - Report generation
   - Image processing

**✅ If everything works offline, you're fully set up!**

---

## 📞 **Support & Community**

### **Common Issues**
- **Slow first response**: Normal - model loading
- **Out of memory**: Use smaller model or more RAM
- **File upload fails**: Check file format compatibility

### **Performance Tips**
- **Close other apps** during AI processing
- **Use SSD storage** for faster model loading
- **Keep 16GB+ RAM** for best experience
- **Regular updates** for latest features

---

<div align="center">

## 🎉 **Installation Complete!**

**You're now equipped with a powerful AI assistant that works completely offline.**

*Ready to explore the capabilities?*

[← Back to Project](PROJECT.md) • [Next: Usage Examples →](USAGE.md)

---

*Built for the Gemma 4 Good Hackathon*

</div></content>
<parameter name="filePath">d:\My Local Projects\local-ai-operator\INSTALLATION.md