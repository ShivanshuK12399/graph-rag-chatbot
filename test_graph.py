from graph_memory import add_memory, query_memory, get_user_relations

add_memory("user1", "likes", "pizza")
add_memory("user1", "hates", "spinach")

print(get_user_relations("user1"))