"""
AI Sales Agent Squad - Gradio Application
AI agent system for generating and sending sales emails
"""

import os
import asyncio
from typing import Dict, List, Tuple
from datetime import datetime

import gradio as gr
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import (
    Agent, 
    Runner, 
    trace, 
    function_tool, 
    input_guardrail, 
    GuardrailFunctionOutput
)
from pydantic import BaseModel
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content

# Load environment variables
load_dotenv(override=True)

# ========== CONFIGURATION ==========
class Config:
    """Application centralized configuration"""
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
    MODEL = "gpt-4o-mini"
    
    # Configurable emails
    FROM_EMAIL = "testingavomo@gmail.com"
    TO_EMAIL = "contactola24podcast@gmail.com"

# ========== TOOLS ==========
@function_tool
def send_html_email(subject: str, html_body: str) -> Dict[str, str]:
    """Sends an HTML formatted email to sales prospects"""
    try:
        sg = sendgrid.SendGridAPIClient(api_key=Config.SENDGRID_API_KEY)
        from_email = Email(Config.FROM_EMAIL)
        to_email = To(Config.TO_EMAIL)
        content = Content("text/html", html_body)
        mail = Mail(from_email, to_email, subject, content).get()
        sg.client.mail.send.post(request_body=mail)
        return {"status": "success", "message": "Email sent successfully"}
    except Exception as e:
        return {"status": "error", "message": f"Error sending email: {str(e)}"}

# ========== GUARDRAILS ==========
class NameCheckOutput(BaseModel):
    """Output structure for name verification"""
    is_name_in_message: bool
    name: str = ""

guardrail_agent = Agent(
    name="Name Checker",
    instructions="Check if the user is including someone's personal name in their request. A personal name is a proper name of a real person.",
    output_type=NameCheckOutput,
    model=Config.MODEL
)

@input_guardrail
async def guardrail_against_name(ctx, agent, message):
    """Guardrail that blocks messages with personal names"""
    result = await Runner.run(guardrail_agent, message, context=ctx.context)
    is_name_in_message = result.final_output.is_name_in_message
    return GuardrailFunctionOutput(
        output_info={"found_name": result.final_output},
        tripwire_triggered=is_name_in_message
    )

# ========== SALES AGENTS ==========
class SalesAgentFactory:
    """Factory for creating sales agents with different personalities"""
    
    @staticmethod
    def create_agents(company_name: str) -> Tuple[Agent, Agent, Agent]:
        """Creates three sales agents with different personalities"""
        
        instructions_professional = f"""You are a sales agent working for {company_name}, 
        a startup that develops specialized AI agents for cybersecurity. 
        You write professional and formal cold sales emails."""
        
        instructions_funny = f"""You are a sales agent with a great sense of humor and captivating style working for {company_name}, 
        a startup that develops specialized AI agents for cybersecurity. 
        You write clever and engaging cold sales emails that have a high probability of getting responses."""
        
        instructions_busy = f"""You are a very busy sales agent working for {company_name}, 
        a startup that develops specialized AI agents for cybersecurity. 
        You write short and straight-to-the-point cold sales emails."""
        
        agent1 = Agent(name="Professional Agent", instructions=instructions_professional, model=Config.MODEL)
        agent2 = Agent(name="Funny Agent", instructions=instructions_funny, model=Config.MODEL)
        agent3 = Agent(name="Direct Agent", instructions=instructions_busy, model=Config.MODEL)
        
        return agent1, agent2, agent3

# ========== FORMATTING AGENTS ==========
def create_email_formatter_agents() -> Tuple[Agent, Agent]:
    """Creates specialized email formatting agents"""
    
    subject_instructions = """You are an expert in creating subject lines for cold sales emails. 
    Given a message, you must write a subject line that has a high probability of getting a response."""
    
    html_instructions = """You convert email body from plain text to HTML. 
    You receive an email body in plain text (which may include markdown) 
    and transform it into an HTML email body with a clear, simple and attractive design."""
    
    subject_writer = Agent(
        name="Subject Writer",
        instructions=subject_instructions,
        model=Config.MODEL
    )
    
    html_converter = Agent(
        name="HTML Converter",
        instructions=html_instructions,
        model=Config.MODEL
    )
    
    return subject_writer, html_converter

# ========== EMAIL MANAGER AGENT ==========
def create_email_manager() -> Agent:
    """Creates the agent that manages email formatting and sending"""
    
    instructions = """You are an email formatter and sender. You receive the body of an email that needs to be sent.
    
    Follow these steps:
    1. Use the 'subject_writer' tool to create the email subject
    2. Use the 'html_converter' tool to convert the body to HTML format
    3. Use the 'send_html_email' tool to send the email with the subject and HTML body
    """
    
    subject_writer, html_converter = create_email_formatter_agents()
    
    subject_tool = subject_writer.as_tool(
        tool_name="subject_writer",
        tool_description="Writes the subject for a cold sales email"
    )
    
    html_tool = html_converter.as_tool(
        tool_name="html_converter",
        tool_description="Converts email body to HTML format"
    )
    
    emailer_agent = Agent(
        name="Email Manager",
        instructions=instructions,
        handoff_description="Converts an email to HTML and sends it",
        model=Config.MODEL,
        tools=[subject_tool, html_tool, send_html_email]
    )
    
    return emailer_agent

