from typing import Any, Dict, List, Optional

from pymilvus import CollectionSchema, DataType, FieldSchema, MilvusClient


class MilvusVectorDB:
    def __init__(self, collection_name: str, uri: str, token: str) -> None:
        self.collection_name = collection_name

        self.client = MilvusClient(
            uri=uri,
            token=token
        )

        self.collection_name = collection_name

        self.init_collection()

    def init_collection(self, drop: bool = False) -> None:
        """Initialize the collection

        Args:
            drop (bool, optional): _description_. Defaults to False.
        """
        if self.client.has_collection(collection_name=self.collection_name) and drop:
            self.client.drop_collection(collection_name=self.collection_name)
        if not self.client.has_collection(self.collection_name):
            fields = [
                FieldSchema(name="id", dtype=DataType.VARCHAR,
                            is_primary=True, max_length=128),
                FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR,
                            dim=512, index="vector"),
                FieldSchema(name="metadata", dtype=DataType.JSON),
            ]
            schema = CollectionSchema(fields=fields)
            self.client.create_collection(
                collection_name=self.collection_name, schema=schema)

    def insert_vector(
        self,
        key: str,
        vector: List[float],
        metadata: Dict[str, Any]
    ) -> None:
        data = {
            "id": key,
            "vector": vector,
            "metadata": metadata
        }
        self.client.insert(self.collection_name, data)

    def search_by_vector(
        self, query_vector: List[float], top_k: int = 10
    ) -> Optional[List[Dict[str, Any]]]:
        search_params = {"metric_type": "cosine", "params": {}}
        results = self.client.search(
            collection_name=self.collection_name,
            data=[query_vector],
            anns_field="vector",
            #             param=search_params,
            limit=top_k,
        )
        return results if results else None

    def search_by_id(self, vector_id: str) -> Optional[Dict[str, Any]]:
        collections = self.client.list_collections()
        print(collections)
        results = self.client.query(
            self.collection_name,
            ids=[vector_id],
            output_fields=["id", "vector"]
        )
        # print({"results":results, "vector_id":vector_id})

        return results[0] if results else None

    def delete_vector(self, vector_id: str) -> None:
        self.client.delete(self.collection_name, [vector_id])
