from pathlib import Path
import joblib

BASE = Path(__file__).resolve().parent
INTENT_MODEL = joblib.load(BASE / 'artifacts' / 'intent_model.joblib')
TOPIC_MODEL = joblib.load(BASE / 'artifacts' / 'topic_model.joblib')

def predict(text):
    intent = str(INTENT_MODEL.predict([text])[0])
    topic = str(TOPIC_MODEL.predict([text])[0])
    intent_conf = float(max(INTENT_MODEL.predict_proba([text])[0]))
    topic_conf = float(max(TOPIC_MODEL.predict_proba([text])[0]))
    return intent, topic, intent_conf, topic_conf
