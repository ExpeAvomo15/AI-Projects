"""
OWASP Juice Shop Security Threat Dashboard (Minimal Gradio Version)

REQUIREMENTS:
- gradio>=3.0
- pandas
- plotly

Instructions:
- Ensure 'threat_analysis.json' is present in the same directory.
- The JSON should be a list of threat dicts with "type", "severity", and "mitigation_status" fields.
  Example:
  [
    {"type": "Broken Access Control", "severity": "Critical", "mitigation_status": "Open"},
    {"type": "Injection Attack", "severity": "High", "mitigation_status": "Open"},
    {"type": "Cryptographic Failure", "severity": "Medium", "mitigation_status": "Mitigated"},
    {"type": "Insecure Design", "severity": "High", "mitigation_status": "Open"}
  ]
- No download or upload functionality for max compatibility; table and charts only.
"""

import gradio as gr
import pandas as pd
import plotly.express as px
import json
import os

# Utility: load and validate the threat data
def load_threat_data(path="threat_analysis.json"):
    if not os.path.exists(path):
        return pd.DataFrame(), "File 'threat_analysis.json' not found."
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        # basic schema enforcement
        for col in ["type", "severity", "mitigation_status"]:
            if col not in df.columns:
                df[col] = "Unknown"
        df = df[["type", "severity", "mitigation_status"]]
        return df, None
    except Exception as e:
        return pd.DataFrame(), f"Error loading 'threat_analysis.json': {e}"

def severity_chart(df):
    if df.empty:
        return px.bar(title="No threat data available.")
    levels = ["Critical", "High", "Medium", "Low"]
    return px.histogram(df, x="severity", color="type",
                        category_orders={"severity": levels},
                        title="Severity Distribution")

def mitigation_chart(df):
    if df.empty:
        return px.pie(title="No threat data available.")
    return px.pie(df, names="mitigation_status", title="Mitigation Status")

# Cargar datos una vez al inicio
df, err = load_threat_data()
if err:
    print(f"Error: {err}")
    barfig = px.bar(title="No data available")
    piefig = px.pie(title="No data available")
    table_data = pd.DataFrame({"Error": [err]})
else:
    barfig = severity_chart(df)
    piefig = mitigation_chart(df)
    table_data = df

# Build minimal dashboard - FORMA CORRECTA
with gr.Blocks() as demo:
    gr.Markdown("# OWASP Juice Shop Security Threat Dashboard")
    gr.Markdown("Shows severity and mitigation status from threat_analysis.json")
    
    with gr.Row():
        # Pasar los gráficos directamente al crear los componentes
        gr.Plot(barfig, label="Severity Distribution")
        gr.Plot(piefig, label="Mitigation Status")
    
    # Pasar los datos directamente al crear el DataFrame
    gr.Dataframe(table_data, label="Threat Data Table")

if __name__ == "__main__":
    demo.launch()


