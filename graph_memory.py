import networkx as nx
import spacy

nlp = spacy.load("en_core_web_sm")
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
    doc = nlp(text)

    # 🚫 Skip questions
    if doc[0].tag_ in ("WP", "WRB") or text.strip().endswith("?"):
        return None

    for token in doc:
        # Look for ROOT verb
        if token.dep_ == "ROOT" and token.pos_ == "VERB":

            # Check subject = I
            subject = None
            for child in token.children:
                if child.dep_ in ("nsubj", "nsubjpass") and child.text.lower() == "i":
                    subject = child

            if not subject:
                continue

            # Detect negation
            is_negated = any(child.dep_ == "neg" for child in token.children)
            if is_negated:
                return  # Ignore negative statements for now

            verb = token.lemma_.lower()

            # Extract object / complement
            entity = None

            for child in token.children:
            
                # Direct object
                if child.dep_ in ("dobj", "attr"):
                    entity = doc[child.left_edge.i : child.right_edge.i + 1].text
            
                # Prepositional object (work at X, live in X)
                if child.dep_ == "prep":
                    for prep_child in child.children:
                        if prep_child.dep_ == "pobj":
                            entity = doc[
                                prep_child.left_edge.i : prep_child.right_edge.i + 1
                            ].text

            if not entity:
                return

            entity = entity.rstrip(".,!?")

            # Map verb to relation
            relation = None

            if verb == "work":
                relation = "WORKS_AT"
            
            elif verb == "live":
                relation = "LIVES_IN"
            
            elif verb == "like":
                relation = "LIKES"
            
            elif verb == "study":
                # If preposition "at" exists → institution
                if any(child.dep_ == "prep" and child.text.lower() == "at" for child in token.children):
                    relation = "STUDIES_AT"
                else:
                    relation = "STUDIES"

            if relation:
                add_memory(user_id, relation, entity)
                return f"Got it. I'll remember that."

    return None

def get_user_subgraph(user_id):
    import networkx as nx

    subgraph = nx.MultiDiGraph()

    for u, v, data in G.edges(data=True):
        if u == user_id:
            subgraph.add_edge(u, v, relation=data["relation"])

    return subgraph