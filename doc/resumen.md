# Resumen del Proyecto — Promtior Chatbot

## Cómo abordé el desafío

Al leer los requisitos, identifiqué que el objetivo central era construir un chatbot capaz de responder preguntas específicas sobre Promtior. La arquitectura RAG era la indicada para esto: en lugar de depender del conocimiento general de un LLM (que puede inventar información o estar desactualizado), el sistema primero recupera información real desde una base de conocimiento y luego la usa como contexto para generar la respuesta.

Mi primer paso fue definir esa base de conocimiento. Compilé la información relevante sobre Promtior, su historia de fundación, servicios, cultura y propuesta de valor, en un archivo de texto estructurado (`promtior_data.txt`), que actúa como la única fuente de verdad del sistema.

## Lógica de implementación

El pipeline RAG que construí funciona en dos etapas:

**Etapa de indexado** (al iniciar el servidor):
1. Se carga el archivo de conocimiento y se divide en fragmentos con `CharacterTextSplitter`.
2. Cada fragmento se convierte en un vector numérico usando `HuggingFaceEmbeddings` con el modelo `all-MiniLM-L6-v2`, que corre localmente sin necesidad de API key.
3. Los vectores se almacenan en una base de datos FAISS en memoria, lista para ser consultada.

**Etapa de consulta** (por cada pregunta del usuario):
1. La pregunta se convierte en un vector y se buscan los fragmentos más similares en FAISS.
2. El contexto recuperado y la pregunta original se inyectan en una plantilla de prompt diseñada para que el LLM responda de forma directa.
3. El prompt se envía al LLM `llama-3.3-70b-versatile` via la API de Groq, que genera la respuesta.
4. La respuesta se parsea y se devuelve al usuario a través del endpoint de LangServe.

Para la exposición de la API utilicé **LangServe** sobre **FastAPI**, que además de proveer los endpoints REST genera automáticamente un playground interactivo para probar el chatbot desde el navegador.

## Principales desafíos y cómo los superé

**1. Respuestas incorrectas por datos ambiguos**
La base de conocimiento mencionaba tanto el lanzamiento de ChatGPT (noviembre 2022) como la fundación de Promtior (mayo 2023). El LLM inicialmente confundía ambas fechas y respondía que Promtior se fundó en 2022. Lo resolví de dos formas: siendo más explícito en el archivo de datos (agregando una nota que diferencia claramente ambos eventos) y refinando el prompt para que el modelo priorice la información más específica.

**2. Respuestas en el idioma incorrecto**
El LLM respondía en español incluso cuando se le hacía una pregunta en inglés. La causa raíz era que el contexto recuperado desde `promtior_data.txt` está en español, y el modelo lo tomaba como referencia para el idioma de la respuesta. Lo resolví marcando la regla de idioma como crítica en el prompt, especificando explícitamente que el idioma del contexto es irrelevante y que la respuesta debe coincidir exclusivamente con el idioma de la pregunta.

**3. Compatibilidad de dependencias**
El ecosistema de LangChain evolucionó significativamente entre versiones. Durante el desarrollo encontré múltiples errores de `ModuleNotFoundError` y cambios en las interfaces de los proveedores de modelos. Los resolví migrando los imports a los paquetes modernos correctos (`langchain-community`, `langchain-huggingface`, `langchain-groq`)

**4. Elección del LLM para el despliegue**
Originalmente el proyecto usaba Ollama con llama2 corriendo localmente, lo cual no era viable para desplegar en la nube sin recursos costosos. Migré primero a HuggingFace Inference API, pero los modelos gratuitos dejaron de ser compatibles con la nueva versión de `huggingface_hub`. Finalmente adopté **Groq** como proveedor, que ofrece un tier gratuito con modelos de alta calidad (`llama-3.3-70b-versatile`) y tiempos de respuesta muy rápidos.

## Resultado

El chatbot está desplegado y disponible públicamente en:
**[https://promtior-challenge-production-b9df.up.railway.app/chatbot/playground/]**

