"""
AI Sanitizer - Demo Application
Professional tool for analyzing and sanitizing AI models
Author: AI Security Expert
"""

import gradio as gr
import json
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum
import random
from datetime import datetime
import tempfile
import os

# ============================
# Data Structures
# ============================

class RiskLevel(Enum):
    """Enum for risk level classification"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

@dataclass
class Vulnerability:
    """Data structure for vulnerability information"""
    name: str
    description: str
    risk_level: RiskLevel
    potential_impact: str
    detected: bool = True
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for display"""
        return {
            "Vulnerability": self.name,
            "Description": self.description,
            "Risk Level": self.risk_level.value,
            "Potential Impact": self.potential_impact
        }

@dataclass
class SanitizationResult:
    """Data structure for sanitization results"""
    vulnerability_name: str
    action_taken: str
    result: str
    new_risk_level: RiskLevel

# ============================
# Core Analysis Logic
# ============================

class AISanitizer:
    """Main class for AI model analysis and sanitization"""
    
    def __init__(self):
        self.vulnerabilities_db = self._initialize_vulnerabilities_db()
        
    def _initialize_vulnerabilities_db(self) -> List[Vulnerability]:
        """Initialize the database of known vulnerabilities"""
        return [
            Vulnerability(
                name="Prompt Injection",
                description="Model can be manipulated via carefully crafted inputs to bypass safety filters",
                risk_level=RiskLevel.HIGH,
                potential_impact="Unauthorized access, data extraction, malicious content generation"
            ),
            Vulnerability(
                name="Jailbreak Risk",
                description="Risk of circumventing ethical boundaries and safety mechanisms",
                risk_level=RiskLevel.HIGH,
                potential_impact="Generation of harmful, unethical, or dangerous content"
            ),
            Vulnerability(
                name="Data Leakage",
                description="Potential exposure of training data or sensitive information",
                risk_level=RiskLevel.MEDIUM,
                potential_impact="Privacy violations, data breaches, intellectual property theft"
            ),
            Vulnerability(
                name="Malware-in-Weights",
                description="Potential for malicious code embedded in model weights",
                risk_level=RiskLevel.MEDIUM,
                potential_impact="System compromise, backdoor access, data corruption"
            ),
            Vulnerability(
                name="Toxic Output / Bias",
                description="Model exhibits biased behavior or generates toxic content",
                risk_level=RiskLevel.MEDIUM,
                potential_impact="Discrimination, harm to users, reputational damage"
            ),
            Vulnerability(
                name="Overexposure",
                description="Model provides overly detailed responses that could be exploited",
                risk_level=RiskLevel.LOW,
                potential_impact="Information disclosure, social engineering attacks"
            )
        ]
    
    def analyze_model(self, model_input: str, source_type: str = "file") -> Tuple[List[Dict], str, float, str]:
        """
        Analyze an AI model for security vulnerabilities
        
        Args:
            model_input: Simulated model input (filename, HuggingFace ID, or model info)
            source_type: Type of model source ("file", "huggingface", "identifier")
            
        Returns:
            Tuple of (vulnerabilities list, markdown report, risk percentage, model name)
        """
        # Simulate download/loading based on source type
        model_name = self._simulate_model_loading(model_input, source_type)
        
        # Simulate analysis with some randomness for realism
        detected_vulns = []
        
        for vuln in self.vulnerabilities_db:
            # Simulate detection (90% detection rate for demo)
            if random.random() < 0.9:
                detected_vulns.append(vuln)
        
        # Calculate risk percentage
        risk_percentage = self._calculate_risk_percentage(detected_vulns)
        
        # Generate markdown report
        report = self._generate_analysis_report(detected_vulns, risk_percentage, model_name, source_type)
        
        # Convert to dict for display
        vuln_dicts = [v.to_dict() for v in detected_vulns]
        
        return vuln_dicts, report, risk_percentage, model_name
    
    def _simulate_model_loading(self, model_input: str, source_type: str) -> str:
        """Simulate model loading with progress updates"""
        if source_type == "huggingface":
            # Simulate HuggingFace model download
            return f"hf://{model_input}"
        elif source_type == "file":
            # Simulate file upload
            return f"local://{model_input}"
        else:
            # Just use the identifier
            return model_input
    
    def _calculate_risk_percentage(self, vulnerabilities: List[Vulnerability]) -> float:
        """Calculate overall risk percentage based on vulnerabilities"""
        if not vulnerabilities:
            return 0.0
        
        risk_weights = {
            RiskLevel.HIGH: 1.0,
            RiskLevel.MEDIUM: 0.6,
            RiskLevel.LOW: 0.3
        }
        
        total_risk = sum(risk_weights[v.risk_level] for v in vulnerabilities)
        max_risk = len(vulnerabilities) * risk_weights[RiskLevel.HIGH]
        
        return min(100.0, (total_risk / max_risk) * 100)
    
    def _generate_analysis_report(self, vulnerabilities: List[Vulnerability], 
                                 risk_percentage: float, model_name: str, 
                                 source_type: str) -> str:
        """Generate a professional markdown report"""
        source_display = "HuggingFace Model" if source_type == "huggingface" else "Local Model File" if source_type == "file" else "Model Identifier"
        
        report = f"""# AI Model Security Analysis Report

## 📋 Executive Summary
**Model Analyzed:** `{model_name}`  
**Source Type:** {source_display}  
**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Overall Risk Score:** **{risk_percentage:.1f}%**  
**Vulnerabilities Found:** {len(vulnerabilities)}

## 🔍 Detected Vulnerabilities
"""
        
        # Count vulnerabilities by risk level
        risk_counts = {level: 0 for level in RiskLevel}
        for vuln in vulnerabilities:
            risk_counts[vuln.risk_level] += 1
        
        report += f"""
### Risk Distribution
- 🔴 **High Risk:** {risk_counts[RiskLevel.HIGH]}
- 🟡 **Medium Risk:** {risk_counts[RiskLevel.MEDIUM]}
- 🟢 **Low Risk:** {risk_counts[RiskLevel.LOW]}

## 📊 Detailed Findings
"""
        
        for i, vuln in enumerate(vulnerabilities, 1):
            risk_emoji = "🔴" if vuln.risk_level == RiskLevel.HIGH else "🟡" if vuln.risk_level == RiskLevel.MEDIUM else "🟢"
            report += f"""
### {i}. {vuln.name} {risk_emoji}
**Risk Level:** {vuln.risk_level.value}  
**Description:** {vuln.description}  
**Potential Impact:** {vuln.potential_impact}
"""
        
        report += f"""
## 🎯 Recommendations
1. **Immediate Action Required** for High-Risk vulnerabilities
2. **Review and Patch** Medium-Risk issues within 7 days
3. **Monitor** Low-Risk vulnerabilities in next model update
4. **Implement** continuous security scanning in your ML pipeline

---
*Report generated by AI Sanitizer v1.0*  
*This is a simulated analysis for demonstration purposes*
"""
        
        return report
    
    def sanitize_model(self, vulnerabilities: List[Dict], model_name: str) -> Tuple[List[Dict], str, Dict, str]:
        """
        Simulate sanitization of detected vulnerabilities
        
        Args:
            vulnerabilities: List of detected vulnerabilities
            model_name: Name of the model being sanitized
            
        Returns:
            Tuple of (sanitization results, comparison report, cleaned model, sanitized_model_path)
        """
        sanitization_results = []
        sanitization_actions = {
            "Prompt Injection": "Implemented input validation layers and adversarial training",
            "Jailbreak Risk": "Enhanced safety classifiers and context-aware filtering",
            "Data Leakage": "Added differential privacy and output sanitization",
            "Malware-in-Weights": "Conducted integrity checks and weight scanning",
            "Toxic Output / Bias": "Applied debiasing techniques and content moderation",
            "Overexposure": "Implemented response length controls and sensitivity filters"
        }
        
        results_text = {
            "Prompt Injection": "Reduced success rate from 85% to 2%",
            "Jailbreak Risk": "Blocked 99% of known jailbreak attempts",
            "Data Leakage": "Prevented training data reconstruction attacks",
            "Malware-in-Weights": "Removed suspicious weight patterns",
            "Toxic Output / Bias": "Reduced biased outputs by 95%",
            "Overexposure": "Limited sensitive information disclosure"
        }
        
        for vuln in vulnerabilities:
            vuln_name = vuln["Vulnerability"]
            original_risk = RiskLevel(vuln["Risk Level"])
            
            # Reduce risk level (simulated improvement)
            new_risk = RiskLevel.LOW
            if original_risk == RiskLevel.HIGH:
                new_risk = RiskLevel.LOW if random.random() > 0.3 else RiskLevel.MEDIUM
            elif original_risk == RiskLevel.MEDIUM:
                new_risk = RiskLevel.LOW
            
            result = SanitizationResult(
                vulnerability_name=vuln_name,
                action_taken=sanitization_actions.get(vuln_name, "Standard security patch applied"),
                result=results_text.get(vuln_name, "Successfully mitigated"),
                new_risk_level=new_risk
            )
            
            sanitization_results.append(result)
        
        # Generate comparison report
        comparison_report = self._generate_comparison_report(vulnerabilities, sanitization_results, model_name)
        
        # Create cleaned model object
        cleaned_model = {
            "status": "sanitized",
            "security_score": 95.0 + random.uniform(0, 5),
            "compliance": ["ISO 27001", "GDPR", "ML Security Standard"],
            "version": f"2.{random.randint(0, 9)}.0-sanitized",
            "certification": "AI Security Certified",
            "model_name": model_name,
            "sanitization_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "vulnerabilities_fixed": len(vulnerabilities)
        }
        
        # Convert results to dict for display
        results_dict = [{
            "Vulnerability": r.vulnerability_name,
            "Action Taken": r.action_taken,
            "Result": r.result,
            "New Risk Level": r.new_risk_level.value
        } for r in sanitization_results]
        
        # Create a simulated sanitized model file
        sanitized_model_path = self._create_sanitized_model_file(cleaned_model, model_name)
        
        return results_dict, comparison_report, cleaned_model, sanitized_model_path
    
    def _create_sanitized_model_file(self, cleaned_model: Dict, model_name: str) -> str:
        """Create a simulated sanitized model file for download"""
        # Extract base name
        if "hf://" in model_name:
            base_name = model_name.replace("hf://", "").split("/")[-1]
        elif "local://" in model_name:
            base_name = model_name.replace("local://", "").split("/")[-1]
        else:
            base_name = model_name
        
        # Clean base name for filename
        base_name = "".join(c for c in base_name if c.isalnum() or c in ('_', '-', '.'))
        if not base_name:
            base_name = "sanitized_model"
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(
            mode='w', 
            suffix=f'_{base_name}_sanitized.json',
            delete=False,
            encoding='utf-8'
        )
        
        # Create file content
        file_content = {
            "model_info": cleaned_model,
            "sanitization_report": {
                "sanitization_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "security_certificate": "AI_SECURITY_CERTIFIED_V1.0",
                "compliance_standards": cleaned_model["compliance"],
                "validation_checks": [
                    "Prompt Injection Protection: PASSED",
                    "Jailbreak Resistance: PASSED",
                    "Data Privacy: PASSED",
                    "Bias Mitigation: PASSED",
                    "Security Audit: PASSED"
                ]
            },
            "metadata": {
                "generated_by": "AI Sanitizer v1.0",
                "copyright": "© 2024 Avomo Innovations LLC",
                "license": "For demonstration purposes only"
            }
        }
        
        # Write to file
        json.dump(file_content, temp_file, indent=2, ensure_ascii=False)
        temp_file.close()
        
        return temp_file.name
    
    def _generate_comparison_report(self, before: List[Dict], 
                                   after: List[SanitizationResult], 
                                   model_name: str) -> str:
        """Generate before/after comparison report"""
        report = f"""# 🛡️ Sanitization Results Report

## 📈 Security Improvement Summary
**Model:** `{model_name}`  
**Sanitization Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

| Vulnerability | Before | After | Improvement |
|---------------|--------|-------|-------------|
"""
        
        # Create mapping for easy lookup
        after_map = {r.vulnerability_name: r for r in after}
        
        for vuln in before:
            vuln_name = vuln["Vulnerability"]
            after_result = after_map.get(vuln_name)
            
            if after_result:
                improvement = "✅ Fixed" if after_result.new_risk_level == RiskLevel.LOW else "⚠️ Reduced"
                report += f"| {vuln_name} | {vuln['Risk Level']} | {after_result.new_risk_level.value} | {improvement} |\n"
        
        # Calculate statistics
        high_before = sum(1 for v in before if v["Risk Level"] == RiskLevel.HIGH.value)
        high_after = sum(1 for r in after if r.new_risk_level == RiskLevel.HIGH)
        
        medium_before = sum(1 for v in before if v["Risk Level"] == RiskLevel.MEDIUM.value)
        medium_after = sum(1 for r in after if r.new_risk_level == RiskLevel.MEDIUM)
        
        report += f"""
## 📊 Risk Reduction Statistics

### High Risk Vulnerabilities
- **Before:** {high_before} 🔴
- **After:** {high_after} 🔴
- **Reduction:** {(high_before - high_after)/max(high_before, 1)*100:.0f}%

### Medium Risk Vulnerabilities
- **Before:** {medium_before} 🟡
- **After:** {medium_after} 🟡
- **Reduction:** {(medium_before - medium_after)/max(medium_before, 1)*100:.0f}%

## 🎯 Sanitization Actions Applied

"""
        
        for result in after:
            emoji = "🛡️" if result.new_risk_level == RiskLevel.LOW else "⚠️"
            report += f"### {emoji} {result.vulnerability_name}\n"
            report += f"**Action:** {result.action_taken}\n"
            report += f"**Result:** {result.result}\n"
            report += f"**New Risk Level:** {result.new_risk_level.value}\n\n"
        
        report += """
## ✅ Final Model Status
- **Security Score:** 95+ (Excellent)
- **Compliance:** Multiple standards met
- **Ready for:** Production deployment
- **Recommendation:** Continuous monitoring enabled

### 📥 Download Sanitized Model
The sanitized model is now ready for download. Click the **"Download Sanitized Model"** button to get your secured AI model.

---
*Sanitization completed successfully*  
*Model is now production-ready with enhanced security*

---

**Copyright © 2024 Avomo Innovations LLC. All rights reserved.**  
*This software is provided for demonstration purposes only.*  
*Unauthorized copying, distribution, or use is strictly prohibited.*
"""
        
        return report

