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

    if not text:
        return None

    text_stripped = text.strip()
    text_lower = text_stripped.lower()

    patterns = {
        "i work at ": ("WORKS_AT", "Got it. I’ll remember you work at {entity}."),
        "i live in ": ("LIVES_IN", "Got it. I’ll remember you live in {entity}."),
        "i study at ": ("STUDIES_AT", "Got it. I’ll remember you study at {entity}."),
        "i study ": ("STUDIES", "Got it. I’ll remember you study {entity}."),
        "i like ": ("LIKES", "Got it. I’ll remember you like {entity}."),
    }

    for prefix, (relation, message_template) in patterns.items():
        if text_lower.startswith(prefix):
            entity = text_stripped[len(prefix):].strip().rstrip(".,!?")

            if entity:
                add_memory(user_id, relation, entity)
                return message_template.format(entity=entity)

    return None

def get_user_subgraph(user_id):
    import networkx as nx

    subgraph = nx.MultiDiGraph()

    for u, v, data in G.edges(data=True):
        if u == user_id:
            subgraph.add_edge(u, v, relation=data["relation"])

    return subgraph