from sklearn.metrics import silhouette_score


def evaluate_clustering(feature_matrix, labels):

    unique_labels = set(labels)

    if len(unique_labels) < 2:
        raise ValueError("At least two clusters are required.")

    if len(unique_labels) >= feature_matrix.shape[0]:
        raise ValueError("Each cluster must contain multiple samples.")

    score = silhouette_score(feature_matrix, labels)

    return {
        "silhouette_score": round(float(score), 4)
    }