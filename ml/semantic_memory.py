from sklearn.metrics.pairwise import cosine_similarity
from ml.feature_extraction import FeatureExtractor


class SemanticMemory:

    def __init__(self):
        self.extractor = FeatureExtractor()
        self.documents = []
        self.feature_matrix = None

    def add_documents(self, documents):
        """Store unique documents and generate their numerical representations."""

        if not documents:
            raise ValueError("Documents cannot be empty.")

        for document in documents:
            if not isinstance(document, str) or not document.strip():
                raise ValueError("Every document must be a non-empty string.")

            if document not in self.documents:
                self.documents.append(document)

        self.feature_matrix = self.extractor.extract_features(
            self.documents
        )

        return len(self.documents)

    def search(self, query, top_k=3):
        """Find the most similar stored documents."""

        if self.feature_matrix is None:
            raise ValueError("No documents stored yet.")

        if not isinstance(query, str) or not query.strip():
            raise ValueError("Query cannot be empty.")

        if not isinstance(top_k, int) or top_k < 1:
            raise ValueError("top_k must be a positive integer.")

        query_vector = self.extractor.transform([query])

        similarities = cosine_similarity(
            query_vector,
            self.feature_matrix
        ).flatten()

        ranked_indices = similarities.argsort()[::-1][:top_k]

        results = []

        for index in ranked_indices:
            results.append({
                "document": self.documents[index],
                "similarity": round(float(similarities[index]), 4)
            })

        return results
    