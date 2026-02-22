import streamlit as st
from graph_memory import add_memory, query_memory

st.set_page_config(page_title="Graph RAG Chatbot")

# -----------------------
# Sidebar
# -----------------------
st.sidebar.title("Graph RAG Settings")

user_id = st.sidebar.text_input("Enter User ID", value="user_1")

st.sidebar.markdown("---")
st.sidebar.markdown("Stage 1: UI Skeleton Only")

st.title("Graph RAG Chatbot - Stage 1")

# -----------------------
# Initialize Session
# -----------------------
def initialize_session():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = {}

    if user_id not in st.session_state.chat_history:
        st.session_state.chat_history[user_id] = []

# -----------------------
# Display Chat
# -----------------------
def display_chat():
    for message in st.session_state.chat_history[user_id]:
        with st.chat_message(message["role"]):
            st.write(message["content"])

# -----------------------
# Handle Input
# -----------------------
def handle_input():
    user_input = st.chat_input("Type your message...")

    if user_input:
        # Store user message
        st.session_state.chat_history[user_id].append({
            "role": "user",
            "content": user_input
        })

        # ---------------- GRAPH MEMORY LOGIC ---------------- #

        if user_input.startswith("remember:"):
            try:
                data = user_input.replace("remember:", "").strip()
                parts = data.split(" ")

                if len(parts) < 2:
                    raise ValueError

                relation = parts[0]
                entity = " ".join(parts[1:])

                add_memory(user_id, relation, entity)
                bot_response = "Memory stored."

            except:
                bot_response = "Invalid format. Use: remember: relation entity"

        elif user_input.startswith("recall:"):
            try:
                relation = user_input.replace("recall:", "").strip()
                memories = query_memory(user_id, relation)

                if memories:
                    bot_response = ", ".join(memories)
                else:
                    bot_response = "No memory found."

            except:
                bot_response = "Invalid format. Use: recall: relation"

        else:
            bot_response = "Use 'remember:' to store and 'recall:' to retrieve."

        # ----------------------------------------------------- #

        st.session_state.chat_history[user_id].append({
            "role": "assistant",
            "content": bot_response
        })


initialize_session()
handle_input()
display_chat()