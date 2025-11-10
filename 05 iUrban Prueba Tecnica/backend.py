# backend.py
import os
import numpy as np
from openai import AsyncOpenAI
from agents import Agent, Runner, function_tool, trace, input_guardrail, GuardrailFunctionOutput
import requests
from bs4 import BeautifulSoup
import asyncio
import re

# Buscar el archivo .env
env_locations = ['.env', '../.env', '../../.env', '../../../.env']
api_key = None
for env_path in env_locations:
    try:
        with open(env_path, 'r') as f:
            for line in f:
                if 'OPENAI_API_KEY' in line and '=' in line:
                    key, value = line.strip().split('=', 1)
                    api_key = value
                    print(f"✅ API key encontrada en: {env_path}")
                    break
        if api_key:
            break
    except FileNotFoundError:
        continue

if not api_key:
    print("❌ Error: No se encontró OPENAI_API_KEY")
    exit(1)

client = AsyncOpenAI(api_key=api_key)
os.environ["OPENAI_API_KEY"] = api_key

# Caché simple con expiración (ahora global para acceso desde frontend)
embedding_cache = {}
CACHE_EXPIRY_SECONDS = 3600

# GUARDRAIL DE SEGURIDAD CORREGIDO
@input_guardrail
async def security_guardrail(ctx, agent, message):
    """Guardrail que bloquea inyecciones y contenido malicioso"""
    
    if not message or len(message.strip()) == 0:
        return GuardrailFunctionOutput(
            output_info={"reason": "Mensaje vacío"},
            tripwire_triggered=True
        )
    
    if len(message) > 500:
        return GuardrailFunctionOutput(
            output_info={"reason": "Mensaje demasiado largo (>500 chars)"},
            tripwire_triggered=True
        )
    
    # Detectar inyección de prompts
    injection_patterns = [
        r'(?i)ignore.*previous',
        r'(?i)system.*prompt', 
        r'(?i)role.*play',
        r'(?i)you are now',
        r'(?i)from now on',
        r'(?i)as an ai',
    ]
    
    for pattern in injection_patterns:
        if re.search(pattern, message):
            return GuardrailFunctionOutput(
                output_info={"reason": "Intento de inyección de prompt"},
                tripwire_triggered=True
            )
    
    # Detectar código y scripts
    code_patterns = [
        r'(?i)<script[^>]*>',
        r'(?i)javascript:',
        r'(?i)onload=',
        r'(?i)onerror=',
        r'<iframe',
        r'exec\(',
        r'eval\(',
        r'import os',
        r'import sys',
    ]
    
    for pattern in code_patterns:
        if re.search(pattern, message):
            return GuardrailFunctionOutput(
                output_info={"reason": "Código malicioso detectado"},
                tripwire_triggered=True
            )
    
    # CORRECCIÓN: output_info siempre requerido
    return GuardrailFunctionOutput(
        output_info={"reason": "Input válido"},
        tripwire_triggered=False
    )

# Sanitización HTML
def sanitize_html(text: str) -> str:
    """Elimina etiquetas HTML peligrosas"""
    if not text:
        return ""
    clean = re.sub(r'<[^>]*>', '', text)
    clean = re.sub(r'on\w+=', '', clean)
    return clean[:5000]

# Validación de URL
def validate_url(url: str) -> bool:
    """Valida que la URL sea segura"""
    allowed_domains = ['iurban.es']
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return any(parsed.netloc.endswith(domain) for domain in allowed_domains)
    except:
        return False

