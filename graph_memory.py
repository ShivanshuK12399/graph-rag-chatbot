import networkx as nx
import spacy


nlp = spacy.load("en_core_web_sm") #Loads small English NLP model
G = nx.MultiDiGraph() #Loads directed multi-graph, have direction and allows multiple different relations between same nodes


# Store a fact in the graph.
def add_memory(user, relation, entity):
    G.add_node(user, type="user")      #Ensures user node exists
    G.add_node(entity, type="entity")  #Ensures entity node exists 

    # Check if same relation already exists
    #format of each item: (source_node, target_node, edge_attributes_dict)
    for _, target, data in G.out_edges(user, data=True):  #("user_1", "Google", {"relation": "WORKS_AT"})
        if target == entity and data.get("relation") == relation:
            return  # Already exists, do nothing

    G.add_edge(user, entity, relation=relation)  #Connects them with a labeled edge



# Retrieves stored facts
def query_memory(user, relation):
    results = []

    #If user doesn’t exist → return empty list.
    if user not in G:  
        return results
    
    #format of each item: (source, target, key, data_dict)
    #key is uniqueID of graph Without keys, you could lose access to multiple edges between same nodes.
    for _, target, key, data in G.out_edges(user, keys=True, data=True):  #("user_1", "Google", 0, {"relation": "WORKS_AT"})
        if data.get("relation") == relation:
            results.append(target)

    return results



# Returns all unique relation types a user has.
def get_user_relations(user):
    relations = set() #creates an empty set

    # If user not in graph → return empty list.
    if user not in G:
        return []

    # Collect the "relation" value from each edge.
    for _, _, data in G.out_edges(user, data=True):
        relations.add(data.get("relation"))

    # Convert set to list before returning
    return list(relations)



# reads sentence and decides whether to store something in graph.
def extract_and_store(user_id, text):
    doc = nlp(text) #spaCy analyzes grammar: subject, verb, object, etc

    # skip questions, only store statements
    # token.tag_ → detailed POS tag (WRB, Wp, PRP, etc)
    # means if the sentence starts with a WH-question word skip storing
    if doc[0].tag_ in ("WP", "WRB") or text.strip().endswith("?"): #Wp->(what, who), WRB->(where, when, why, how)
        return None

    for token in doc:
        # token.dep_ (dependency tree)-> Look for ROOT verb(main head of sentence): “I work at Google” → ROOT = work
        # token.pos_ (part of speec)  -> part of speech (VERB, NOUN, etc.)
        # ensures ROOT must be a verb
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



# Create a smaller graph containing only that user’s memories.
def get_user_subgraph(user_id):
    subgraph = nx.MultiDiGraph()

    # Loop through all edges in main graph G.
    for u, v, data in G.edges(data=True):
        if u == user_id:  
            #Copies only edges where u == user_id
            subgraph.add_edge(u, v, relation=data["relation"])

    return subgraph