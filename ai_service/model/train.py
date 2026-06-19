import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(current_dir, 'dataset.csv')
model_path = os.path.join(current_dir, 'model.pkl')
features_path = os.path.join(current_dir, 'features.joblib')

def train_model():
    print("Loading dataset...")
    df = pd.read_csv(data_path)
    
    # Séparation Features / Target
    X = df.drop('disease', axis=1)
    y = df['disease']
    
    print(f"Training Random Forest with {len(X.columns)} features...")
    # Modèle Scikit-Learn
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X, y)
    
    print("Saving model to model.pkl...")
    joblib.dump(clf, model_path)
    
    # Save the feature names so the API knows the expected input
    joblib.dump(list(X.columns), features_path)
    
    print("Training complete!")

if __name__ == '__main__':
    train_model()
