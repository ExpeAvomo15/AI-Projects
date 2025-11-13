# app.py
#a¡Author: Expe Avomo - AI & ML Engineer
import gradio as gr
import asyncio
import time
from backend import analyze_company_data, get_available_companies

current_analysis = None

async def async_analyze_company(company_symbol, analysis_type):
    global current_analysis
    
    try:
        if not company_symbol.strip():
            return "❌ Please select a company", "Waiting for analysis..."
        
        result = await analyze_company_data(company_symbol, analysis_type)
        
        current_analysis = {
            "company": company_symbol,
            "analysis": result["analysis"],
            "metrics": result["metrics"],
            "recommendation": result["recommendation"],
            "timestamp": time.strftime("%H:%M:%S"),
            "success": result["success"]
        }
        
        system_info = f"""=== MARKETINTEL AI STATUS ===
🤖 Agent: MarketIntel AI
📊 Model: GPT-4o-mini 
🏢 Company: {company_symbol}
📈 Analysis: {analysis_type.replace('_', ' ').title()}

=== LAST ANALYSIS ===
⏰ Time: {current_analysis['timestamp']}
✅ Status: {'Analysis Complete' if current_analysis['success'] else 'Failed'}

=== FEATURES ===
💹 Alpha Vantage API
📊 Real-time Financial Data
📝 Markdown Formatting
🎯 Professional Reports

=== TRACES & MONITORING ===
🔍 Live Traces: https://platform.openai.com/logs?api=traces
📈 Observability: Full execution tracking
⚡ Performance: Real-time monitoring"""

        return current_analysis["analysis"], system_info
        
    except Exception as e:
        error_msg = f"❌ Analysis error: {str(e)}"
        return error_msg, "System temporarily unavailable"

def analyze_company(company_symbol, analysis_type):
    try:
        return asyncio.run(async_analyze_company(company_symbol, analysis_type))
    except Exception as e:
        return f"❌ Processing error: {str(e)}", "System error"

def get_system_status():
    companies = get_available_companies()
    
    status_lines = [
        "=== MARKETINTEL AI ===",
        "🤖 AI-Powered Financial Analysis",
        "",
        "=== AVAILABLE COMPANIES ==="
    ]
    
    for i, company in enumerate(companies, 1):
        status_lines.append(f"{i}. {company}")
    
    status_lines.extend([
        "",
        "=== ANALYSIS TYPES ===",
        "• Financial Health",
        "• Market Position", 
        "• Investment Potential",
        "• Competitive Analysis",
        "",
        "=== OBSERVABILITY ===",
        "✅ OpenAI Traces Active",
        "🔍 Monitor: platform.openai.com/logs",
        "📊 Full execution tracking",
        "⚡ Performance metrics",
        "",
        "=== TRACE LINK ===",
        "🌐 https://platform.openai.com/logs?api=traces"
    ])
    
    return "\n".join(status_lines)

def clear_analysis():
    global current_analysis
    current_analysis = None
    return "", get_system_status()

