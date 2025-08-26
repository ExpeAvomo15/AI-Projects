import gradio as gr
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px

# Datos basados en análisis previos
data = {
    'Startups': ['Nodal Power', 'Cloover', 'xAI', 'Vortex Bladeless', 'Enapter', 'Delta Green', 'Pavegen', 'Zeno Power', 'Causam Energy', 'Blockenergy'],
    'Sector': ['Renewable Energy', 'Renewable Energy', 'Artificial Intelligence', 'Renewable Energy', 'Clean Tech', 'Clean Energy', 'Renewable Energy and IoT', 'Clean Energy', 'AI and Energy Management', 'Blockchain in Energy'],
    'Stage': ['Seed', 'Seed', 'Series A', 'Series A', 'Seed', 'Seed', 'Series A', 'Seed', 'Series A', 'Seed'],
    'Projected ROI (%)': [20, 25, 30, 22, 28, 26, 24, 27, 29, 21],
    'Growth Potential ($B)': [1.5, 1.2, 1.8, 1.6, 1.3, 1.4, 1.1, 1.0, 1.7, 1.3]
}

df = pd.DataFrame(data)

# Función para crear gráficos

def create_charts():
    # Gráfico de barras de ROI
    plt.figure(figsize=(10, 5))
    plt.bar(df['Startups'], df['Projected ROI (%)'], color='skyblue')
    plt.title('Projected ROI for Startups')
    plt.xlabel('Startups')
    plt.ylabel('Projected ROI (%)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('roi_chart.png')
    plt.close()
    # Gráfico de pastel de crecimiento
    fig = px.pie(df, values='Growth Potential ($B)', names='Startups', title='Growth Potential of Startups')
    fig.write_html('growth_chart.html')

# Función principal para Gradio

def dashboard():
    create_charts()  
    return df, 'roi_chart.png', 'growth_chart.html'

# Interfaz Gradio con gr.Blocks()
with gr.Blocks() as app:
    gr.Markdown("## Dashboard de Recomendaciones de Inversión en Startups")
    with gr.Row():
        data_table = gr.Dataframe(value=df, label='Tabla Comparativa de Startups')
        roi_image = gr.Image(value='roi_chart.png', label='Gráfico de ROI')
    with gr.Row():
        growth_chart = gr.HTML('<iframe src="growth_chart.html" width="100%" height="500"></iframe>')
    button = gr.Button('Actualizar Gráfico')
    button.click(dashboard)

app.launch()