import json, os
from pathlib import Path
import joblib
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

BASE = Path(__file__).resolve().parent
DATA = BASE / 'data' / 'training_data.json'
ART = BASE / 'artifacts'
ART.mkdir(exist_ok=True)
rows = json.loads(DATA.read_text())
texts = [r['text'] for r in rows]
for target in ('intent','topic'):
    y=[r[target] for r in rows]
    X_train,X_test,y_train,y_test=train_test_split(texts,y,test_size=0.25,random_state=42,stratify=y)
    model=Pipeline([
      ('tfidf',TfidfVectorizer(ngram_range=(1,2),sublinear_tf=True,min_df=1)),
      ('clf',LogisticRegression(max_iter=2000,class_weight='balanced'))
    ])
    model.fit(X_train,y_train)
    pred=model.predict(X_test)
    print(target, 'accuracy:', round(accuracy_score(y_test,pred),3))
    print(classification_report(y_test,pred,zero_division=0))
    joblib.dump(model, ART/f'{target}_model.joblib')
print('trained', len(rows), 'examples')
