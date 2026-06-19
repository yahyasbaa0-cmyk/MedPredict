import os
import joblib
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, 'model', 'model.pkl')
features_path = os.path.join(current_dir, 'model', 'features.joblib')

# Load Model
model = None
feature_names = []

if os.path.exists(model_path) and os.path.exists(features_path):
    model = joblib.load(model_path)
    feature_names = joblib.load(features_path)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return jsonify({"error": "Model not loaded. Please train first."}), 500
        
    data = request.json
    if not data or 'symptoms' not in data:
        return jsonify({"error": "Please provide 'symptoms' list"}), 400
        
    user_symptoms = data['symptoms']
    
    # Create input vector initialized to 0
    input_data = {feat: 0 for feat in feature_names}
    
    # Set to 1 the symptoms present in the user request
    for s in user_symptoms:
        if s in input_data:
            input_data[s] = 1
            
    df_input = pd.DataFrame([input_data])
    
    try:
        # Get probabilities for all classes
        probabilities = model.predict_proba(df_input)[0]
        classes = model.classes_
        
        # Combine and sort
        results = sorted(zip(classes, probabilities), key=lambda x: x[1], reverse=True)
        
        # Take Top 3
        top_3 = [{"disease": c, "confidence": round(p * 100, 2)} for c, p in results[:3] if p > 0]
        
        if not top_3:
            return jsonify({"predictions": [], "message": "No clear diagnosis found"}), 200
            
        return jsonify({
            "predictions": top_3,
            "disclaimer": "Outil d'aide - ne remplace pas le diagnostic médical"
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
