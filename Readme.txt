Graph RAG Chatbot with Auto-Updating Memory


📌 Overview
This project implements a Graph-based Retrieval-Augmented Generation (RAG) chatbot that maintains structured memory using a knowledge graph.
When a user provides new information, the system extracts structured facts and stores them in a graph database. When the user asks a question, the system retrieves relevant graph context and uses an LLM to generate a response strictly based on stored memory.
The system supports multi-user memory separation.


🏗️ Architecture
User Input
    ↓
Information Extraction (Rule-based / spaCy)
    ↓
Graph Update (NetworkX)
    ↓
Graph Retrieval
    ↓
LLM Formatting (Gemini/Groq API)
    ↓
Final Response


🛠️ Tech Stack
Python
Streamlit – Web interface
NetworkX – Knowledge graph
spaCy / Rule-based extraction – Information extraction
Gemini / Groq API – LLM response formatting
Matplotlib / Pyvis – Graph visualization


🧠 How It Works

1️⃣ Memory Addition

When the user provides structured input such as:
“I work at Brainzym”
“I like Unity”
“I study AI”

The system extracts triples in the format: (User, RELATION, Entity)

Example:
(Shivanshu, WORKS_AT, Brainzym)
(Shivanshu, LIKES, Unity)

These are stored as nodes and edges inside a NetworkX multi-directed graph.

2️⃣ Memory Retrieval

When the user asks:
“Where do I work?”
“What do I like?”

The system:
Detects intent
Maps question to relation
Queries graph
Retrieves matching triples
Sends them as context to the LLM

If no memory is found, the system responds: I don't know.
The LLM is strictly instructed to answer only using retrieved graph context.


👥 Multi-User Support

Each user has isolated memory based on a unique user_id.
Graph queries are scoped per user to prevent cross-memory leakage.


📊 10 Memory Inputs

Use this sequence:
I work at Google.
I live in Delhi.
I study at JSS Noida.
I study mathematics.
I like football.
I like machine learning.
I work at Microsoft.
I live in India.
I study physics.
I like coding.

After entering, click Show Graph to demonstrate graph visualization.


❓ 5 Query Demonstrations

Where do I work?
Where do I live?
Where do I study?
What do I study?
What do I like?


📈 Graph Visualization

The application includes a live visualization of the memory graph showing:

User nodes
Entity nodes
Relationship edges
![Graph visualization](images/graph.png)
This enables visual inspection of stored knowledge.


🚀 How to Run Locally

1. Clone Repository
git clone https://github.com/ShivanshuK12399/graph-rag-chatbot
cd Graph-RAG-Chatbot

2. Install Dependencies
pip install -r requirements.txt

3. Run Application
py -m streamlit run app.py


📁 Project Structure
Graph-RAG-Chatbot/
│
├── app.py
├── graph_memory.py
├── extraction.py
├── llm_service.py
├── requirements.txt
├── README.md
└── reflection.md


⚠️ Known Limitations

1️⃣ Limited Verb Coverage (Hard-Coded Ontology)

Your system only understands: work, live, study, like
Anything outside that is ignored.

Example failures:
I built a game.
I prefer Python.
I hate maths.
I moved to Delhi.
I completed B.Tech.

These won’t be stored.
Because you require explicit verb → relation mapping. This is a structural limitation of controlled ontology design.

2️⃣ No Memory Update / Conflict Resolution

If user says:
I work at Google.
I work at Microsoft.
I do not work at Google.

My system:
Stores Google
Stores Microsoft
Ignores negation
Never deletes old fact

There is no temporal awareness, no contradiction handling, no update logic.
Memory only grows. It never corrects itself.

3️⃣ No Temporal Context

You cannot represent:
I worked at Google in 2022.
I used to live in Mumbai.
I will study in Germany next year.

All facts are treated as permanent truth, graph memory lacks time dimension.

4️⃣ Fragile NLP Scope

spaCy extraction handles: Simple first-person declarative sentences

It does NOT handle:
Passive voice - “Google employs me.”
Indirect phrasing - “Currently employed by Google.”
Complex clauses - “Although I studied maths, I now study physics.”
Pronoun resolution - “I joined Microsoft. It’s great.”

No multi-sentence reasoning.

5️⃣ No Semantic Generalization

If user says: I enjoy football.
Your system does not map "enjoy" → LIKES.

No synonym handling.
No embedding-based similarity.

Everything depends on exact verb lemma match.

7️⃣ No Persistence (If Not Implemented)

If graph resets on restart, memory is volatile, Not real-world ready.

⚠️ NOTE - In llm_service : client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
I intentionally didn't mentioned my API key due to security reasons