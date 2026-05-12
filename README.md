# Promtior Chatbot — Prueba Técnica

Chatbot basado en la arquitectura RAG, desarrollado con LangChain y LangServe, que responde preguntas sobre Promtior utilizando una base de conocimiento.

---

## Resumen del Proyecto

El objetivo de esta prueba fue construir un chatbot capaz de responder preguntas sobre Promtior utilizando la arquitectura **RAG (Generación Aumentada con Recuperación)** y el framework **LangChain**.

### Enfoque

En lugar de depender únicamente del conocimiento general del LLM (que puede desvariar o estar desactualizado), implementé un pipeline RAG que primero recupera información relevante desde una base de conocimiento y luego la pasa al LLM como contexto para generar una respuesta precisa.

La base de conocimiento fue construida a partir de información sobre Promtior: su historia de fundación, servicios, cultura y propuesta de valor.

### Lógica de Implementación

1. **Base de conocimiento:** Toda la información relevante sobre Promtior fue compilada en un archivo de texto (`app/promtior_data.txt`), que actúa como única fuente de verdad para el chatbot.
2. **División de texto:** El documento se divide en fragmentos más pequeños usando `CharacterTextSplitter` para permitir una recuperación eficiente y precisa.
3. **Embeddings y Vector Store:** Cada fragmento se convierte en un vector numérico usando `OllamaEmbeddings` (llama2) y se almacena en una base de datos vectorial **FAISS** en memoria.
4. **Recuperación:** Cuando se recibe una pregunta, los fragmentos más semánticamente relevantes son recuperados de FAISS mediante búsqueda por similitud.
5. **Generación:** El contexto recuperado y la pregunta original se inyectan en un prompt y se envían al LLM **llama2** (a través de Ollama) para generar una respuesta.
6. **API:** El pipeline RAG completo se expone como un endpoint REST usando **FastAPI** y **LangServe**, incluyendo un playground interactivo para pruebas.

### Principales Desafíos y Soluciones

- **Respuestas incorrectas por datos ambiguos:** La base de conocimiento contenía información tanto sobre el lanzamiento de ChatGPT (noviembre 2022) como sobre la fundación de Promtior (mayo 2023). El LLM inicialmente confundía ambas fechas. Se resolvió haciendo la distinción explícita en el texto de la base de conocimiento y refinando el prompt.
- **Respuestas en el idioma incorrecto:** El LLM respondía en inglés incluso cuando se le hablaba en español. Se resolvió agregando instrucciones explícitas de detección de idioma directamente en el prompt, incluyendo un marcador de respuesta con etiqueta de idioma.
- **Conflictos de dependencias:** El ecosistema de LangChain evolucionó significativamente entre versiones. Varios errores de `ModuleNotFoundError` se resolvieron migrando los imports a los paquetes modernos correctos (`langchain-community`, `langchain-ollama`, `langchain-text-splitters`).

---

## Diagrama de Componentes

![Diagrama de Componentes](doc/component_diagram.png)

---

## Stack Tecnológico

| Componente | Tecnología |
|---|---|
| LLM | llama2 (via Ollama) |
| Embeddings | OllamaEmbeddings (llama2) |
| Vector Store | FAISS (en memoria) |
| Framework RAG | LangChain |
| Servidor API | FastAPI + LangServe |
| Runtime | Python 3.10+ |

---

## Cómo Ejecutar Localmente

### Requisitos previos
- [Python 3.10+](https://www.python.org/)
- [Ollama](https://ollama.com/) instalado y corriendo
- Modelo llama2 descargado: `ollama pull llama2`

### Pasos

1. **Clonar el repositorio:**
    ```bash
    git clone <tu-repo-url>
    cd promtior_challenge
    ```

2. **Crear y activar un entorno virtual:**
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3. **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Asegurarse de que Ollama esté corriendo** con el modelo llama2 disponible.

5. **Iniciar el servidor:**
    ```bash
    python -m app.main
    ```

6. **Abrir el playground interactivo:**
    ```
    http://localhost:8000/chatbot/playground/
    ```

