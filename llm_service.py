from groq import Groq
import os

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def generate_answer(triples, user_question):
    """
    triples: list of strings like
        ["UserA WORKS_AT Google", "UserA LIVES_IN Delhi"]
    """

    context_block = "\n".join(triples)

    system_prompt = f"""
You are a memory assistant.

You must answer ONLY using the provided context.

Context:
{context_block}

Rules:
- Always answer in a complete natural sentence.
- Speak in second person (use "You").
- Do NOT output raw entity values alone.
- If the answer is not in the context, say exactly: I don't know.
- Do not guess.
- Do not use outside knowledge.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question}
        ],
        temperature=0
    )

    return response.choices[0].message.content.strip()