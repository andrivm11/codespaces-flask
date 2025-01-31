from py2neo import Graph
from app.services.text_processing import extract_entities

neo4j_graph = None

def initialize_neo4j(app):
    global neo4j_graph
    neo4j_graph = Graph(app.config['NEO4J_URI'], auth=app.config['NEO4J_AUTH'])

def update_knowledge_graph(text, doc_id):
    entities = extract_entities(text)
    
    neo4j_graph.run(
        "MERGE (d:Document {id: $doc_id})",
        doc_id=doc_id
    )
    
    for entity, label in entities:
        neo4j_graph.run(
            """
            MATCH (d:Document {id: $doc_id})
            MERGE (e:Entity {name: $name, type: $type})
            MERGE (d)-[:CONTAINS_ENTITY]->(e)
            """,
            doc_id=doc_id,
            name=entity,
            type=label
        )

def get_document_entities(doc_id):
    return neo4j_graph.run(
        """
        MATCH (d:Document {id: $doc_id})-[:CONTAINS_ENTITY]->(e:Entity)
        RETURN e.name AS name, e.type AS type
        """,
        doc_id=doc_id
    ).data()