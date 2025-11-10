Documentación del Proyecto Asistente iUrban.es
Descripción General
Este proyecto es un sistema de preguntas y respuestas inteligente construido con OpenAI Agents SDK que puede buscar información en el sitio web iurban.es y responder a tus consultas de manera segura y eficiente. Piensa en él como un asistente virtual especializado que conoce todo sobre iurban.es.

Requisitos Técnicos
Librerías y Dependencias Principales
Backend y IA:

openai - Para acceder a los modelos de OpenAI y el Agents SDK

agents - OpenAI Agents SDK (framework principal para crear agentes inteligentes)

numpy - Para cálculos matemáticos en búsquedas semánticas

Procesamiento Web:

requests - Para descargar contenido de sitios web

beautifulsoup4 - Para analizar y extraer información de páginas HTML

Interfaz de Usuario:

gradio - Para crear la interfaz web interactiva

asyncio - Para manejar operaciones simultáneas eficientemente

Seguridad y Utilidades:

re - Para expresiones regulares y validación de patrones

os - Para manejo de variables de entorno y sistema

Versiones Recomendadas
text
openai>=1.0.0
numpy>=1.21.0
requests>=2.25.0
beautifulsoup4>=4.9.0
gradio>=4.0.0
python>=3.8
Componentes del Sistema
1. Backend (backend.py) - El Cerebro con OpenAI Agents SDK
El backend utiliza el OpenAI Agents SDK para crear agentes inteligentes que procesan las consultas:

Arquitectura del Agente:

python
web_analysis_agent = Agent(
    name="WebAnalysisAgent",
    instructions="Eres un asistente seguro...",
    tools=[ask_about_iurban],  # Herramientas personalizadas
    model="gpt-4o-mini",
    input_guardrails=[security_guardrail]  # Sistemas de seguridad
)
Herramientas Personalizadas del Agente:

ask_about_iurban() - Herramienta principal que combina:

Extracción web segura de iurban.es

Búsqueda semántica con embeddings

Generación de respuestas contextuales

security_guardrail() - Sistema de seguridad que verifica cada entrada

Proceso de Búsqueda con Agents SDK:

Runner.run() - Ejecuta el agente con la consulta del usuario

Guardrails - Filtran y validan la entrada antes de procesar

Tools - El agente decide cuándo usar cada herramienta

Traces - Registro detallado de cada paso del proceso

Funciones de Seguridad:

Filtro de Entrada: Revisa cada pregunta para detectar y bloquear contenido malicioso o intentos de hackeo usando el sistema de guardrails del Agents SDK

Limpieza HTML: Elimina cualquier código peligroso que pueda venir del sitio web

Validación de URLs: Solo permite acceder a iurban.es, bloqueando otros sitios

Características Técnicas:

Caché Inteligente: Recuerda búsquedas anteriores para responder más rápido

Límites de Tiempo: Evita que el sistema se quede "colgado"

Control de Tamaño: Maneja eficientemente grandes cantidades de texto

2. Interfaz Web (app.py) - Frontend con Gradio
La interfaz web construida con Gradio proporciona una experiencia de usuario amigable:

Tecnologías Utilizadas:

Gradio Framework - Para crear interfaces web rápidamente

CSS Personalizado - Para estilos y diseño responsive

Manejo Asíncrono - Para no bloquear la interfaz durante procesamiento

Panel de Consultas:

Área para escribir tus preguntas sobre iurban.es

Botones para enviar consultas y limpiar conversaciones

Límite de 500 caracteres por pregunta

Panel de Respuestas:

Muestra las respuestas del asistente en un formato claro

Incluye estadísticas sobre la respuesta (longitud, hora)

Panel del Sistema:

Muestra el estado actual del sistema

Número de búsquedas almacenadas en memoria

Información de la última consulta procesada

Integración con Agents SDK:

python
# Conexión directa con el agente de OpenAI
result = await Runner.run(web_analysis_agent, question)
3. Sistema de Pruebas (test.py) - Calidad y Seguridad
Las pruebas aseguran que el sistema funcione correctamente usando pytest:

Tecnologías de Testing:

pytest - Framework principal de pruebas

