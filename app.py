import streamlit as st
from graph_memory import add_memory, query_memory, extract_and_store, get_user_subgraph
from llm_service import generate_answer
import matplotlib.pyplot as plt
import networkx as nx

import spacy
nlp = spacy.load("en_core_web_sm")

st.set_page_config(page_title="Graph RAG Chatbot")

# -----------------------
# Sidebar
# -----------------------
st.sidebar.title("Graph RAG Settings")

user_id = st.sidebar.text_input("Enter User ID", value="user_1")

if st.sidebar.button("Show Graph"):
    subgraph = get_user_subgraph(user_id)

    if len(subgraph.edges()) == 0:
        st.sidebar.write("No memory to display.")
    else:
        fig, ax = plt.subplots()
        pos = nx.spring_layout(subgraph)

        nx.draw(
            subgraph,
            pos,
            with_labels=True,
            node_color="lightblue",
            node_size=2000,
            font_size=10,
            ax=ax
        )

        edge_labels = nx.get_edge_attributes(subgraph, 'relation')
        nx.draw_networkx_edge_labels(subgraph, pos, edge_labels=edge_labels, ax=ax)

        st.pyplot(fig)

st.title("Graph RAG Chatbot")

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

        # ----------- AUTO EXTRACTION FIRST -----------
        memory_response = extract_and_store(user_id, user_input)

        if memory_response:
            st.session_state.chat_history[user_id].append({
                "role": "assistant",
                "content": memory_response
            })
            return
        # ---------------------------------------------

        question = user_input.strip().lower().rstrip("?.!")

        triples = []

        # ----------- NLP-BASED RECALL DETECTION -----------
        doc = nlp(user_input)
        
        question_word = None
        verb_lemma = None
        
        supported_verbs = {"work", "live", "study", "like"}

        for token in doc:
            if token.pos_ == "VERB" and token.lemma_.lower() in supported_verbs:
                verb_lemma = token.lemma_.lower()
        
            if token.lower_ in {"where", "what"}:
                question_word = token.text.lower()
        
        if question_word and verb_lemma:
        
            # WORK
            if verb_lemma == "work" and question_word == "where":
                memories = query_memory(user_id, "WORKS_AT")
                triples = [f"{user_id} WORKS_AT {m}" for m in memories]
        
            # LIVE
            elif verb_lemma == "live" and question_word == "where":
                memories = query_memory(user_id, "LIVES_IN")
                triples = [f"{user_id} LIVES_IN {m}" for m in memories]
        
            # STUDY LOCATION
            elif verb_lemma == "study" and question_word == "where":
                memories = query_memory(user_id, "STUDIES_AT")
                triples = [f"{user_id} STUDIES_AT {m}" for m in memories]
        
            # STUDY SUBJECT
            elif verb_lemma == "study" and question_word == "what":
                memories = query_memory(user_id, "STUDIES")
                triples = [f"{user_id} STUDIES {m}" for m in memories]
        
            # LIKES
            elif verb_lemma == "like" and question_word == "what":
                memories = query_memory(user_id, "LIKES")
                triples = [f"{user_id} LIKES {m}" for m in memories]


        # ----------- MANUAL GRAPH COMMANDS ----------
        elif user_input.startswith("remember:"):
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

            st.session_state.chat_history[user_id].append({
                "role": "assistant",
                "content": bot_response
            })
            return

        elif user_input.startswith("recall:"):
            try:
                relation = user_input.replace("recall:", "").strip()
                memories = query_memory(user_id, relation)

                triples = [f"{user_id} {relation} {m}" for m in memories]

            except:
                st.session_state.chat_history[user_id].append({
                    "role": "assistant",
                    "content": "Invalid format. Use: recall: relation"
                })
                return

        # ----------------------------------------------------------

        # ----------- LLM RESPONSE -----------
        if triples:
            bot_response = generate_answer(triples, user_input)
        else:
            bot_response = "I don't know."
        # ------------------------------------

        st.session_state.chat_history[user_id].append({
            "role": "assistant",
            "content": bot_response
        })


initialize_session()
handle_input()
display_chat()