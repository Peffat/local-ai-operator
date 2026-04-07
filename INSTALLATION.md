# 📦 Installation Guide

## Setting Up Local AI Operator

---

## 🎯 System Requirements

### 💻 Hardware

* RAM: 8GB minimum (16GB recommended)
* Storage: 10GB free space
* CPU: Any modern processor

### 🖥️ Software

* OS: Windows / macOS / Linux
* Python: 3.8+
* Internet: Only for initial setup

---

## 🚀 Quick Start (Recommended)

```bash
git clone https://github.com/Peffat/local-ai-operator
cd local-ai-operator

python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # macOS/Linux

pip install -r requirements.txt

ollama run gemma4:e2b

streamlit run app.py
```

---

## 📋 Detailed Steps

### 1. Clone the Repository

```bash
git clone https://github.com/Peffat/local-ai-operator
cd local-ai-operator
```

---

### 2. Setup Python Environment

#### Windows

```powershell
python -m venv venv
venv\Scripts\activate
```

#### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Install Ollama

Download:
👉 https://ollama.com

Verify:

```bash
ollama --version
```

---

### 5. Download Gemma 4 Model

```bash
ollama run gemma4:e2b
```

---

### 6. Run the App

```bash
streamlit run app.py
```

---

## 🧪 Test Installation

### Basic Chat

* Select: General Assistant
* Ask: “Hello”

### Excel Analysis

* Upload CSV / Excel
* Generate report

### Image Analysis

* Upload image
* Ask a question

---

## 🚨 Troubleshooting

### Ollama not found

* Reinstall Ollama
* Add it to PATH

---

### Model not found

```bash
ollama pull gemma4:e2b
```

---

### Streamlit not working

```bash
streamlit run app.py --server.port 8502
```

---

### Memory issues

* Close other apps
* Use `gemma4:e2b`
* Ensure 8GB+ RAM

---

## 🌐 Offline Verification

1. Disconnect internet
2. Run app
3. Test features

If everything works → ✅ fully offline

---

## 🔄 Updates

```bash
git pull
pip install -r requirements.txt --upgrade
ollama pull gemma4:e2b
```

---

## 🎉 Done

You now have a fully offline AI system running locally.

---