with gr.Blocks(
    title="MarketIntel AI - Financial Analysis Platform",
    theme=gr.themes.Soft(primary_hue="blue", secondary_hue="green"),
    css="""
    .container { max-width: 1000px; margin: 0 auto; }
    .analysis-box { 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 25px; 
        border-radius: 15px; 
        border-left: 5px solid #4CAF50;
    }
    .metrics-box { 
        background: #f8f9fa; 
        padding: 20px; 
        border-radius: 12px; 
        border: 2px solid #e9ecef;
    }
    .system-box { 
        background: #fff3cd; 
        padding: 20px; 
        border-radius: 12px; 
        border-left: 5px solid #ffc107;
        font-family: 'Monaco', monospace;
    }
    .header { 
        text-align: center; 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px;
        border-radius: 15px;
        margin-bottom: 25px;
    }
    .trace-box {
        background: #e8f4fd;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #2196F3;
        margin: 10px 0;
    }
    .markdown-content {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.6;
        padding: 20px;
    }
    .markdown-content h1, .markdown-content h2, .markdown-content h3 {
        color: #2c3e50;
        margin-top: 1.5em;
        margin-bottom: 0.5em;
    }
    .markdown-content ul {
        padding-left: 1.5em;
    }
    .markdown-content li {
        margin-bottom: 0.5em;
    }
    .markdown-content strong {
        color: #2c3e50;
    }
    """
) as demo:
    
    gr.HTML("""
    <div class="header">
        <h1>🚀 MarketIntel AI</h1>
        <h3>AI-Powered Financial Analysis Platform</h3>
        <p>Professional market analysis with real-time data, markdown reports, and full observability</p>
    </div>
    """)
    
    with gr.Row():
        with gr.Column(scale=2):
            with gr.Group():
                gr.HTML("<h3>🏢 Select Company for Analysis</h3>")
                company_symbol = gr.Dropdown(
                    label="Company Symbol",
                    choices=get_available_companies(),
                    value="AAPL",
                    info="Choose from major publicly traded companies"
                )
                
                analysis_type = gr.Radio(
                    label="Analysis Type",
                    choices=[
                        "financial_health",
                        "market_position", 
                        "investment_potential",
                        "competitive_analysis"
                    ],
                    value="financial_health",
                    info="Select the focus of your analysis"
                )
            
            with gr.Group(elem_classes="trace-box"):
                gr.HTML("""
                <h4>🔍 Observability & Tracing</h4>
                <p><strong>Live Traces:</strong> <a href="https://platform.openai.com/logs?api=traces" target="_blank">https://platform.openai.com/logs?api=traces</a></p>
                <p>Monitor agent execution, API calls, and performance metrics in real-time</p>
                """)
            
            with gr.Row():
                analyze_btn = gr.Button("📊 Analyze Company", variant="primary", size="lg")
                clear_btn = gr.Button("🔄 New Analysis", variant="secondary")
            
            analysis_output = gr.Markdown(
                label="🤖 AI Analysis Report",
                elem_classes="markdown-content",
                value="*Select a company and click **Analyze Company** to generate a professional financial report...*"
            )
            
            with gr.Group(elem_classes="metrics-box"):
                gr.HTML("<h3>📈 Key Financial Metrics</h3>")
                metrics_output = gr.Textbox(
                    label="Real-time Market Data",
                    value="Select a company and click analyze to view financial metrics...",
                    interactive=False,
                    lines=4
                )
        
        with gr.Column(scale=1):
            system_output = gr.Textbox(
                label="⚙️ System Dashboard",
                value=get_system_status(),
                interactive=False,
                lines=22,
                elem_classes="system-box"
            )
            
            with gr.Row():
                refresh_btn = gr.Button("🔄 Refresh Status", variant="secondary")
    
    gr.HTML("""
    <div style="margin-top: 30px; padding: 25px; background: #f8f9fa; border-radius: 15px;">
        <h2>💼 Professional Features</h2>
        
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-top: 20px;">
            <div style="padding: 20px; background: white; border-radius: 10px; border-left: 4px solid #4CAF50;">
                <h4>🔍 Alpha Vantage Data</h4>
                <p>Real-time financial data from professional market data API</p>
            </div>
            
            <div style="padding: 20px; background: white; border-radius: 10px; border-left: 4px solid #2196F3;">
                <h4>📝 Markdown Reports</h4>
                <p>Professional formatting with headers, sections, and emphasis</p>
            </div>
            
            <div style="padding: 20px; background: white; border-radius: 10px; border-left: 4px solid #FF9800;">
                <h4>🔗 Full Observability</h4>
                <p>OpenAI Traces for monitoring agent execution and performance</p>
            </div>
            
            <div style="padding: 20px; background: white; border-radius: 10px; border-left: 4px solid #9C27B0;">
                <h4>📊 Live Metrics</h4>
                <p>Current prices, market cap, P/E ratios, and fundamentals</p>
            </div>
        </div>
        
        <div style="margin-top: 25px; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px;">
            <h3>🎯 Observability & Monitoring</h3>
            <ul>
                <li><strong>Live Agent Traces:</strong> Real-time execution monitoring</li>
                <li><strong>Performance Metrics:</strong> Response times and token usage</li>
                <li><strong>API Call Tracking:</strong> Alpha Vantage and OpenAI calls</li>
                <li><strong>Error Monitoring:</strong> Full stack trace visibility</li>
                <li><strong>Dashboard:</strong> <a href="https://platform.openai.com/logs?api=traces" target="_blank" style="color: #ffeb3b;">platform.openai.com/logs</a></li>
            </ul>
        </div>
        
        <div style="margin-top: 20px; padding: 15px; background: #e8f4fd; border-radius: 10px; border-left: 4px solid #2196F3;">
            <h4>🔍 How to Use Traces:</h4>
            <ol>
                <li>Click the trace link above after running an analysis</li>
                <li>View agent execution steps and thinking process</li>
                <li>Monitor API performance and token usage</li>
                <li>Debug any issues with full visibility</li>
            </ol>
        </div>
    </div>
    """)
    
    def update_metrics():
        if current_analysis:
            metrics_text = "\n".join([f"• {k}: {v}" for k, v in current_analysis['metrics'].items()])
            return f"📊 Real-time Metrics\n{metrics_text}"
        return "Select a company and click analyze to view financial metrics..."
    
    analyze_btn.click(
        fn=analyze_company,
        inputs=[company_symbol, analysis_type],
        outputs=[analysis_output, system_output]
    ).then(
        fn=update_metrics,
        outputs=metrics_output
    )
    
    clear_btn.click(
        fn=clear_analysis,
        outputs=[analysis_output, system_output]
    ).then(
        fn=lambda: "Ready for new analysis. Select a company and click analyze.",
        outputs=metrics_output
    )
    
    refresh_btn.click(
        fn=get_system_status,
        outputs=system_output
    )

if __name__ == "__main__":
    print("🚀 Starting MarketIntel AI - With Observability")
    print("💼 Professional Financial Analysis Platform")
    print("📊 Real-time data from Alpha Vantage API")
    print("📝 Markdown formatting for professional reports")
    print("🔍 Observability: https://platform.openai.com/logs?api=traces")
    print("🌐 Dashboard: http://localhost:7860")
    
    demo.launch(
        server_name="localhost",
        server_port=7860,
        share=False,
        show_error=True
    )