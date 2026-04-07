# 🎯 Usage Guide
## *Mastering Local AI Operator - Complete Tutorials*

<div align="center">

![Usage](https://img.shields.io/badge/Usage-Guide-green?style=for-the-badge&logo=book)
![Examples](https://img.shields.io/badge/Interactive-Examples-blue?style=for-the-badge&logo=lightbulb)
![Tutorials](https://img.shields.io/badge/Step-by-Step-orange?style=for-the-badge&logo=graduation-cap)

*From beginner to expert - unlock the full potential of offline AI*

[← Installation](INSTALLATION.md) • [Back to Project](PROJECT.md) • [Next: Architecture →](ARCHITECTURE.md)

</div>

---

## 🚀 **Getting Started**

### **First Launch**
1. **Start Ollama**: `ollama run gemma4`
2. **Launch App**: `streamlit run app.py`
3. **Select Mode**: Choose from sidebar (General, Health, Agriculture, Smart Tools)
4. **Start Chatting**: Type your first message!

---

## 💬 **Mode Selection Guide**

### 🎯 **General Assistant**
*Best for: Everyday questions, casual conversation, general advice*

**Use when:**
- Asking about current events (with offline knowledge cutoff)
- Getting explanations of concepts
- Casual conversation and brainstorming
- General problem-solving

**Example:**
```
User: "Explain how photosynthesis works"
AI: Provides detailed explanation with examples
```

---

### 🩺 **Health Assistant**
*Best for: Medical questions, injury assessment, health guidance*

**Features:**
- Injury analysis from photos
- First-aid recommendations
- Risk assessment
- When to seek professional help

**Example Conversation:**
```
User: Uploads photo of a cut
AI: "This appears to be a moderate laceration. Clean with soap and water, apply pressure for 10 minutes. Seek medical attention if bleeding doesn't stop."
```

---

### 🌾 **Agriculture Advisor**
*Best for: Plant care, crop management, farming advice*

**Capabilities:**
- Plant disease identification
- Nutrient deficiency detection
- Pest recognition
- Growth optimization tips

**Example:**
```
User: Uploads photo of yellowing leaves
AI: "Signs of nitrogen deficiency. Recommend balanced fertilizer application and soil testing."
```

---

### 🛠️ **Smart Tools Mode**
*Best for: Data analysis, document processing, specialized tasks*

**Available Tools:**
- Excel Analysis (PDF reports)
- Document/Image Analysis
- Auto AI (decides best approach)

---

## 📊 **Data Analysis Mastery**

### **Excel/CSV Analysis Workflow**

#### **Step 1: Upload Data**
```
📁 Upload → Select Excel/CSV file
📊 System detects → 566 records, 78 columns
✅ Auto-cleaning → Handles missing values
```

#### **Step 2: AI Analysis**
```
🤖 AI Processing → Advanced statistical analysis
📈 Chart Generation → 11 professional visualizations
🔍 Insight Discovery → Data-driven observations
```

#### **Step 3: Premium Report**
```
📄 PDF Generation → Executive summary + detailed analysis
📥 Download → Professional report with:
   ├── Executive Summary (key metrics & risks)
   ├── Data Quality Dashboard
   ├── Key Insights (actionable observations)
   ├── Visual Evidence (charts with captions)
   ├── Statistical Details
   └── Recommendations
```

### **Sample Analysis Output**

**Executive Summary:**
```
• Dataset: 566 records, high quality (98%)
• Key issue: 299 outliers detected across features
• Key insight: Performance metrics show variability
• Risk: Outliers may distort modeling
• Recommendation: Validate extreme values
```

**Generated Charts:**
- Distribution histograms
- Box plots (outlier detection)
- Correlation heatmaps
- Statistical summary charts

---

## 🖼️ **Image Analysis Tutorials**

### **Health Mode: Injury Assessment**

#### **Example 1: Cut Analysis**
```
Input: Photo of hand with deep cut
Process: AI analyzes wound characteristics
Output:
├── Severity: Moderate laceration
├── Immediate action: Clean and pressure
├── Risk factors: Infection potential
├── Professional care: Stitches may be needed
└── Prevention: Keep wound covered
```

#### **Example 2: Rash Evaluation**
```
Input: Photo of skin rash
Process: Pattern recognition and analysis
Output:
├── Likely cause: Allergic reaction
├── Treatment: Antihistamine, avoid irritants
├── Monitoring: Watch for spreading
├── When to see doctor: If worsens or with fever
```

### **Agriculture Mode: Plant Diagnosis**

#### **Example 1: Disease Detection**
```
Input: Photo of tomato plant with spots
Process: Symptom pattern matching
Output:
├── Diagnosis: Early blight fungus
├── Treatment: Copper fungicide spray
├── Prevention: Improve air circulation
├── Timeline: Treat within 48 hours
```

#### **Example 2: Nutrient Deficiency**
```
Input: Photo of yellowing corn leaves
Process: Color and pattern analysis
Output:
├── Issue: Nitrogen deficiency
├── Solution: Apply nitrogen-rich fertilizer
├── Timing: Immediate application needed
├── Monitoring: Reassess in 7-10 days
```

---

## 📄 **Document Processing**

### **PDF Analysis**
```
Upload PDF → AI extraction → Smart summarization
├── Content understanding
├── Key points identification
├── Structure recognition
└── Contextual insights
```

**Example:**
```
Input: Research paper PDF
Output: "This study examines climate change impacts on agriculture, finding 15-20% yield reductions in drought-prone areas. Key recommendations include drought-resistant crop varieties and improved irrigation systems."
```

### **Word Document Processing**
```
Upload DOCX → Text extraction → Analysis
├── Content summarization
├── Key information highlighting
├── Structure preservation
└── Insight generation
```

---

## 💡 **Advanced Usage Patterns**

### **Conversational Memory**
```
Turn 1: "I'm having chest pain"
AI: Asks clarifying questions, recommends monitoring

Turn 2: "It's sharp and comes and goes"
AI: Remembers previous context, provides more specific advice

Turn 3: "It's been 2 hours now"
AI: Escalates recommendation to seek immediate medical attention
```

### **Follow-up Analysis**
```
Initial: Upload Excel → Get basic insights
Follow-up: "Focus on outliers in column X"
AI: Provides deeper analysis of specific outliers

Follow-up: "Generate heatmap for correlations"
AI: Creates targeted correlation analysis
```

### **Multi-modal Combinations**
```
Text + Image: "What's wrong with this plant?" + photo
AI: Combines textual context with visual analysis

Data + Questions: Upload CSV + "Analyze sales trends"
AI: Provides data-driven insights with explanations
```

---

## 🎨 **Customization & Advanced Features**

### **Chart Type Selection**
```
Smart Tools → Excel Analysis → Chart Type dropdown
├── Auto (AI chooses best)
├── Histogram (distributions)
├── Boxplot (outliers)
└── Heatmap (correlations)
```

### **Mode Switching**
```
Start in General → Switch to Health for medical questions
Start in Agriculture → Switch to Smart Tools for data analysis
AI remembers context across mode switches
```

### **File Format Support**
```
✅ Excel (.xlsx, .xls)
✅ CSV (comma/tab separated)
✅ PDF (text-based documents)
✅ Images (.png, .jpg, .jpeg)
✅ Word (.docx)
```

---

## 🚨 **Best Practices & Tips**

### **Data Analysis**
- **Clean data first**: Let AI handle preprocessing
- **Ask specific questions**: "Focus on outliers" gives better results
- **Download reports**: Premium PDFs include all insights
- **Iterate**: Follow up with "explain this correlation" for deeper understanding

### **Image Analysis**
- **Clear photos**: Well-lit, focused images give better results
- **Context matters**: Add text description with uploads
- **Multiple angles**: Different views help with diagnosis
- **Recent photos**: Current state for accurate assessment

### **Conversational AI**
- **Be specific**: Detailed questions get better answers
- **Provide context**: Background information improves responses
- **Follow up**: Ask clarifying questions for deeper insights
- **Mode selection**: Choose appropriate assistant for best results

---

## 🔧 **Troubleshooting Common Issues**

### **Slow Responses**
```
Cause: Model loading or large files
Solution:
├── Wait for first response (normal)
├── Use smaller images/files
├── Close other applications
└── Consider gemma4:e2b for lighter weight
```

### **Analysis Errors**
```
Issue: File format problems
Fix:
├── Check file isn't corrupted
├── Ensure supported format
├── Try smaller file size
└── Verify data structure
```

### **Memory Issues**
```
Problem: Out of RAM during processing
Resolution:
├── Close other programs
├── Process smaller batches
├── Use gemma4:e2b model
└── Restart application
```

---

## 📈 **Power User Techniques**

### **Batch Processing**
```
Upload multiple related files
AI: "I see you have sales data, inventory, and customer info. Would you like me to analyze relationships between these datasets?"
```

### **Comparative Analysis**
```
Upload: "Compare these two crop photos"
AI: Identifies differences and provides comparative insights
```

### **Trend Analysis**
```
Data: "Show me sales trends over time"
AI: Generates time-series analysis with seasonality detection
```

### **Custom Insights**
```
Question: "What are the most important factors affecting crop yield?"
AI: Performs feature importance analysis and correlation studies
```

---

## 🎯 **Real-World Use Cases**

### **Student Research**
```
Scenario: Analyzing survey data for thesis
Process: Upload Excel → Get statistical insights → Download professional report
Result: Publication-ready analysis in minutes
```

### **Farmer Decision Making**
```
Scenario: Identifying plant health issues
Process: Photo upload → AI diagnosis → Treatment recommendations
Result: Faster response than waiting for agricultural extension
```

### **Healthcare Worker Support**
```
Scenario: Assessing injury severity in remote area
Process: Photo analysis → Triage guidance → Treatment plan
Result: Better patient outcomes with AI assistance
```

### **Small Business Intelligence**
```
Scenario: Analyzing sales data without expensive tools
Process: CSV upload → AI insights → Strategic recommendations
Result: Data-driven decisions on limited budget
```

---

## 🔄 **Workflow Optimization**

### **Efficient Data Analysis**
1. **Upload** → Quick scan of data structure
2. **Ask** → "What's the data quality like?"
3. **Focus** → "Analyze outliers in sales column"
4. **Deep-dive** → "Explain the correlation between X and Y"
5. **Report** → Download comprehensive PDF

### **Image Assessment Workflow**
1. **Capture** → Clear, well-lit photo
2. **Context** → Add descriptive text
3. **Upload** → Select appropriate mode
4. **Analysis** → Review AI assessment
5. **Follow-up** → Ask clarifying questions

---

## 🌟 **Pro Tips for Best Results**

### **Data Preparation**
- Remove unnecessary columns before upload
- Ensure consistent data formats
- Check for extreme outliers that might skew analysis

### **Question Formulation**
- Specific questions get better answers
- Include context: "As a farmer, how should I..."
- Ask follow-ups: "Can you explain that in simpler terms?"

### **Image Quality**
- Use good lighting and focus
- Include scale references when helpful
- Multiple angles for complex assessments

### **Report Customization**
- Use different chart types for various insights
- Ask for specific sections: "Focus on recommendations"
- Save reports for future reference

---

<div align="center">

## 🎉 **Master Local AI Operator**

**You've now learned to harness the full power of offline AI intelligence!**

*From simple questions to complex data analysis - you're equipped for anything.*

[← Installation](INSTALLATION.md) • [Back to Project](PROJECT.md) • [Next: Architecture →](ARCHITECTURE.md)

---

*Built for the Gemma 4 Good Hackathon - Digital Equity Track*

</div></content>
<parameter name="filePath">d:\My Local Projects\local-ai-operator\USAGE.md