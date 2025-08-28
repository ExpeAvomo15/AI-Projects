#!/usr/bin/env python
import sys
import warnings
import os
from datetime import datetime

from cybersentinel.crew import CyberSentinel

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def run():
    """
    Run the research crew.
    """
    # Solicitar el nombre de la empresa al usuario
    company_name = input("Por favor, ingrese el nombre de la empresa para el análisis de ciberseguridad: ")
    
    inputs = {
        'sector': 'Technology',
        'company': company_name,  # Nuevo input para la empresa
        'threat_category': 'cybersecurity',  # Añadimos threat_category que faltaba
        "current_date": str(datetime.now())
    }

    # Create and run the crew
    result = CyberSentinel().crew().kickoff(inputs=inputs)

    # Print the result
    print("\n\n=== FINAL DECISION ===\n\n")
    print(result.raw)


if __name__ == "__main__":
    run()