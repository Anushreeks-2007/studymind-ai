from sklearn.feature_extraction.text import TfidfVectorizer
from ml.preprocessing import preprocess_documents


class FeatureExtractor:

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 2),
            stop_words="english"
        )
        self.is_fitted = False

    def extract_features(self, documents):
        """Clean documents and convert them into TF-IDF features."""

        if not documents:
            raise ValueError("Documents cannot be empty.")

        cleaned_documents = preprocess_documents(documents)

        feature_matrix = self.vectorizer.fit_transform(
            cleaned_documents
        )

        self.is_fitted = True
        return feature_matrix

    def transform(self, documents):
        """Convert new documents using the already-trained vectorizer."""

        if not self.is_fitted:
            raise ValueError("Feature extractor has not been fitted.")

        cleaned_documents = preprocess_documents(documents)

        return self.vectorizer.transform(cleaned_documents)

    def get_feature_names(self):
        if not self.is_fitted:
            raise ValueError("Feature extractor has not been fitted.")

        return self.vectorizer.get_feature_names_out()