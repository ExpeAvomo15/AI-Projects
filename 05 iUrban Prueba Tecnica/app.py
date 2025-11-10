# app.py
import gradio as gr
import asyncio
import time
from backend import web_analysis_agent, Runner, trace, embedding_cache

# Variable global para almacenar resultados
current_result = None

async def async_process_question(question):
    """Procesa la pregunta de forma asíncrona"""
    global current_result
    
    try:
        if not question or len(question.strip()) == 0:
            return "❌ Por favor, ingresa una pregunta válida", "Esperando consulta..."
        
        with trace("WebQASystemSecure"):
            result = await Runner.run(web_analysis_agent, question)
            
            # Almacenar resultado
            current_result = {
                "answer": result.final_output,
                "length": len(result.final_output),
                "timestamp": time.strftime("%H:%M:%S")
            }
            
            # Actualizar información del sistema
            cache_size = len(embedding_cache)
            system_info = f"""=== ESTADO DEL SISTEMA ===
Agente: WebAnalysisAgent
Modelo: GPT-4o-mini
Embeddings en cache: {cache_size}

=== ÚLTIMA CONSULTA ===
Hora: {current_result['timestamp']}
Longitud respuesta: {current_result['length']} caracteres

=== ENLACES ===
Trazas: https://platform.openai.com/logs?api=traces
Web analizada: https://iurban.es"""
            
            return current_result["answer"], system_info
            
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        current_result = {
            "answer": error_msg,
            "length": len(error_msg),
            "timestamp": time.strftime("%H:%M:%S")
        }
        return error_msg, f"Error en el sistema: {str(e)}"

def process_question(question):
    """Wrapper síncrono para Gradio"""
    try:
        # Ejecutar la función asíncrona
        return asyncio.run(async_process_question(question))
    except Exception as e:
        return f"❌ Error al procesar: {str(e)}", f"Error: {str(e)}"

def get_system_status():
    """Obtiene el estado actual del sistema"""
    global current_result
    
    cache_size = len(embedding_cache)
    
    status_lines = [
        "=== ESTADO DEL SISTEMA ===",
        f"Agente: WebAnalysisAgent",
        f"Modelo: GPT-4o-mini",
        f"Embeddings en cache: {cache_size}",
        "",
        "=== ÚLTIMA CONSULTA ==="
    ]
    
    if current_result:
        status_lines.extend([
            f"Hora: {current_result['timestamp']}",
            f"Longitud respuesta: {current_result['length']} caracteres"
        ])
    else:
        status_lines.append("Aún no se han procesado consultas")
    
    status_lines.extend([
        "",
        "=== ENLACES ===",
        "Trazas: https://platform.openai.com/logs?api=traces",
        "Web analizada: https://iurban.es"
    ])
    
    return "\n".join(status_lines)

def clear_conversation():
    """Limpia la conversación"""
    global current_result
    current_result = None
    return "", get_system_status()

# Configuración de la interfaz Gradio
with gr.Blocks(
    title="Asistente iUrban.es",
    theme=gr.themes.Soft(),
    css="""
    .container { max-width: 800px; margin: 0 auto; }
    .answer-box { 
        background-color: #f0f8ff; 
        padding: 20px; 
        border-radius: 10px; 
        border-left: 4px solid #4CAF50; 
    }
    .system-box { 
        background-color: #fff3cd; 
        padding: 15px; 
        border-radius: 8px; 
        border-left: 4px solid #ffc107; 
        font-family: monospace;
        font-size: 12px;
    }
    .warning { color: #856404; background-color: #fff3cd; border-color: #ffeaa7; }
    .header { text-align: center; margin-bottom: 20px; }
    """
) as demo:
    
    gr.HTML("""
    <div class="header">
        <h1>🤖 Asistente iUrban.es</h1>
        <p><strong>Consulta información actualizada sobre iurban.es de forma segura</strong></p>
    </div>
    """)
    
    with gr.Row():
        with gr.Column(scale=2):
            # Área de entrada
            question_input = gr.Textbox(
                label="📝 Tu pregunta sobre iUrban.es",
                placeholder="Ej: ¿Qué servicios ofrece iUrban? ¿Cuál es su misión? ¿A qué se dedica la empresa?",
                lines=3,
                max_lines=5,
                info="Escribe tu pregunta en español (máximo 500 caracteres)"
            )
            
            with gr.Row():
                submit_btn = gr.Button("🚀 Enviar Consulta", variant="primary", scale=2)
                clear_btn = gr.Button("🧹 Limpiar", variant="secondary", scale=1)
            
            # Área de respuesta
            answer_output = gr.Textbox(
                label="🤖 Respuesta del Asistente",
                interactive=False,
                lines=4,
                elem_classes="answer-box"
            )
            
            # Estadísticas
            stats_output = gr.Textbox(
                label="📊 Estadísticas de la Respuesta",
                value="Esperando consulta...",
                interactive=False,
                lines=2
            )
        
        with gr.Column(scale=1):
            # Panel del sistema
            system_output = gr.Textbox(
                label="⚙️ Estado del Sistema",
                value=get_system_status(),
                interactive=False,
                lines=12,
                elem_classes="system-box"
            )
            
            with gr.Row():
                status_btn = gr.Button("🔄 Actualizar Estado", variant="secondary", scale=2)
    
    # Mensajes informativos
    gr.HTML("""
    <div style="margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 8px;">
        <h3>🔒 Características de Seguridad</h3>
        <ul>
            <li><strong>Guardrails de entrada:</strong> Detección de inyecciones y contenido malicioso</li>
            <li><strong>Sanitización HTML:</strong> Eliminación de etiquetas peligrosas</li>
            <li><strong>Validación de URLs:</strong> Solo se permite iurban.es</li>
            <li><strong>Límites de tamaño:</strong> Protección contra contenido excesivo</li>
        </ul>
        
        <h3>📊 Características Técnicas</h3>
        <ul>
            <li><strong>Búsqueda semántica:</strong> Usa embeddings para encontrar información relevante</li>
            <li><strong>Cache inteligente:</strong> Reutiliza embeddings para mejor rendimiento</li>
            <li><strong>Rate limiting:</strong> Protege contra uso excesivo de API</li>
            <li><strong>Trazas OpenAI:</strong> Monitoreo completo de ejecución</li>
        </ul>
    </div>
    """)
    
    # Event handlers
    def update_stats():
        """Actualiza las estadísticas"""
        if current_result:
            return f"✓ Longitud: {current_result['length']} caracteres | ✓ Hora: {current_result['timestamp']}"
        return "Esperando consulta..."
    
    submit_btn.click(
        fn=process_question,
        inputs=question_input,
        outputs=[answer_output, system_output]
    ).then(
        fn=update_stats,
        outputs=stats_output
    )
    
    clear_btn.click(
        fn=clear_conversation,
        outputs=[question_input, system_output]
    ).then(
        fn=lambda: "Conversación limpiada - listo para nueva consulta",
        outputs=stats_output
    )
    
    status_btn.click(
        fn=get_system_status,
        outputs=system_output
    )

if __name__ == "__main__":
    print("🚀 Iniciando servidor Gradio...")
    print("📱 La interfaz estará disponible en: http://localhost:7860")
    print("⏹️  Presiona Ctrl+C para detener el servidor")
    
    demo.launch(
        server_name="localhost",  # Cambiado de 0.0.0.0 a localhost
        server_port=7860,
        share=False,
        show_error=True,
        inbrowser=True  # Abre automáticamente el navegador
    )