import networkx as nx

G = nx.MultiDiGraph()

def add_memory(user, relation, entity):
    G.add_node(user, type="user")      #Ensures user node exists
    G.add_node(entity, type="entity")  #Ensures entity node exists 

    # Check if same relation already exists
    for _, target, data in G.out_edges(user, data=True):
        if target == entity and data.get("relation") == relation:
            return  # Already exists, do nothing

    G.add_edge(user, entity, relation=relation)  #Connects them with a labeled edge

def query_memory(user, relation):
    results = []

    if user not in G:
        return results

    for _, target, key, data in G.out_edges(user, keys=True, data=True):
        if data.get("relation") == relation:
            results.append(target)

    return results

def get_user_relations(user):
    relations = set()

    if user not in G:
        return []

    for _, _, data in G.out_edges(user, data=True):
        relations.add(data.get("relation"))

    return list(relations)

def extract_and_store(user_id, text):
    """
    Detect supported patterns.
    If matched:
        call add_memory()
        return confirmation string
    Else:
        return None
    """