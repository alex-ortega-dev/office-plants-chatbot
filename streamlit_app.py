import streamlit as st
import openai
import os
from plant_database import plants_database

# Configuración de la página
st.set_page_config(
    page_title="🌱 Office Plants Expert",
    page_icon="🌱",
    layout="wide"
)

# Configurar OpenAI
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Función para crear la base de conocimiento
def create_knowledge_base():
    knowledge = "BASE DE CONOCIMIENTO SOBRE PLANTAS DE OFICINA:\n\n"
    
    for plant_id, plant_info in plants_database.items():
        knowledge += f"=== {plant_info['name']} ({plant_info['scientific_name']}) ===\n"
        knowledge += f"Descripción: {plant_info['description']}\n"
        knowledge += f"Luz: {plant_info['light']}\n"
        knowledge += f"Riego: {plant_info['water']}\n"
        knowledge += f"Humedad: {plant_info['humidity']}\n"
        knowledge += f"Temperatura: {plant_info['temperature']}\n"
        knowledge += f"Toxicidad: {plant_info['toxicity']}\n"
        knowledge += f"Dificultad: {plant_info['difficulty']}/5\n"
        knowledge += "Problemas comunes:\n"
        for problem, solution in plant_info['common_problems'].items():
            knowledge += f"- {problem}: {solution}\n"
        knowledge += "\n"
    
    return knowledge

# Función para obtener respuesta del chatbot
def get_bot_response(user_question, chat_history=None):
    knowledge_base = create_knowledge_base()
    
    system_prompt = f"""
    Eres un experto en plantas de oficina especializado en ayudar a empresas a mantener sus plantas saludables.

    IMPORTANTE: Solo responde sobre las plantas que están en tu base de conocimiento. Si preguntan sobre plantas que no conoces, sugiere las alternativas más similares de tu base de datos.

    {knowledge_base}

    INSTRUCCIONES:
    1. Responde de forma práctica y profesional
    2. Si detectas un problema, da soluciones específicas paso a paso
    3. Siempre menciona el nivel de dificultad de la planta
    4. Si preguntan por recomendaciones, pregunta sobre condiciones de luz y espacio
    5. Menciona toxicidad si es relevante para oficinas
    6. Sé conciso pero completo

    EJEMPLOS DE RESPUESTAS:
    - Para diagnósticos: "Basándome en los síntomas, parece que tu [planta] tiene [problema]. Aquí está la solución..."
    - Para recomendaciones: "Para tu oficina recomiendo [planta] porque..."
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_question}
    ]
    
    # Añadir historial si existe
    if chat_history:
        for msg in chat_history[-4:]:  # Solo últimos 4 mensajes
            messages.insert(-1, msg)

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error al procesar tu consulta: {str(e)}"

# Función para recomendaciones rápidas
def get_plant_recommendations(light_level, difficulty_preference):
    recommendations = []
    
    light_mapping = {
        "baja": ["sansevieria", "zz_plant"],
        "media": ["pothos", "spathiphyllum", "dracaena"],
        "alta": ["ficus_benjamin"]
    }
    
    suitable_plants = light_mapping.get(light_level, [])
    
    for plant_id in suitable_plants:
        plant = plants_database[plant_id]
        if plant['difficulty'] <= difficulty_preference:
            recommendations.append({
                'name': plant['name'],
                'difficulty': plant['difficulty'],
                'description': plant['description']
            })
    
    return recommendations

# Interfaz principal
def main():
    # Título principal
    st.title("🌱 Office Plants Expert")
    st.subheader("Tu asistente experto en plantas de oficina")
    
    # Sidebar con información
    with st.sidebar:
        st.header("🏢 ¿Qué puedo hacer?")
        st.write("""
        • **Diagnóstico**: "Las hojas de mi pothos están amarillas"
        • **Recomendaciones**: "¿Qué planta es mejor para poca luz?"
        • **Cuidados**: "¿Cada cuánto riego mi sansevieria?"
        • **Problemas**: "Mi planta tiene manchas marrones"
        """)
        
        st.header("🌿 Plantas disponibles")
        for plant_id, plant_info in plants_database.items():
            difficulty_stars = "⭐" * plant_info['difficulty']
            st.write(f"**{plant_info['name']}** {difficulty_stars}")
        
    # Inicializar historial de chat
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Área principal del chat
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.header("💬 Hazme tu consulta")
        
        # Input del usuario
        user_input = st.text_area(
            "Pregúntame sobre tus plantas de oficina:",
            placeholder="Ej: Las hojas de mi pothos están amarillas, ¿qué puedo hacer?",
            height=100
        )
        
        if st.button("🤔 Consultar", type="primary"):
            if user_input.strip():
                # Mostrar pregunta del usuario
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                
                # Obtener respuesta
                with st.spinner("Analizando tu consulta..."):
                    response = get_bot_response(user_input, st.session_state.chat_history)
                
                # Guardar respuesta
                st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        # Mostrar historial del chat
        if st.session_state.chat_history:
            st.header("💭 Conversación")
            for i, message in enumerate(reversed(st.session_state.chat_history[-10:])):  # Últimos 10 mensajes
                if message["role"] == "user":
                    with st.chat_message("user"):
                        st.write(f"**Tú:** {message['content']}")
                else:
                    with st.chat_message("assistant"):
                        st.write(f"**Expert:** {message['content']}")
    
    with col2:
        st.header("🚀 Herramientas rápidas")
        
        # Recomendador rápido
        st.subheader("Recomendador")
        light_level = st.selectbox(
            "Nivel de luz en tu oficina:",
            ["baja", "media", "alta"]
        )
        
        difficulty = st.slider(
            "Dificultad máxima:",
            1, 5, 2,
            help="1=Muy fácil, 5=Experto"
        )
        
        if st.button("🌱 Recomendar plantas"):
            recommendations = get_plant_recommendations(light_level, difficulty)
            if recommendations:
                st.success("**Plantas recomendadas:**")
                for plant in recommendations:
                    st.write(f"• **{plant['name']}** (Dificultad: {plant['difficulty']}/5)")
                    st.write(f"  {plant['description'][:80]}...")
            else:
                st.warning("No encontré plantas que coincidan con tus criterios.")
        
        # Botón limpiar chat
        if st.button("🗑️ Limpiar conversación"):
            st.session_state.chat_history = []
            st.rerun()

if __name__ == "__main__":
    main()