# ============================
# Gradio Interface
# ============================

def create_gradio_interface():
    """Create the Gradio interface for AI Sanitizer"""
    
    sanitizer = AISanitizer()
    
    # Define custom CSS as a string
    custom_css = """
    .gradio-container {
        max-width: 1200px !important;
        margin: 0 auto !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .title {
        text-align: center;
        padding: 25px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        margin-bottom: 25px;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
    }
    .title h1 {
        margin: 0;
        font-size: 2.5em;
        font-weight: 700;
    }
    .title p {
        margin: 10px 0 0 0;
        font-size: 1.1em;
        opacity: 0.95;
    }
    .section {
        background: white;
        padding: 22px;
        border-radius: 10px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.08);
        margin-bottom: 20px;
        border: 1px solid #eaeaea;
    }
    .section h3 {
        margin-top: 0;
        color: #2c3e50;
        border-bottom: 2px solid #667eea;
        padding-bottom: 10px;
    }
    .warning-box {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border-left: 5px solid #ffc107;
        padding: 18px;
        margin: 18px 0;
        border-radius: 6px;
        box-shadow: 0 2px 5px rgba(255, 193, 7, 0.1);
    }
    .success-box {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border-left: 5px solid #28a745;
        padding: 18px;
        margin: 18px 0;
        border-radius: 6px;
        box-shadow: 0 2px 5px rgba(40, 167, 69, 0.1);
    }
    .info-box {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        border-left: 5px solid #17a2b8;
        padding: 18px;
        margin: 18px 0;
        border-radius: 6px;
        box-shadow: 0 2px 5px rgba(23, 162, 184, 0.1);
    }
    .info-box ol {
        margin: 10px 0;
        padding-left: 20px;
    }
    .info-box li {
        margin: 8px 0;
        line-height: 1.5;
    }
    .tab-button {
        font-weight: 600 !important;
        padding: 12px 20px !important;
    }
    .gradio-button {
        font-weight: 600 !important;
        padding: 12px 24px !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
    }
    .gradio-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
    }
    .download-button {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        padding: 14px 28px !important;
        border-radius: 8px !important;
        border: none !important;
    }
    .download-button:hover {
        background: linear-gradient(135deg, #218838 0%, #1ea079 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3) !important;
    }
    .footer {
        text-align: center;
        margin-top: 35px;
        padding: 25px;
        color: #666;
        font-size: 0.9em;
        background: #f8f9fa;
        border-radius: 10px;
        border-top: 1px solid #eaeaea;
    }
    .footer hr {
        margin: 20px 0;
        border: none;
        border-top: 1px solid #ddd;
    }
    .json-display {
        max-height: 400px;
        overflow-y: auto !important;
        background: #f8f9fa !important;
        padding: 15px !important;
        border-radius: 8px !important;
        border: 1px solid #dee2e6 !important;
    }
    .markdown-display {
        max-height: 500px;
        overflow-y: auto !important;
        padding-right: 10px !important;
    }
    .model-source-tabs {
        margin-bottom: 20px !important;
    }
    .model-source-tabs .tab-nav {
        border-radius: 8px !important;
        background: #f8f9fa !important;
        padding: 5px !important;
    }
    .model-input-group {
        margin-bottom: 20px !important;
    }
    .examples-box {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        margin-top: 10px;
        border: 1px solid #eaeaea;
    }
    .examples-box h4 {
        margin-top: 0;
        color: #2c3e50;
    }
    .download-section {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
        border-left: 5px solid #28a745;
    }
    .download-section h3 {
        margin-top: 0;
        color: #155724;
    }
    """
    
    # Create Gradio interface sin el parámetro css
    with gr.Blocks() as demo:
        # Set title
        demo.title = "AI Sanitizer - Security Analysis Tool"
        
        # Inject custom CSS
        gr.HTML(f"<style>{custom_css}</style>")
        
        # Store state between callbacks
        state = gr.State({
            "current_vulnerabilities": [],
            "current_model": "",
            "analysis_report": "",
            "model_name": "",
            "source_type": "file",
            "sanitized_model_path": None
        })
        
        # Title Section
        gr.HTML("""
        <div class="title">
            <h1>🛡️ AI Sanitizer</h1>
            <p>Professional Security Analysis & Sanitization for AI Models</p>
            <p style="font-size: 0.95em; opacity: 0.9;">Detect and mitigate vulnerabilities in machine learning models</p>
        </div>
        """)
        
        # Main Layout
        with gr.Row():
            # Left Column - Input and Controls
            with gr.Column(scale=1):
                with gr.Group(elem_classes="section"):
                    gr.HTML('<h3>📤 Model Input</h3>')
                    
                    # Model source selection
                    source_type = gr.Radio(
                        choices=[
                            ("📁 Upload Model File", "file"),
                            ("🤗 HuggingFace Model", "huggingface"),
                            ("📝 Model Identifier", "identifier")
                        ],
                        value="file",
                        label="Select Model Source",
                        elem_classes="model-source-tabs"
                    )
                    
                    # Model input based on source type
                    model_input = gr.Textbox(
                        label="Model File or Identifier",
                        placeholder="Enter model name, HuggingFace ID, or upload a file",
                        value="my_ai_model.pkl",
                        lines=2
                    )
                    
                    # File upload component
                    file_upload = gr.File(
                        label="Upload Model File",
                        file_types=[".pkl", ".pt", ".h5", ".onnx", ".safetensors"],
                        visible=True
                    )
                    
                    # HuggingFace examples
                    with gr.Group(elem_classes="examples-box", visible=False) as hf_examples:
                        gr.HTML("""
                        <h4>🤗 HuggingFace Examples:</h4>
                        <ul style="margin: 5px 0; padding-left: 20px;">
                            <li><code>bert-base-uncased</code></li>
                            <li><code>gpt2</code></li>
                            <li><code>distilbert-base-uncased</code></li>
                            <li><code>microsoft/codebert-base</code></li>
                        </ul>
                        """)
                    
                    # Update visibility based on source type
                    def update_input_visibility(source_type):
                        if source_type == "file":
                            return gr.update(visible=True), gr.update(visible=False), gr.update(label="Model File Path", placeholder="Enter model file path or upload")
                        elif source_type == "huggingface":
                            return gr.update(visible=False), gr.update(visible=True), gr.update(label="HuggingFace Model ID", placeholder="Enter HuggingFace model ID (e.g., bert-base-uncased)")
                        else:
                            return gr.update(visible=False), gr.update(visible=False), gr.update(label="Model Identifier", placeholder="Enter model name or identifier")
                    
                    source_type.change(
                        fn=update_input_visibility,
                        inputs=[source_type],
                        outputs=[file_upload, hf_examples, model_input]
                    )
                    
                    with gr.Row():
                        analyze_btn = gr.Button(
                            "🔍 Analyze Model", 
                            variant="primary",
                            scale=2
                        )
                        sanitize_btn = gr.Button(
                            "🛡️ Sanitize Model", 
                            variant="secondary",
                            scale=2
                        )
                    
                    with gr.Group(elem_classes="info-box"):
                        gr.HTML("""
                        <p style="font-weight: bold; margin-bottom: 15px;">📖 How to use:</p>
                        <ol>
                            <li>Select model source (Upload, HuggingFace, or Identifier)</li>
                            <li>Provide model information based on selected source</li>
                            <li>Click <strong>Analyze Model</strong> to detect vulnerabilities</li>
                            <li>Review the security report in the tabs</li>
                            <li>Click <strong>Sanitize Model</strong> to apply fixes</li>
                            <li>Download the sanitized model using the download button</li>
                        </ol>
                        """)
                    
                    risk_gauge = gr.HTML(label="Risk Assessment")
            
            # Right Column - Output and Reports
            with gr.Column(scale=2):
                # Tabs for different outputs
                with gr.Tabs():
                    with gr.TabItem("📋 Analysis Results"):
                        vulnerabilities_display = gr.JSON(
                            label="Detected Vulnerabilities",
                            elem_classes="json-display"
                        )
                    
                    with gr.TabItem("📄 Detailed Report"):
                        analysis_report = gr.Markdown(
                            label="Security Analysis Report",
                            elem_classes="markdown-display"
                        )
                    
                    with gr.TabItem("🔄 Sanitization Results"):
                        sanitization_results = gr.JSON(
                            label="Sanitization Actions",
                            elem_classes="json-display"
                        )
                    
                    with gr.TabItem("📊 Comparison Report"):
                        comparison_report = gr.Markdown(
                            label="Before/After Comparison",
                            elem_classes="markdown-display"
                        )
                    
                    with gr.TabItem("✅ Cleaned Model"):
                        cleaned_model_display = gr.JSON(
                            label="Sanitized Model Output",
                            elem_classes="json-display"
                        )
                        
                        # Download button section
                        download_section = gr.Group(elem_classes="download-section", visible=False)
                        with download_section:
                            gr.HTML('<h3>📥 Download Sanitized Model</h3>')
                            gr.HTML('<p>Your model has been successfully sanitized and is ready for download.</p>')
                            download_btn = gr.Button(
                                "⬇️ Download Sanitized Model",
                                variant="primary",
                                elem_classes="download-button"
                            )
                            download_file = gr.File(
                                label="Sanitized Model File",
                                visible=False
                            )
        
        # Footer
        gr.HTML("""
        <div class="footer">
            <hr>
            <p style="margin-bottom: 8px;"><strong>AI Sanitizer v1.0</strong> | For demonstration purposes only</p>
            <p style="font-size: 0.85em; opacity: 0.8; margin-bottom: 15px;">
                This tool simulates AI model security analysis. Real-world implementation requires additional security measures.
            </p>
            <p style="font-size: 0.8em; color: #888; border-top: 1px solid #eee; padding-top: 15px;">
                <strong>Copyright © 2024 Avomo Innovations LLC. All rights reserved.</strong><br>
                This software is provided for demonstration purposes only.<br>
                Unauthorized copying, distribution, or use is strictly prohibited.
            </p>
        </div>
        """)
        
        # Callback functions
        def analyze_model_callback(model_input: str, source_type: str, app_state: Dict) -> Tuple:
            """Callback for Analyze Model button"""
            if not model_input.strip():
                model_input = "demo_model_v1.2.3.pkl"
            
            # Perform analysis
            vulnerabilities, report, risk_percentage, model_name = sanitizer.analyze_model(
                model_input, source_type
            )
            
            # Update state
            app_state.update({
                "current_vulnerabilities": vulnerabilities,
                "current_model": model_input,
                "analysis_report": report,
                "risk_percentage": risk_percentage,
                "model_name": model_name,
                "source_type": source_type,
                "sanitized_model_path": None  # Reset download path
            })
            
            # Format vulnerabilities for display
            vuln_display = json.dumps(vulnerabilities, indent=2)
            
            # Create risk gauge visualization
            risk_color = "red" if risk_percentage > 70 else "orange" if risk_percentage > 40 else "green"
            gauge_html = f"""
            <div style="text-align: center; padding: 20px; background: #f5f5f5; border-radius: 10px; margin: 20px 0;">
                <h3 style="margin-bottom: 10px;">Overall Risk Score</h3>
                <div style="width: 200px; height: 200px; margin: 0 auto; border-radius: 50%; 
                            background: conic-gradient({risk_color} 0% {risk_percentage}%, #e0e0e0 {risk_percentage}% 100%);
                            display: flex; align-items: center; justify-content: center; position: relative;">
                    <div style="background: white; width: 150px; height: 150px; border-radius: 50%; 
                                display: flex; align-items: center; justify-content: center;">
                        <span style="font-size: 2em; font-weight: bold; color: {risk_color};">{risk_percentage:.1f}%</span>
                    </div>
                </div>
                <p style="margin-top: 10px;">{len(vulnerabilities)} vulnerabilities detected</p>
                <p style="font-size: 0.9em; color: #666;">Model: {model_name}</p>
            </div>
            """
            
            # Hide download section after new analysis
            return vuln_display, report, gauge_html, app_state, gr.update(visible=False)
        
        def sanitize_model_callback(app_state: Dict) -> Tuple:
            """Callback for Sanitize Model button"""
            if not app_state.get("current_vulnerabilities"):
                return "No vulnerabilities to sanitize. Please analyze a model first.", "", {}, app_state, gr.update(visible=False)
            
            # Perform sanitization
            results, comparison_report, cleaned_model, sanitized_model_path = sanitizer.sanitize_model(
                app_state["current_vulnerabilities"],
                app_state["model_name"]
            )
            
            # Update state with sanitized model path
            app_state["sanitized_model_path"] = sanitized_model_path
            
            # Format results for display
            results_display = json.dumps(results, indent=2)
            model_display = json.dumps(cleaned_model, indent=2)
            
            # Show download section
            return results_display, comparison_report, model_display, app_state, gr.update(visible=True)
        
        def download_model_callback(app_state: Dict) -> Dict:
            """Callback for Download Model button"""
            if not app_state.get("sanitized_model_path"):
                return gr.update(value=None, visible=False)
            
            # Return the file for download
            return gr.update(value=app_state["sanitized_model_path"], visible=True)
        
        # Set up callbacks
        analyze_btn.click(
            fn=analyze_model_callback,
            inputs=[model_input, source_type, state],
            outputs=[vulnerabilities_display, analysis_report, risk_gauge, state, download_section]
        )
        
        sanitize_btn.click(
            fn=sanitize_model_callback,
            inputs=[state],
            outputs=[sanitization_results, comparison_report, cleaned_model_display, state, download_section]
        )
        
        # Download button callback
        download_btn.click(
            fn=download_model_callback,
            inputs=[state],
            outputs=[download_file]
        )
        
        # Update model input when file is uploaded
        def update_model_input_from_file(file):
            if file:
                return file.name
            return "my_ai_model.pkl"
        
        file_upload.change(
            fn=update_model_input_from_file,
            inputs=[file_upload],
            outputs=[model_input]
        )
    
    return demo

# ============================
# Main Application
# ============================

def main():
    """Main application entry point"""
    print("🚀 Starting AI Sanitizer Demo...")
    print("📊 Open the browser at the provided local URL to access the interface")
    print("🔒 This is a simulated security analysis tool for demonstration purposes")
    
    # Create and launch the interface
    demo = create_gradio_interface()
    
    # Usar localhost en lugar de 0.0.0.0
    demo.launch(
        server_name="localhost",
        server_port=7860,
        share=False,
        quiet=False,
        show_error=True,
        inbrowser=False
    )

if __name__ == "__main__":
    main()