# Herramienta de extracción web segura
def extract_web_content():
    """Extrae contenido de iurban.es con seguridad"""
    target_url = "https://iurban.es"
    
    if not validate_url(target_url):
        return {"error": "URL no permitida", "status": "failed"}
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        
        response = requests.get(target_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Verificar tipo de contenido
        content_type = response.headers.get('content-type', '')
        if 'text/html' not in content_type:
            return {"error": "Contenido no HTML", "status": "failed"}
        
        # Limitar tamaño
        if len(response.content) > 5 * 1024 * 1024:
            return {"error": "Contenido demasiado grande", "status": "failed"}
        
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title.text.strip() if soup.title else "iUrban"
        
        # Sanitizar contenido
        paragraphs = [p.get_text().strip() for p in soup.find_all('p')[:10]]
        sanitized_paragraphs = [sanitize_html(p) for p in paragraphs]
        
        content = " ".join([p for p in sanitized_paragraphs if len(p) > 20])
        
        if len(content) < 50:
            return {"error": "Contenido insuficiente", "status": "failed"}
        
        return {
            "title": sanitize_html(title),
            "content": content[:1500],
            "status": "success"
        }
        
    except requests.exceptions.Timeout:
        return {"error": "Timeout al conectar", "status": "failed"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Error de conexión: {str(e)}", "status": "failed"}
    except Exception as e:
        return {"error": f"Error inesperado: {str(e)}", "status": "failed"}

# Generar embeddings con cache
async def generate_embeddings(text: str):
    """Genera embeddings con cache y rate limiting"""
    if not text or len(text.strip()) < 5:
        return None
    
    current_time = asyncio.get_event_loop().time()
    if text in embedding_cache:
        cached_data = embedding_cache[text]
        if current_time - cached_data['timestamp'] < CACHE_EXPIRY_SECONDS:
            return cached_data['embedding']
    
    try:
        await asyncio.sleep(0.1)  # Rate limiting
        
        response = await client.embeddings.create(
            model="text-embedding-3-small",
            input=text[:8000]
        )
        embedding = response.data[0].embedding
        
        embedding_cache[text] = {
            'embedding': embedding,
            'timestamp': current_time
        }
        
        return embedding
        
    except Exception as e:
        print(f"⚠️ Error en embeddings: {e}")
        return None

# Búsqueda semántica
async def semantic_search(query: str, content: str):
    """Busca información relevante con embeddings"""
    if not content or len(content) < 50:
        return "Contenido insuficiente"
    
    try:
        query_embedding = await generate_embeddings(query)
        if not query_embedding:
            return "Error procesando consulta"
        
        sentences = [s.strip() for s in content.split('.') if 20 < len(s.strip()) < 500]
        
        if not sentences:
            return "No hay oraciones válidas"
        
        best_match = ""
        best_similarity = 0
        
        for sentence in sentences[:50]:
            sentence_embedding = await generate_embeddings(sentence)
            if sentence_embedding:
                try:
                    similarity = np.dot(query_embedding, sentence_embedding)
                    norm_product = np.linalg.norm(query_embedding) * np.linalg.norm(sentence_embedding)
                    if norm_product > 0:
                        similarity /= norm_product
                    
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_match = sentence
                except:
                    continue
        
        return best_match if best_similarity > 0.3 else "No se encontró información relevante"
        
    except Exception as e:
        return f"Error en búsqueda: {str(e)}"

# HERRAMIENTA PRINCIPAL
@function_tool
async def ask_about_iurban(question: str):
    """Responde preguntas sobre iurban.es con seguridad"""
    try:
        web_data = extract_web_content()
        if web_data["status"] == "failed":
            return f"❌ No se pudo acceder a iurban.es: {web_data['error']}"
        
        relevant_info = await semantic_search(question, web_data["content"])
        
        if relevant_info.startswith("Error") or "No se encontró" in relevant_info:
            return "🤔 No encontré información específica sobre esto en iurban.es"
        
        prompt = f"""
        Información de iurban.es: {relevant_info}
        
        Pregunta: {question}
        
        Responde basándote ÚNICAMENTE en la información proporcionada.
        Máximo 200 caracteres.
        """
        
        try:
            response = await asyncio.wait_for(
                client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=100,
                    temperature=0.3
                ),
                timeout=30.0
            )
            
            answer = response.choices[0].message.content
            if len(answer) > 200:
                answer = answer[:197] + "..."
            return answer
            
        except asyncio.TimeoutError:
            return "⏰ Timeout al generar respuesta"
            
    except Exception as e:
        return f"❌ Error del sistema: {str(e)}"

# AGENTE CON GUARDRAIL
web_analysis_agent = Agent(
    name="WebAnalysisAgent",
    instructions="""
    Eres un asistente seguro que responde preguntas sobre iurban.es.
    
    Solo usa la herramienta ask_about_iurban.
    Responde siempre en español con máximo 200 caracteres.
    """,
    tools=[ask_about_iurban],
    model="gpt-4o-mini",
    input_guardrails=[security_guardrail]
)

# Función para uso directo (opcional)
async def process_question_directly(question: str):
    """Procesa una pregunta directamente (para uso externo)"""
    try:
        with trace("WebQASystemSecure"):
            result = await Runner.run(web_analysis_agent, question)
            return {
                "answer": result.final_output,
                "length": len(result.final_output),
                "cache_size": len(embedding_cache),
                "success": True
            }
    except Exception as e:
        return {
            "answer": f"❌ Error: {str(e)}",
            "length": 0,
            "cache_size": len(embedding_cache),
            "success": False
        }

if __name__ == "__main__":
    print("✅ Backend cargado correctamente")
    print("🔧 Ejecuta 'python app.py' para iniciar la interfaz web")