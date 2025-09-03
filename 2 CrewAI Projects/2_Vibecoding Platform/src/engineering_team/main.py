#!/usr/bin/env python
import sys
import warnings
import os
import json
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Try to import Streamlit
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    print("Streamlit not available. Running in console mode...")

# Add current directory to path to import crew
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from crew import EngineeringTeam
except ImportError:
    print("Error: Could not import EngineeringTeam from crew.py")
    print("Make sure crew.py is in the same folder as main.py")
    sys.exit(1)

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# Load environment variables from .env
load_dotenv()

# Initial configuration
os.makedirs('output', exist_ok=True)

# Configure OpenAI client
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    if STREAMLIT_AVAILABLE:
        st.error("❌ OPENAI_API_KEY not found in .env file")
    else:
        print("❌ OPENAI_API_KEY not found in .env file")
    sys.exit(1)

client = OpenAI(api_key=api_key)

def refine_requirements_with_ai(user_input):
    """Use OpenAI to refine user requirements"""
    prompt = f"""
    You are an expert software requirements analyst. A user has described what they want to build:
    
    "{user_input}"
    
    Transform this into clear, structured, and detailed technical requirements that can be understood 
    by an AI development team. The requirements should include:
    
    1. Main system functionalities
    2. Main entities and classes needed
    3. Necessary restrictions and validations
    4. Important technical considerations
    5. Suggested names for the main module and main class (Python format)
    
    Return ONLY the structured requirements text, without additional comments.
    The format should be clear and direct so CrewAI can process it efficiently.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert technical requirements analyst who turns ideas into precise technical specifications."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        error_msg = f"Error connecting to OpenAI: {e}"
        if STREAMLIT_AVAILABLE:
            st.error(error_msg)
        else:
            print(error_msg)
        return f"System based on: {user_input}"

def extract_module_info(requirements):
    """Extract module and class information from refined requirements"""
    module_name = "app_module.py"
    class_name = "MainClass"
    
    try:
        lines = requirements.split('\n')
        for line in lines:
            line_lower = line.lower()
            if 'module:' in line_lower:
                parts = line.split(':')
                if len(parts) > 1:
                    suggested_name = parts[1].strip()
                    if suggested_name:
                        module_name = suggested_name.replace(' ', '_') + '.py'
            elif 'class:' in line_lower:
                parts = line.split(':')
                if len(parts) > 1:
                    suggested_name = parts[1].strip()
                    if suggested_name:
                        class_name = suggested_name.replace(' ', '')
    except:
        pass
    
    return module_name, class_name

def run_crewai(requirements, module_name, class_name):
    """Run CrewAI with the provided requirements"""
    inputs = {
        'requirements': requirements,
        'module_name': module_name,
        'class_name': class_name
    }

    if STREAMLIT_AVAILABLE:
        with st.spinner("🚀 Running engineering team..."):
            result = EngineeringTeam().crew().kickoff(inputs=inputs)
    else:
        print("🚀 Running engineering team...")
        result = EngineeringTeam().crew().kickoff(inputs=inputs)
    
    return result

def console_mode():
    """Console mode when Streamlit is not available"""
    print("🚀 VibeCoding Platform - Console Mode")
    print("Describe the application you want to build (type 'exit' to quit):")
    
    while True:
        user_input = input("\nYour description: ").strip()
        if user_input.lower() in ['exit', 'quit']:
            break
        
        if not user_input:
            continue
        
        print("🧠 Analyzing and refining your requirements...")
        refined_requirements = refine_requirements_with_ai(user_input)
        
        print("\n✅ Refined requirements:")
        print(refined_requirements)
        
        module_name, class_name = extract_module_info(refined_requirements)
        print(f"\n📦 Module: {module_name}, Class: {class_name}")
        
        print("🚀 Executing CrewAI...")
        result = run_crewai(refined_requirements, module_name, class_name)
        
        print("🎉 Application created successfully!")
        print("📁 Files generated in 'output/' folder")
        print(f"  - output/{module_name} - Main module")
        print(f"  - output/app.py - Gradio interface")
        print(f"  - output/test_{module_name.replace('.py', '')}.py - Unit tests")
        print(f"  - output/{module_name.replace('.py', '')}_design.md - Technical design")
        
        print("\n" + "="*50)
        print("Want to create another application? (type 'exit' to quit)")

def main():
    if STREAMLIT_AVAILABLE:
        # Streamlit mode
        st.set_page_config(
            page_title="VibeCoding Platform",
            page_icon="🚀",
            layout="wide"
        )
        
        st.title("🚀 VibeCoding Platform")
        st.markdown("### Describe any application you want to build and our AI team will build it for you!")
        
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        if "crew_executed" not in st.session_state:
            st.session_state.crew_executed = False
        
        if "generated_files" not in st.session_state:
            st.session_state.generated_files = {}
        
        # Show message history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # User input
        if prompt := st.chat_input("Describe the application you want to create..."):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Process with OpenAI
            with st.chat_message("assistant"):
                with st.spinner("🧠 Analyzing and refining your requirements..."):
                    refined_requirements = refine_requirements_with_ai(prompt)
                
                st.markdown("✅ **Refined requirements:**")
                st.markdown(refined_requirements)
                
                # Extract module information
                module_name, class_name = extract_module_info(refined_requirements)
                
                # Add to messages
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": f"Refined requirements:\n\n{refined_requirements}\n\nModule: {module_name}, Class: {class_name}"
                })
                
                # Execute CrewAI
                result = run_crewai(refined_requirements, module_name, class_name)
                st.session_state.crew_executed = True
                
                # Save generated files information
                st.session_state.generated_files = {
                    'module_name': module_name,
                    'class_name': class_name,
                    'requirements': refined_requirements
                }
                
                st.success("🎉 Application created successfully!")
                st.markdown("**Generated files:**")
                st.markdown(f"- `output/{module_name}` - Main module")
                st.markdown(f"- `output/app.py` - Gradio interface")
                st.markdown(f"- `output/test_{module_name.replace('.py', '')}.py` - Unit tests")
                st.markdown(f"- `output/{module_name.replace('.py', '')}_design.md` - Technical design")
        
        # Show results if already executed
        if st.session_state.crew_executed:
            st.sidebar.title("📁 Generated Files")
            
            module_name = st.session_state.generated_files.get('module_name', 'app_module.py')
            base_name = module_name.replace('.py', '')
            
            # File selector in sidebar
            file_option = st.sidebar.selectbox(
                "Select file to view:",
                [module_name, "app.py", f"test_{base_name}.py", f"{base_name}_design.md"]
            )
            
            # Read and show selected file
            file_path = f"output/{file_option}"
            try:
                if os.path.exists(file_path):
                    with open(file_path, "r", encoding='utf-8') as f:
                        file_content = f.read()
                    
                    if file_option.endswith('.py'):
                        st.subheader(f"📦 {file_option}")
                        st.code(file_content, language="python")
                    elif file_option.endswith('.md'):
                        st.subheader(f"📋 {file_option}")
                        st.markdown(file_content)
                else:
                    st.warning(f"File {file_option} has not been generated yet.")
            
            except Exception as e:
                st.error(f"Error reading file {file_option}: {e}")
        
        # Additional information
        st.sidebar.title("ℹ️ Information")
        st.sidebar.info("""
        **How it works:**
        1. ✅ Describe your application in natural language
        2. 🧠 OpenAI refines the technical requirements
        3. 🚀 CrewAI generates the code automatically
        4. 📁 Get your application ready to use!
        
        **You can create:**
        - Any type of Python application
        - Management systems
        - Analysis tools
        - APIs and microservices
        - Whatever you can imagine!
        """)
        
        # Button to clear and start over
        if st.sidebar.button("🔄 Clear and start over"):
            st.session_state.messages = []
            st.session_state.crew_executed = False
            st.session_state.generated_files = {}
            st.rerun()
    else:
        # Console mode
        console_mode()

if __name__ == "__main__":
    main()