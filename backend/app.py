from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import numpy as np

app = Flask(__name__)
CORS(app)

# Load ML artifacts
model = joblib.load('clinical_model.joblib')
encoder = joblib.load('label_encoder.joblib')

EVIDENCE_BASE = {
    "ESAR": [
        "25-40% lower peak forces (Hafner et al.)",
        "15-20% faster walking speeds (Geertzen et al.)",
        "12-18% better energy efficiency (Hofstad et al.)"
    ],
    "Single-Axis": [
        "30% reduced knee buckling risk (Highsmith et al.)",
        "Improved weight acceptance stability",
        "18-22% lower hip moments"
    ],
    "SACH": [
        "Cost-effective solution",
        "Suitable for basic ambulation",
        "Low maintenance design"
    ]
}

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        
        # Prepare input
        input_data = pd.DataFrame([{
            'ambulation_type': data['ambulation'],
            'stability': data['stability'],
            'risk': data['risk']
        }])
        
        # Encode features
        encoded = input_data.apply(lambda col: encoder.transform(col))
        
        # Predict
        prediction = model.predict(encoded)
        confidence = model.predict_proba(encoded).max()
        
        foot_type = encoder.inverse_transform(prediction)[0]
        
        return jsonify({
            'recommendation': foot_type,
            'confidence': float(confidence),
            'evidence': EVIDENCE_BASE[foot_type],
            'clinical_rules': get_clinical_rules(data)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_clinical_rules(data):
    rules = []
    if data['ambulation'] == 'variable-speed':
        rules.append("ESAR recommended for community ambulation (Clinical Guideline #4)")
    if data['risk'] in ['high', 'moderate']:
        rules.append("ESAR reduces overuse injury risk (Guideline #2)")
    return rules

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
