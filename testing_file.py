from llm_service import generate_answer

triples = [
    "user1 WORKS_AT Google",
    "user1 LIVES_IN Delhi"
]

question = "Where i live?"

answer = generate_answer(triples, question)
print(answer)