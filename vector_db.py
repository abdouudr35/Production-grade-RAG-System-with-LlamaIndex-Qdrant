from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

class QdrantStorage:
    # 1. CHANGEMENTS ICI : On remplace 'url' par 'path', on met dim=1024, et on enlève l'espace dans "docs"
    def __init__(self, path="./qdrant_storage", collection="docs", dim=1024):
        # 2. On connecte Qdrant directement au dossier local (Zéro Podman !)
        self.client = QdrantClient(path=path)
        self.collection = collection
        
        if not self.client.collection_exists(self.collection):
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
            )
            print(f"Collection '{self.collection}' créée en local !")

    def upsert(self, ids, vectors, payloads):
        points = [PointStruct(id=ids[i], vector=vectors[i], payload=payloads[i]) for i in range(len(ids))]
        self.client.upsert(self.collection, points=points)

    def search(self, query_vector, top_k: int=5): 
        # 1. On remplace .search() par .query_points()
        reponse = self.client.query_points(
            collection_name=self.collection,
            query=query_vector, # 2. L'argument s'appelle 'query' et plus 'query_vector'
            with_payload=True, 
            limit=top_k
        )
        
        contexts = []
        sources = set()

        # 3. Les résultats se trouvent maintenant dans reponse.points
        for r in reponse.points: 
            payload = getattr(r, "payload", None) or {}
            text = payload.get("text", "")
            source = payload.get("source", "")
            if text: 
                contexts.append(text)
                sources.add(source)

        return {"contexts": contexts, "sources": list(sources)}