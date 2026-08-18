"""ML Classifier Evaluation Script.

Evaluates the trained report classifier and prints precision, recall, F1, and confusion matrix.
"""
import os
import joblib
from sklearn.metrics import classification_report, confusion_matrix
from ml.training.train_classifier import DATASET


def evaluate():
    model_path = os.path.join(os.path.dirname(__file__), "..", "models", "classifier.joblib")
    if not os.path.exists(model_path):
        print("Trained model artifact not found. Run train_classifier.py first.")
        return

    artifact = joblib.load(model_path)
    model = artifact["model"]
    vectorizer = artifact["vectorizer"]

    texts, y_true = zip(*DATASET)
    X = vectorizer.transform(texts)
    y_pred = model.predict(X)

    print("=== Classification Report ===")
    print(classification_report(y_true, y_pred, zero_division=0))
    print("=== Confusion Matrix ===")
    print(confusion_matrix(y_true, y_pred))


if __name__ == "__main__":
    evaluate()