# ========== MAIN AGENT ==========
def create_sales_manager(company_name: str, use_guardrails: bool = False) -> Agent:
    """Creates the main agent that coordinates the entire process"""
    
    agent1, agent2, agent3 = SalesAgentFactory.create_agents(company_name)
    
    tool1 = agent1.as_tool(tool_name="sales_agent_professional", tool_description="Writes a professional cold sales email")
    tool2 = agent2.as_tool(tool_name="sales_agent_funny", tool_description="Writes a funny cold sales email")
    tool3 = agent3.as_tool(tool_name="sales_agent_direct", tool_description="Writes a direct cold sales email")
    
    emailer_agent = create_email_manager()
    
    instructions = """You are the **Sales Manager**. Your goal is to find the best cold sales email using the sales agent tools.

Follow these steps carefully:

1. **Generate drafts:** Use the three sales agent tools to create three different email drafts. Do not continue until you have all three ready.

2. **Evaluate and select:** Review the drafts and choose the single email you consider most effective.
   You can use the tools multiple times if you are not satisfied with the initial results.

3. **Delegate for sending:** Deliver **ONLY** the winning email to the **"Email Manager"** agent. That agent will handle formatting and sending.

Crucial rules:
* You must use the **sales agent tools** to generate the drafts - **DO NOT** write them yourself.
* You must deliver **exactly ONE** email to the Email Manager - never more than one.
"""
    
    guardrails = [guardrail_against_name] if use_guardrails else []
    
    sales_manager = Agent(
        name="Sales Director",
        instructions=instructions,
        tools=[tool1, tool2, tool3],
        handoffs=[emailer_agent],
        model=Config.MODEL,
        input_guardrails=guardrails
    )
    
    return sales_manager

# ========== EXECUTION FUNCTIONS ==========
async def run_simple_agents(company_name: str, progress=gr.Progress()) -> Dict[str, str]:
    """Executes the three simple sales agents in parallel"""
    
    progress(0, desc="Initializing agents...")
    
    agent1, agent2, agent3 = SalesAgentFactory.create_agents(company_name)
    message = "Send a cold sales email"
    
    progress(0.3, desc="Generating emails...")
    
    with trace("SIMPLE_SALES_AGENTS"):
        results = await asyncio.gather(
            Runner.run(agent1, message),
            Runner.run(agent2, message),
            Runner.run(agent3, message),
        )
    
    progress(1.0, desc="Completed!")
    
    outputs = [result.final_output for result in results]
    
    return {
        "professional": outputs[0],
        "funny": outputs[1],
        "direct": outputs[2]
    }

async def run_orchestrated_agents(company_name: str, use_guardrails: bool, progress=gr.Progress()) -> Tuple[str, str]:
    """Executes the complete orchestrated system with the sales director"""
    
    progress(0, desc="Initializing sales director...")
    
    sales_manager = create_sales_manager(company_name, use_guardrails)
    message = "Send a cold sales email"
    
    progress(0.5, desc="Executing complete process...")
    
    try:
        trace_name = "ORCHESTRATED_WITH_GUARDRAILS" if use_guardrails else "ORCHESTRATED_NO_GUARDRAILS"
        with trace(trace_name):
            result = await Runner.run(sales_manager, message)
        
        progress(1.0, desc="Completed!")
        
        return result.final_output, "✅ Process completed successfully"
    
    except Exception as e:
        error_msg = str(e)
        if "Guardrail" in error_msg:
            return "", "🚫 Guardrail activated: Personal name detected in the message"
        return "", f"❌ Error: {error_msg}"

async def test_guardrails(company_name: str, test_message: str, progress=gr.Progress()) -> str:
    """Tests guardrails with a custom message"""
    
    progress(0, desc="Testing guardrails...")
    
    sales_manager = create_sales_manager(company_name, use_guardrails=True)
    
    progress(0.5, desc="Analyzing message...")
    
    try:
        with trace("GUARDRAIL_TEST"):
            result = await Runner.run(sales_manager, test_message)
        
        progress(1.0, desc="Completed!")
        return f"✅ Message approved. Result:\n\n{result.final_output}"
    
    except Exception as e:
        progress(1.0, desc="Blocked")
        error_msg = str(e)
        if "Guardrail" in error_msg:
            return "🚫 **GUARDRAIL ACTIVATED**\n\nPersonal name detected in the message. For security reasons, this request will not be processed."
        return f"❌ Error: {error_msg}"

