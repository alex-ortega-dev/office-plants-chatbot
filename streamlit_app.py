import streamlit as st
import openai
import os
from dotenv import load_dotenv
from plant_database import plants_database

# Cargar variables de entorno
load_dotenv()

def main():
    st.set_page_config(
        page_title="🌱 Office Plants Expert",
        page_icon="🌱",
        layout="wide"
    )
    
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
        
    # Inicializar chatbot
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = OfficePlantsChatbot()
    
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
                    response = st.session_state.chatbot.get_response(
                        user_input, 
                        st.session_state.chat_history
                    )
                
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
            recommendations = st.session_state.chatbot.get_plant_recommendations(light_level, difficulty)
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
    # Verificar que existe la API key
    if not os.getenv("OPENAI_API_KEY"):
        st.error("⚠️ Necesitas configurar tu OPENAI_API_KEY en el archivo .env")
        st.stop()
    
    main()
