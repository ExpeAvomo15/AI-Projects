#!/usr/bin/env python
import sys
import warnings
import os
from datetime import datetime

# Fix for Windows asyncio issue
import asyncio
import platform

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crew import VentureScoutCrew

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# Create output directory if it doesn't exist
os.makedirs('output', exist_ok=True)
os.makedirs('memory', exist_ok=True)
os.makedirs('memory/short_term', exist_ok=True)
os.makedirs('memory/entities', exist_ok=True)

def run():
    """
    Run the VentureScout AI crew.
    """
    inputs = {
        'sector': 'inteligencia artificial, blockchain, clean energy',
        'investment_criteria': 'startups en etapa seed o serie A, equipos técnicos fuertes, mercado addressable mínimo de $1B',
        'investment_thesis': 'tecnologías disruptivas con potencial de scaling global y defensibilidad',
        'current_date': str(datetime.now())
    }
    
    print("🚀 Starting VentureScout AI analysis...")
    
    try:
        # Initialize the crew
        venture_crew = VentureScoutCrew()
        
        # Run the crew
        result = venture_crew.crew().kickoff(inputs=inputs)
        
        print("\n" + "="*60)
        print("💼 VENTURESCOUT AI INVESTMENT REPORT")
        print("="*60)
        
        # Access the result properly
        if hasattr(result, 'raw'):
            output = result.raw
        else:
            output = str(result)
            
        print(output)
        
        # Save results
        with open('output/investment_report.txt', 'w', encoding='utf-8') as f:
            f.write(output)
        
        print("\n✅ Analysis completed. Report saved to output/investment_report.txt")
        
        return result
        
    except Exception as e:
        print(f"❌ Error during execution: {str(e)}")
        raise

if __name__ == "__main__":
    run()