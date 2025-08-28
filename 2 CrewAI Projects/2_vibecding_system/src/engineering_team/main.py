import gradio as gr
import openai
from typing import Dict, Any
import json
import re
from enum import Enum
import time
import os
from dotenv import load_dotenv
from pathlib import Path
import concurrent.futures
import sys

# ==================== CONFIGURATION ====================
def load_env():
    """Load environment variables from .env in agents folder"""
    env_path = Path(__file__).parent.parent.parent.parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print("✓ .env loaded")
        return True
    print("⚠️  .env not found, using system variables")
    return False

load_env()
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("❌ OPENAI_API_KEY not found")

os.environ["OPENAI_API_KEY"] = API_KEY

# ==================== CLASSES ====================
class CrewStatus(Enum):
    ANALYZING = "Analyzing with AI"
    CREW_WORKING = "Executing CrewAI"
    COMPLETED = "Completed"
    ERROR = "Error"

class FeatureExtractor:
    def __init__(self):
        self.client = openai.OpenAI(api_key=API_KEY)
        
    def extract_features(self, description: str) -> Dict[str, Any]:
        prompt = f"""
        Analyze this description and return JSON with:
        - main_objective
        - main_features (list)
        - recommended_technologies (list) 
        - key_requirements
        - module_name (without .py)
        - class_name
        
        Description: {description}
        Respond only with valid JSON.
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        
        ai_response = response.choices[0].message.content
        json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
        
        if json_match:
            try:
                data = json.loads(json_match.group())
                # Default values if missing
                data.setdefault('module_name', 'app_module')
                data.setdefault('class_name', 'AppClass')
                data.setdefault('key_requirements', description)
                return data
            except json.JSONDecodeError:
                pass
                
        # Fallback if JSON parsing fails
        return {
            'key_requirements': description,
            'module_name': 'app_module', 
            'class_name': 'AppClass'
        }

class CrewManager:
    def __init__(self):
        self.extractor = FeatureExtractor()
        self.status = CrewStatus.ANALYZING
        self.progress = 0
        
    def execute_crew(self, user_input: str) -> str:
        try:
            # Phase 1: AI Analysis
            self.update_status(CrewStatus.ANALYZING, 33)
            structured_data = self.extractor.extract_features(user_input)
            
            # Phase 2: Execute CrewAI
            self.update_status(CrewStatus.CREW_WORKING, 66)
            result = self.run_crewai(structured_data)
            
            # Phase 3: Completed
            self.update_status(CrewStatus.COMPLETED, 100)
            return result
            
        except Exception as e:
            self.update_status(CrewStatus.ERROR, 0)
            return f"Error: {str(e)}"
    
    def run_crewai(self, data: dict) -> str:
        """Execute CrewAI with structured data"""
        try:
            # Add current directory to path to import crew.py
            current_dir = Path(__file__).parent
            if str(current_dir) not in sys.path:
                sys.path.insert(0, str(current_dir))
            
            from crew import EngineeringTeam
            from crewai import Crew
            
            crew = EngineeringTeam().crew()
            inputs = {
                'requirements': data['key_requirements'],
                'module_name': data['module_name'],
                'class_name': data['class_name']
            }
            
            result = crew.kickoff(inputs=inputs)
            return f"✅ Project generated successfully!\n\n{result}"
            
        except ImportError:
            return "❌ Error: Could not import EngineeringTeam"
        except Exception as e:
            return f"❌ Error in CrewAI: {str(e)}"
    
    def update_status(self, status: CrewStatus, progress: int):
        self.status = status
        self.progress = progress
        print(f"Status: {status.value} - Progress: {progress}%")

# ==================== INTERFACE ====================
def create_interface():
    manager = CrewManager()
    
    def process_input(user_input: str):
        if not user_input.strip():
            return "❌ Please enter a description", 0, CrewStatus.ERROR.value
        
        def execute():
            return manager.execute_crew(user_input)
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(execute)
            
            while not future.done():
                yield "", manager.progress, manager.status.value
                time.sleep(0.1)
            
            result = future.result()
            yield result, manager.progress, manager.status.value
    
    with gr.Blocks(title="Vibecoding CrewAI", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 🚀 Project Generator with CrewAI")
        
        user_input = gr.Textbox(
            label="Project Description",
            placeholder="Describe the application you want to create...",
            lines=4
        )
        
        submit_btn = gr.Button("Generate Project", variant="primary")
        
        progress_bar = gr.Slider(
            minimum=0, maximum=100, value=0,
            label="Progress", interactive=False
        )
        
        status_text = gr.Textbox(
            label="Status", value=CrewStatus.ANALYZING.value,
            interactive=False
        )
        
        output_result = gr.Textbox(
            label="Result", lines=10,
            interactive=False
        )
        
        # Installation info
        gr.Markdown("""
        ### 💡 Requirements:
        ```bash
        pip install crewai langchain openai python-dotenv
        ```
        
        ### 📁 Generated structure:
        - `output/{module_name}.py` - Main module with application logic
        - `output/app.py` - Gradio interface to test the application  
        - `output/test_{module_name}.py` - Unit tests
        - `output/{module_name}_design.md` - Architectural design
        """)
        
        submit_btn.click(
            fn=process_input,
            inputs=user_input,
            outputs=[output_result, progress_bar, status_text]
        )
    
    return demo

# ==================== EXECUTION ====================
if __name__ == "__main__":
    print("🟢 Starting system...")
    
    # Check requirements
    try:
        import importlib.util
        crewai_available = importlib.util.find_spec("crewai") is not None
        crew_py_exists = (Path(__file__).parent / "crew.py").exists()
        
        print(f"📦 CrewAI installed: {crewai_available}")
        print(f"📄 crew.py found: {crew_py_exists}")
        print(f"🔑 API Key configured: {bool(API_KEY)}")
        
    except Exception as e:
        print(f"❌ Error checking requirements: {e}")
    
    print("🌐 Server: http://localhost:7860")
    
    interface = create_interface()
    interface.launch(server_name="0.0.0.0", server_port=7860)