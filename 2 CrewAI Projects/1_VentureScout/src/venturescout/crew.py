import os
from dotenv import load_dotenv
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
from crewai.memory import LongTermMemory, ShortTermMemory, EntityMemory
from crewai.memory.storage.rag_storage import RAGStorage
from crewai.memory.storage.ltm_sqlite_storage import LTMSQLiteStorage

def load_environment():
    """Carga las variables de entorno desde múltiples ubicaciones posibles"""
    # Lista de posibles ubicaciones del .env (ajustadas para tu estructura)
    current_dir = os.path.dirname(__file__)
    possible_env_paths = [
        # En el directorio actual
        os.path.join(current_dir, ".env"),
        # En el directorio padre del proyecto
        os.path.join(current_dir, "..", ".env"),
        # En el directorio raíz (donde tienes tu .env original)
        os.path.join(current_dir, "..", "..", "..", "..", ".env"),
        # Ruta específica conocida
        r"C:\Users\cex\projects\agents\.env"
    ]
    
    env_loaded = False
    for env_path in possible_env_paths:
        abs_path = os.path.abspath(env_path)
        if os.path.exists(abs_path):
            print(f"🔑 Loading environment from: {abs_path}")
            load_dotenv(dotenv_path=abs_path)
            env_loaded = True
            break
    
    if not env_loaded:
        print("⚠️  No .env file found in expected locations")
        # Intento de carga por defecto
        load_dotenv()
    
    # Verificar que las variables clave estén cargadas
    openai_key = os.getenv('OPENAI_API_KEY')
    serper_key = os.getenv('SERPER_API_KEY')
    
    if not openai_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("📍 Expected locations searched:")
        for path in possible_env_paths:
            print(f"   - {os.path.abspath(path)}")
        print("\n💡 Solutions:")
        print("   1. Copy your .env file to the project directory")
        print("   2. Set environment variables manually")
        print("   3. Use a different .env location")
    else:
        print("✅ OPENAI_API_KEY loaded successfully")
        
    if not serper_key:
        print("⚠️  SERPER_API_KEY not found in environment variables")
    else:
        print("✅ SERPER_API_KEY loaded successfully")
    # Si no se cargaron las variables, intentar cargarlas manualmente
    if not openai_key:
        # Intentar leer desde el .env conocido
        known_env_path = r"C:\Users\cex\projects\agents\.env"
        if os.path.exists(known_env_path):
            print(f"🔄 Attempting manual load from: {known_env_path}")
            with open(known_env_path, 'r') as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            os.environ[key] = value.strip('"\'')
            
            # Verificar de nuevo
            if os.getenv('OPENAI_API_KEY'):
                print("✅ OPENAI_API_KEY loaded manually")
            if os.getenv('SERPER_API_KEY'):
                print("✅ SERPER_API_KEY loaded manually")
        
    return env_loaded

load_environment()

@CrewBase
class VentureScoutCrew():
    """VentureScout AI crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def market_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config['market_analyzer'],
            tools=[SerperDevTool()],
            verbose=True
        )

    @agent
    def startup_scout(self) -> Agent:
        return Agent(
            config=self.agents_config['startup_scout'],
            tools=[SerperDevTool()],
            verbose=True
        )

    @agent
    def financial_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['financial_analyst'],
            tools=[SerperDevTool()],
            verbose=True
        )

    @agent
    def investment_strategist(self) -> Agent:
        return Agent(
            config=self.agents_config['investment_strategist'],
            verbose=True
        )

    @agent
    def visualization_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['visualization_agent'],
            verbose=True,
            allow_code_execution=True,
            code_execution_mode="safe",  # Uses Docker for safety
            max_execution_time=300, 
            max_retry_limit=5,
        )

    @task
    def analyze_market_trends(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_market_trends'],
            agent=self.market_analyzer()
        )

    @task
    def find_promising_startups(self) -> Task:
        return Task(
            config=self.tasks_config['find_promising_startups'],
            agent=self.startup_scout()
        )

    @task
    def analyze_financial_health(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_financial_health'],
            agent=self.financial_analyst()
        )

    @task
    def generate_investment_recommendations(self) -> Task:
        return Task(
            config=self.tasks_config['generate_investment_recommendations'],
            agent=self.investment_strategist()
        )

    @task
    def generate_visual_dashboard(self) -> Task:
        return Task(
            config=self.tasks_config['generate_visual_dashboard'],
            agent=self.visualization_agent()
        )

    @crew
    def crew(self) -> Crew:
        """Creates the VentureScout AI crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=False  # Desactivar memoria temporalmente
        )