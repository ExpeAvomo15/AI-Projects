from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
from pydantic import BaseModel, Field
from typing import List
from crewai.memory import LongTermMemory, ShortTermMemory, EntityMemory
from crewai.memory.storage.rag_storage import RAGStorage
from crewai.memory.storage.ltm_sqlite_storage import LTMSQLiteStorage
from dotenv import load_dotenv
import os

def load_environment():
    """Carga las variables de entorno"""
    # Cargar el archivo .env desde la carpeta raíz del proyecto "agents"
    dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../.env"))
    
    # Si no existe, intentar desde el directorio actual
    if not os.path.exists(dotenv_path):
        dotenv_path = ".env"
    
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path=dotenv_path)
    else:
        # Intentar cargar desde variables de sistema
        load_dotenv()

load_environment()

class SecurityThreat(BaseModel):
    """A cybersecurity threat identified in the wild"""
    name: str = Field(description="Threat name or identifier")
    type: str = Field(description="Type of threat (malware, phishing, zero-day, etc.)")
    severity: str = Field(description="Severity level (Critical, High, Medium, Low)")
    description: str = Field(description="Brief description of the threat")

class SecurityThreatList(BaseModel):
    """List of multiple cybersecurity threats"""
    threats: List[SecurityThreat] = Field(description="List of identified cybersecurity threats")

class ThreatAnalysis(BaseModel):
    """Detailed analysis of a cybersecurity threat"""
    name: str = Field(description="Threat name")
    technical_details: str = Field(description="Technical analysis and attack vectors")
    impact_assessment: str = Field(description="Potential impact and affected systems")
    mitigation_strategies: str = Field(description="Recommended mitigation and protection measures")
    ioc_indicators: str = Field(description="Indicators of Compromise (IOCs)")

class ThreatAnalysisList(BaseModel):
    """A list of detailed analysis for all threats"""
    analysis_list: List[ThreatAnalysis] = Field(description="Comprehensive analysis of all threats")


@CrewBase
class CyberSentinel():
    """CyberSentinel crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def threat_detector(self) -> Agent:
        return Agent(config=self.agents_config['threat_detector'],
                     tools=[SerperDevTool()], memory=True)
    
    @agent
    def security_analyst(self) -> Agent:
        return Agent(config=self.agents_config['security_analyst'], 
                     tools=[SerperDevTool()])

    @agent
    def threat_assessor(self) -> Agent:
        return Agent(config=self.agents_config['threat_assessor'], 
                     tools=[SerperDevTool()], memory=True)

    @agent
    def visualization_engineer(self) -> Agent:
        return Agent(config=self.agents_config['visualization_engineer'],
                    allow_code_execution=True,
                    code_execution_mode="safe")

    @task
    def detect_security_threats(self) -> Task:
        return Task(
            config=self.tasks_config['detect_security_threats'],
            output_pydantic=SecurityThreatList,
        )

    @task
    def analyze_threats(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_threats'],
            output_pydantic=ThreatAnalysisList,
        )

    @task
    def assess_critical_threats(self) -> Task:
        return Task(
            config=self.tasks_config['assess_critical_threats'],
        )

    @task
    def create_security_dashboard(self) -> Task:
        return Task(
            config=self.tasks_config['create_security_dashboard'],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the CyberSentinel crew"""

        manager = Agent(
            config=self.agents_config['manager'],
            allow_delegation=True
        )
            
        return Crew(
            agents=self.agents,
            tasks=self.tasks, 
            process=Process.hierarchical,
            verbose=True,
            manager_agent=manager,
            memory=True,
            long_term_memory=LongTermMemory(
                storage=LTMSQLiteStorage(
                    db_path="./memory/long_term_memory_storage.db"
                )
            ),
            short_term_memory=ShortTermMemory(
                storage=RAGStorage(
                    embedder_config={
                        "provider": "openai",
                        "config": {
                            "model": 'text-embedding-3-small'
                        }
                    },
                    type="short_term",
                    path="./memory/"
                )
            ),
            entity_memory=EntityMemory(
                storage=RAGStorage(
                    embedder_config={
                        "provider": "openai",
                        "config": {
                            "model": 'text-embedding-3-small'
                        }
                    },
                    type="short_term",
                    path="./memory/"
                )
            ),
        )