import streamlit as st
import fitz  # PyMuPDF
from fuzzywuzzy import fuzz, process
from datetime import datetime
import openai
import os

# Configurar la API Key desde el entorno seguro
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Leer PDF con caché
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

# Buscar la mejor coincidencia difusa
def buscar_respuesta(pregunta, texto):
    lineas = [line.strip() for line in texto.split("\n") if line.strip()]
    mejor, score = process.extractOne(pregunta.lower(), lineas, scorer=fuzz.token_sort_ratio)
    if score >= 60:
        return mejor
    return ""

# Generar respuesta con lenguaje natural
def responder_con_ia(pregunta, contexto):
    try:
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Sos un asistente de RRHH que responde en forma clara, profesional y humana basado en el siguiente contexto de documentos internos."},
                {"role": "user", "content": f"Pregunta: {pregunta}\n\nContexto:\n{contexto}"},
            ]
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Error al contactar OpenAI: {e}"

# Log de interacciones
@st.cache_data(show_spinner=False)
def loggear_chat(pregunta, respuesta):
    with open("chat_log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}]\n👤 {pregunta}\n🤖 {respuesta}\n\n")

# Cargar texto de todos los manuales
texto_admin = leer_pdf("Manual Administrativo Usina .pdf")
texto_ingresante = leer_pdf("Copia de Manual Ingresante.pdf")
texto_capacitacion = leer_pdf("CAPACITACION 2025 .pdf")
texto_completo = "\n".join(set(texto_admin.split("\n") + texto_ingresante.split("\n") + texto_capacitacion.split("\n")))

# Interfaz Streamlit
st.title("👩‍💼🧑‍💼 Asistente Virtual de RRHH")
st.write("Consultá sobre el manual ingresante, capacitación y normativa interna.")

pregunta = st.text_input("¿Qué querés consultar?")

if pregunta:
    contexto = buscar_respuesta(pregunta, texto_completo)
    respuesta = responder_con_ia(pregunta, contexto)
    st.success(respuesta)
    loggear_chat(pregunta, respuesta)

