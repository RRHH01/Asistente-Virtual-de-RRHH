# app.py
import streamlit as st
import fitz  # PyMuPDF
from fuzzywuzzy import fuzz, process
from datetime import datetime
import openai
import os

# Configurar API Key de OpenAI desde variable de entorno
openai.api_key = st.secrets["OPENAI_API_KEY"]  # Guardala en secrets.toml en Streamlit

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

# Buscar texto similar por coincidencia difusa
def buscar_respuesta(pregunta, texto):
    lineas = [line.strip() for line in texto.split("\n") if line.strip()]
    mejor, score = process.extractOne(pregunta.lower(), lineas, scorer=fuzz.partial_ratio)
    if score >= 60:
        return mejor
    return ""

# Reformular con lenguaje natural vía OpenAI
def reformular_respuesta(texto_base, pregunta):
    prompt = f"""
    Reformulá la siguiente información para que sea clara, natural y humana.
    Pregunta: {pregunta}
    Información: {texto_base}
    Respuesta:
    """
    try:
        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=250
        )
        return respuesta.choices[0].message.content.strip()
    except Exception as e:
        return f"Error al contactar OpenAI: {e}"

# Guardar historial
@st.cache_resource
def loggear(pregunta, respuesta):
    with open("chat_log.txt", "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        f.write(f"{timestamp}\n👤 {pregunta}\n🤖 {respuesta}\n\n")

# Interfaz principal
st.set_page_config(page_title="Asistente Virtual RRHH", page_icon="🧑‍💼")
st.title("👩‍💼🧑‍💼 Asistente Virtual de RRHH")
st.write("Consultá sobre el manual ingresante, capacitación y normativa interna.")

texto_admin = leer_pdf("Manual Administrativo Usina .pdf")
texto_ingreso = leer_pdf("Copia de Manual Ingresante.pdf")
texto_capac = leer_pdf("CAPACITACION 2025 .pdf")
texto_completo = "\n".join(set(texto_admin.split("\n") + texto_ingreso.split("\n") + texto_capac.split("\n")))

pregunta = st.text_input("¿Qué querés consultar?")
if pregunta:
    respuesta_base = buscar_respuesta(pregunta, texto_completo)
    if respuesta_base:
        respuesta = reformular_respuesta(respuesta_base, pregunta)
    else:
        respuesta = "No encontré una respuesta clara. Intentá con otra pregunta."    
    st.success(respuesta)
    loggear(pregunta, respuesta)

