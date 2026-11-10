import re
import unicodedata


def clean_text(text):
    if not isinstance(text, str):
        raise TypeError("Input must be a string.")

    text = unicodedata.normalize("NFKC", text)
    text = text.lower()
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"\S+@\S+", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def preprocess_documents(documents):
    if not isinstance(documents, list):
        raise TypeError("Documents must be provided as a list.")

    return [clean_text(doc) for doc in documents]