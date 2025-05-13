import streamlit as st
import fitz  # PyMuPDF
from fuzzywuzzy import fuzz, process
from datetime import datetime
import openai
import os

# Configurar API Key de OpenAI desde variable de entorno
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Leer y combinar texto PDF
@st.cache_data
def leer_pdf(path):
    texto = ""
    try:
        with fitz.open(path) as doc:
            for pagina in doc:
                texto += pagina.get_text()
    except Exception as e:
        st.error(f"⚠️ Error al leer {path}: {e}")
    return texto

# Procesamiento de coincidencia difusa
def buscar_respuesta(pregunta, texto):
    lineas = [line.strip() for line in texto.split("\n") if line.strip()]
    mejor, score = process.extractOne(pregunta.lower(), lineas, scorer=fuzz.partial_ratio)
    if score >= 60:
        return mejor[:280] + "..." if len(mejor) > 300 else mejor
    return None

# Generación de respuesta con IA
def responder_ia(pregunta):
    try:
        respuesta = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Sos un asistente de RRHH que responde con lenguaje claro y humano."},
                {"role": "user", "content": pregunta}
            ]
        )
        return respuesta.choices[0].message.content.strip()
    except Exception as e:
        return f"Error al contactar OpenAI: {e}"

# App principal
st.title("👩‍💼💼 Asistente Virtual de RRHH")
st.markdown("Consultá sobre el manual ingresante, capacitación y normativa interna.")

pregunta = st.text_input("¿Qué querés consultar?")

if pregunta:
    texto1 = leer_pdf("Manual Administrativo Usina .pdf")
    texto2 = leer_pdf("Copia de Manual Ingresante.pdf")
    texto3 = leer_pdf("CAPACITACION 2025 .pdf")
    todo_texto = "\n".join([texto1, texto2, texto3])

    respuesta = buscar_respuesta(pregunta, todo_texto)

    if respuesta:
        st.success(respuesta)
    else:
        respuesta_ia = responder_ia(pregunta)
        st.success(respuesta_ia)

