from ml.semantic_memory import SemanticMemory
from ml.clustering import DocumentClusterer
from ml.evaluation import evaluate_clustering
from ml.preprocessing import preprocess_documents


class StudyMindPipeline:

    def __init__(self, n_clusters=3):
        self.memory = SemanticMemory()
        self.clusterer = DocumentClusterer(n_clusters)
        self.n_clusters = n_clusters

    def process_documents(self, documents):

        if len(documents) <= self.n_clusters:
            raise ValueError(
                "Number of documents must be greater than number of clusters."
            )

        # Group related documents
        groups = self.clusterer.cluster_documents(documents)

        # Store documents in memory
        self.memory.add_documents(documents)

        # Evaluate clustering performance
        features = self.clusterer.extractor.vectorizer.transform(
            preprocess_documents(documents)
        )

        labels = self.clusterer.model.labels_

        evaluation = evaluate_clustering(features, labels)

        return {
            "total_documents": len(documents),
            "groups": groups,
            "evaluation": evaluation
        }

    def ask(self, query, top_k=3):
        return self.memory.search(query, top_k)