# test.py
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Mock completo del módulo agents ANTES de cualquier import
mock_agents = MagicMock()
mock_agents.Agent = MagicMock()
mock_agents.Runner = MagicMock()
mock_agents.function_tool = lambda f: f
mock_agents.trace = lambda name: lambda f: f
mock_agents.input_guardrail = lambda f: f
mock_agents.GuardrailFunctionOutput = MagicMock

sys.modules['agents'] = mock_agents

# Ahora sí importar backend
from backend import (
    sanitize_html,
    validate_url,
    extract_web_content,
)

# ==================== TESTS DE SANITIZACIÓN ====================

def test_sanitize_html_elimina_tags():
    """Test: elimina etiquetas HTML"""
    texto = "<p>Hola <b>mundo</b></p>"
    resultado = sanitize_html(texto)
    assert "<" not in resultado
    assert "Hola mundo" in resultado

def test_sanitize_html_elimina_eventos():
    """Test: elimina atributos de eventos"""
    texto = '<div onclick="alert()">Click</div>'
    resultado = sanitize_html(texto)
    assert "onclick" not in resultado

def test_sanitize_html_limita_longitud():
    """Test: limita texto a 5000 caracteres"""
    texto = "a" * 6000
    resultado = sanitize_html(texto)
    assert len(resultado) == 5000

def test_sanitize_html_texto_vacio():
    """Test: maneja texto vacío"""
    assert sanitize_html("") == ""
    assert sanitize_html(None) == ""

# ==================== TESTS DE VALIDACIÓN URL ====================

def test_validate_url_dominio_permitido():
    """Test: acepta URLs de iurban.es"""
    assert validate_url("https://iurban.es") == True
    assert validate_url("https://www.iurban.es/sobre-nosotros") == True

def test_validate_url_dominio_bloqueado():
    """Test: rechaza URLs externas"""
    assert validate_url("https://evil.com") == False
    assert validate_url("https://google.com") == False

def test_validate_url_invalida():
    """Test: rechaza URLs malformadas"""
    assert validate_url("not-a-url") == False

# ==================== TESTS DE EXTRACCIÓN WEB ====================

@patch('backend.requests.get')
def test_extract_web_content_exito(mock_get):
    """Test: extrae contenido HTML correctamente"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.headers = {'content-type': 'text/html'}
    html_content = """
    <html>
        <head><title>iUrban Test</title></head>
        <body>
            <p>Somos una empresa de tecnologia urbana con mucho contenido aqui.</p>
            <p>Desarrollamos soluciones innovadoras y creativas para ciudades.</p>
        </body>
    </html>
    """
    mock_response.content = html_content.encode('utf-8')
    mock_get.return_value = mock_response
    
    resultado = extract_web_content()
    assert resultado["status"] == "success"
    assert "iUrban" in resultado["title"]
    assert len(resultado["content"]) > 0

@patch('backend.requests.get')
def test_extract_web_content_timeout(mock_get):
    """Test: maneja timeout correctamente"""
    from requests.exceptions import Timeout
    mock_get.side_effect = Timeout("Connection timeout")
    
    resultado = extract_web_content()
    assert resultado["status"] == "failed"
    assert "error" in resultado

@patch('backend.requests.get')
def test_extract_web_content_contenido_no_html(mock_get):
    """Test: rechaza contenido no HTML"""
    mock_response = Mock()
    mock_response.headers = {'content-type': 'application/json'}
    mock_get.return_value = mock_response
    
    resultado = extract_web_content()
    assert resultado["status"] == "failed"

@patch('backend.requests.get')
def test_extract_web_content_contenido_grande(mock_get):
    """Test: rechaza contenido > 5MB"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.headers = {'content-type': 'text/html'}
    mock_response.content = b"X" * (6 * 1024 * 1024)  # 6MB
    mock_get.return_value = mock_response
    
    resultado = extract_web_content()
    assert resultado["status"] == "failed"
    assert "grande" in resultado["error"]

# ==================== TESTS DE EMBEDDINGS ====================

@pytest.mark.asyncio
@patch('backend.client.embeddings.create')
async def test_generate_embeddings_exito(mock_create):
    """Test: genera embeddings correctamente"""
    from backend import generate_embeddings
    
    mock_response = Mock()
    mock_response.data = [Mock(embedding=[0.1, 0.2, 0.3])]
    mock_create.return_value = mock_response
    
    resultado = await generate_embeddings("texto de prueba")
    assert resultado is not None
    assert len(resultado) == 3

@pytest.mark.asyncio
async def test_generate_embeddings_texto_vacio():
    """Test: maneja texto vacío"""
    from backend import generate_embeddings
    
    resultado = await generate_embeddings("")
    assert resultado is None
    
    resultado = await generate_embeddings("abc")
    assert resultado is None

# ==================== TESTS DE BÚSQUEDA SEMÁNTICA ====================

@pytest.mark.asyncio
async def test_semantic_search_contenido_insuficiente():
    """Test: maneja contenido insuficiente"""
    from backend import semantic_search
    
    resultado = await semantic_search("test", "poco")
    assert "Contenido insuficiente" in resultado

@pytest.mark.asyncio
async def test_semantic_search_sin_oraciones():
    """Test: maneja contenido sin oraciones válidas"""
    from backend import semantic_search
    
    resultado = await semantic_search("test", "a b c d e")
    # La función retorna "Contenido insuficiente" para contenido corto
    assert "Contenido insuficiente" in resultado or "No hay oraciones" in resultado

# ==================== CONFIGURACIÓN PYTEST ====================

def test_imports_correctos():
    """Test: verifica que los imports funcionan"""
    from backend import (
        sanitize_html,
        validate_url,
        extract_web_content,
    )
    assert callable(sanitize_html)
    assert callable(validate_url)
    assert callable(extract_web_content)

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])