# ========== GRADIO INTERFACE ==========
def create_interface():
    """Creates the Gradio interface"""
    
    with gr.Blocks(theme=gr.themes.Soft(), title="AI Sales Agent Squad") as demo:
        
        gr.Markdown("""
        # 🤖 AI Sales Agent Squad
        ### AI Agent System for Sales Emails
        
        Explore different types of AI agents working together to create and send professional sales emails.
        """)
        
        # Global configuration
        with gr.Row():
            company_name = gr.Textbox(
                label="🏢 Company Name",
                value="Avomo Innovations",
                placeholder="Enter your company name",
                scale=3
            )
        
        with gr.Tabs() as tabs:
            
            # TAB 1: Simple Agents
            with gr.Tab("📧 Simple Agents", id=0):
                gr.Markdown("""
                ### Three Agents with Different Personalities
                Each agent has a unique style for writing sales emails:
                - **Professional**: Formal and structured
                - **Funny**: Creative and captivating
                - **Direct**: Concise and to the point
                """)
                
                btn_simple = gr.Button("🚀 Generate Emails", variant="primary", size="lg")
                
                with gr.Row():
                    output_professional = gr.Textbox(
                        label="📝 Professional Agent",
                        lines=10,
                        placeholder="Professional email will appear here..."
                    )
                    output_funny = gr.Textbox(
                        label="😄 Funny Agent",
                        lines=10,
                        placeholder="Funny email will appear here..."
                    )
                    output_direct = gr.Textbox(
                        label="⚡ Direct Agent",
                        lines=10,
                        placeholder="Direct email will appear here..."
                    )
                
                async def handle_simple(company):
                    results = await run_simple_agents(company)
                    return results["professional"], results["funny"], results["direct"]
                
                btn_simple.click(
                    fn=handle_simple,
                    inputs=[company_name],
                    outputs=[output_professional, output_funny, output_direct]
                )
            
            # TAB 2: Orchestrated System
            with gr.Tab("🎯 Orchestrated System", id=1):
                gr.Markdown("""
                ### Sales Director with Handoff
                The Sales Director coordinates the entire process:
                1. Generates 3 drafts using simple agents
                2. Selects the best email
                3. Hands it off to the Email Manager
                4. The Manager formats and sends the email
                """)
                
                use_guardrails_check = gr.Checkbox(
                    label="🛡️ Activate Security Guardrails",
                    value=False,
                    info="Blocks messages with personal names"
                )
                
                btn_orchestrated = gr.Button("🎬 Execute Complete System", variant="primary", size="lg")
                
                output_orchestrated = gr.Textbox(
                    label="📬 Final Result",
                    lines=8,
                    placeholder="The result of the complete process will appear here..."
                )
                
                status_orchestrated = gr.Textbox(
                    label="📊 Status",
                    lines=2,
                    placeholder="Process status..."
                )
                
                btn_orchestrated.click(
                    fn=run_orchestrated_agents,
                    inputs=[company_name, use_guardrails_check],
                    outputs=[output_orchestrated, status_orchestrated]
                )
            
            # TAB 3: Guardrail Testing
            with gr.Tab("🛡️ Security Guardrails", id=2):
                gr.Markdown("""
                ### Protection System
                Guardrails verify messages before processing:
                - Detect personal names
                - Block inappropriate requests
                - Protect privacy
                
                **Test:** Try sending a message with a personal name (e.g., "Email for John Smith")
                """)
                
                test_message = gr.Textbox(
                    label="💬 Test Message",
                    placeholder="Write a message to test the guardrails...",
                    lines=3,
                    value="Send a cold sales email"
                )
                
                btn_test = gr.Button("🧪 Test Guardrails", variant="secondary", size="lg")
                
                output_test = gr.Textbox(
                    label="🔍 Test Result",
                    lines=8,
                    placeholder="The result will appear here..."
                )
                
                gr.Examples(
                    examples=[
                        ["Send a cold sales email"],
                        ["Write an email for John Smith"],
                        ["Email for the company CEO"],
                        ["Message addressed to Maria Garcia"]
                    ],
                    inputs=test_message,
                    label="📝 Message Examples"
                )
                
                btn_test.click(
                    fn=test_guardrails,
                    inputs=[company_name, test_message],
                    outputs=output_test
                )
        
        gr.Markdown("""
        ---
        ### 📚 Technical Information
        - **Framework**: OpenAI Agents SDK
        - **Model**: GPT-4o-mini
        - **Features**: Agents as Tools, Handoffs, Input Guardrails
        - **Tracing**: All executions are logged with OpenAI Traces
        """)
    
    return demo

# ========== EXECUTION ==========
if __name__ == "__main__":
    # Verify configuration
    if not Config.OPENAI_API_KEY:
        print("❌ ERROR: OPENAI_API_KEY not configured")
        exit(1)
    
    print("✅ Configuration verified")
    print(f"🔑 OpenAI API Key: {Config.OPENAI_API_KEY[:8]}...")
    
    # Create and launch interface
    demo = create_interface()
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        show_error=True
    )