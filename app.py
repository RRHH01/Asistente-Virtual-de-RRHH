import streamlit as st
import fitz  # PyMuPDF
from fuzzywuzzy import fuzz, process

# Leer y combinar texto de múltiples PDFs
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
    mejor, score = process.extractOne(pregunta.lower(), lineas, scorer=fuzz.token_sort_ratio)
    if score >= 60:
        return f"🤖 {mejor[:300]}..." if len(mejor) > 300 else f"🤖 {mejor}"
    return "❌ No encontré información relacionada."

# Título y carga
st.title("🧑‍💼 Asistente Virtual de RRHH")
st.write("Consultá sobre el manual ingresante, capacitación y normativa interna.")

# Cargar PDFs desde GitHub repo
pdfs = [
    "CAPACITACION 2025 .pdf",
    "Copia de Manual Ingresante.pdf",
    "Manual Administrativo Usina .pdf"
]

texto_total = ""
for archivo in pdfs:
    texto_total += leer_pdf(archivo) + "\n"

# Campo de pregunta
pregunta = st.text_input("¿Qué querés consultar?")
if pregunta:
    respuesta = buscar_respuesta(pregunta, texto_total)
    st.success(respuesta)
