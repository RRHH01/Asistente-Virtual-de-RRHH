# app.py
import streamlit as st
import fitz  # PyMuPDF
from fuzzywuzzy import fuzz, process
from datetime import datetime
import openai
import os

# Configurar API Key desde secretos
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Leer PDF
@st.cache_data
def leer_pdf(path):
    texto = ""
    try:
        with fitz.open(path) as doc:
            for pagina in doc:
                texto += pagina.get_text()
    except Exception as e:
        st.error(f"Error al leer {path}: {e}")
    return texto

# Reformular respuesta con lenguaje natural
def reformular_respuesta(contexto, pregunta):
    prompt = f"""
    Respondé de forma clara, amigable y profesional como si fueras un asistente de RRHH humano.
    Basá tu respuesta solo en esta información:
    ---
    {contexto}
    ---
    Pregunta: {pregunta}
    Respuesta:
    """
    try:
        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return respuesta.choices[0].message.content.strip()
    except Exception as e:
        return f"Error al contactar OpenAI: {e}"

# Buscar en texto por coincidencia difusa
def buscar_contexto(pregunta, texto):
    lineas = [line.strip() for line in texto.split("\n") if line.strip()]
    mejor, score = process.extractOne(pregunta.lower(), lineas, scorer=fuzz.partial_ratio)
    return mejor if score > 60 else ""

# Cargar PDFs
texto_1 = leer_pdf("CAPACITACION 2025 .pdf")
texto_2 = leer_pdf("Copia de Manual Ingresante.pdf")
texto_3 = leer_pdf("Manual Administrativo Usina .pdf")
corpus = "\n".join([texto_1, texto_2, texto_3])

# Interfaz Streamlit
st.title("👩‍💼🧑‍💼 Asistente Virtual de RRHH")
st.write("Consultá sobre el manual ingresante, capacitación y normativa interna.")

pregunta = st.text_input("¿Qué querés consultar?")
if pregunta:
    contexto = buscar_contexto(pregunta, corpus)
    respuesta = reformular_respuesta(contexto, pregunta)
    st.success(respuesta)

