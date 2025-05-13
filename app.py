from openai import OpenAI

# Inicializar cliente OpenAI
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Generar respuesta usando chat completions
def responder_llm(pregunta: str, contexto: str) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Respondé de manera clara y profesional, usando un lenguaje humano y fácil de entender."},
                {"role": "user", "content": f"{pregunta}\n\nContexto:\n{contexto}"}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Error al contactar OpenAI: {str(e)}"