unittest.mock - Para simular componentes externos

MagicMock - Para crear objetos de prueba

Pruebas de Seguridad:

Verifica que el sistema bloquee código malicioso

Confirma que solo se permitan URLs de iurban.es

Valida la eliminación de etiquetas HTML peligrosas

Pruebas de Funcionalidad:

Simula extracciones web exitosas y fallidas

Verifica el manejo de errores y timeouts

Prueba la generación de respuestas

Pruebas de Integración con Agents SDK:

Mock del módulo agents para pruebas aisladas

Verificación de imports y dependencias

Pruebas de funciones asíncronas

Trazabilidad y Observabilidad con OpenAI Agents SDK
Sistema de Monitoreo en Tiempo Real:

El OpenAI Agents SDK incluye un sistema completo de trazas que puedes ver en:

text
https://platform.openai.com/logs?api=traces
Qué puedes monitorear:

Cada paso que sigue el agente para procesar tu pregunta

Tiempos de ejecución de cada herramienta y guardrail

Decisiones del agente sobre qué herramientas usar

Errores y advertencias en tiempo real

Uso de caché y optimizaciones de rendimiento

Funciones de Trazabilidad:

trace("WebQASystemSecure") - Marca secciones específicas del código

Logs automáticos del Agents SDK de cada decisión del agente

Métricas de rendimiento de cada componente

Cómo Usar el Sistema
Instalación y Configuración:
Instalar Dependencias:

bash
pip install openai numpy requests beautifulsoup4 gradio pytest
Configurar API Key:

Crear archivo .env con tu clave de OpenAI

OPENAI_API_KEY=tu_clave_aqui

Ejecutar el Sistema:

bash
python app.py
Para Usuarios Normales:
Iniciar el Sistema: Ejecuta python app.py en la terminal

Acceder a la Interfaz: Abre tu navegador en http://localhost:7860

Hacer Preguntas: Escribe preguntas sobre iurban.es en el cuadro de texto

Ver Respuestas: Lee las respuestas generadas por el agente inteligente

Para Desarrolladores:
Ejecutar Pruebas:

bash
python test.py
# o
pytest test.py -v
Monitorear el Agente: Revisa las trazas en la plataforma OpenAI

Modificar Herramientas: Añade nuevas herramientas al agente

Personalizar Guardrails: Adapta las reglas de seguridad según necesidades

Características de Seguridad con Agents SDK
El sistema utiliza múltiples capas de protección del OpenAI Agents SDK:

Guardrails de Entrada: Sistema integrado del SDK para validación

Detección de Inyecciones: Bloquea intentos de manipular el prompt del agente

Limpieza de Contenido: Elimina código peligroso automáticamente

Límites Estrictos: Controla el tamaño de entradas y salidas

Validación de Fuentes: Solo usa información de iurban.es

Características Técnicas Avanzadas
Agentes con Herramientas: El agente decide cuándo usar cada función

Búsqueda Semántica: Encuentra información relevante usando embeddings

Cache de Embeddings: Almacena búsquedas para mejor rendimiento

Rate Limiting: Protege contra uso excesivo de la API de OpenAI

Trazas Completas: Monitorea cada aspecto de la ejecución del agente

Flujo de Datos del Sistema
text
Usuario → Interfaz Gradio → Guardrails SDK → Agente OpenAI → Herramientas → 
Extracción Web → Búsqueda Semántica → Generación Respuesta → 
Interfaz Usuario → Trazas OpenAI
Solución de Problemas
Errores Comunes:

API Key no encontrada: Verificar archivo .env

Timeout en respuestas: Revisar conexión a internet

Preguntas bloqueadas: Verificar que no contengan patrones maliciosos

Herramientas de Debugging:

Panel de estado en la interfaz Gradio

Trazas detalladas en platform.openai.com/logs

Logs de consola durante ejecución

Este sistema combina la potencia del OpenAI Agents SDK con medidas de seguridad robustas para proporcionar respuestas confiables sobre iurban.es, manteniendo la simplicidad y facilidad de uso para todos los usuarios mientras ofrece capacidades avanzadas de monitoreo y trazabilidad para desarrolladores.