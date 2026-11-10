from sklearn.cluster import KMeans
from ml.feature_extraction import FeatureExtractor


class DocumentClusterer:

    def __init__(self, n_clusters=3):
        self.n_clusters = n_clusters
        self.extractor = FeatureExtractor()
        self.model = KMeans(
            n_clusters=n_clusters,
            random_state=42,
            n_init=10
        )

    def cluster_documents(self, documents):

        if not documents:
            raise ValueError("Documents cannot be empty.")

        if self.n_clusters < 1 or self.n_clusters > len(documents):
            raise ValueError("Invalid number of clusters.")

        feature_matrix = self.extractor.extract_features(documents)

        labels = self.model.fit_predict(feature_matrix)

        groups = {}

        for index, label in enumerate(labels):
            groups.setdefault(int(label), []).append(documents[index])

        return groups