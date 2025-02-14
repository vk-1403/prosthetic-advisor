from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import os
import numpy as np

app = Flask(__name__)
CORS(app)

# Configuration
MODEL_NAME = 'clinical_model.joblib'
ENCODER_NAME = 'label_encoder.joblib'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Initialize ML artifacts
model = None
encoder = None

try:
    model = joblib.load(os.path.join(BASE_DIR, MODEL_NAME))
    encoder = joblib.load(os.path.join(BASE_DIR, ENCODER_NAME))
    print("✅ ML artifacts loaded successfully!")
except Exception as e:
    print(f"❌ Error loading ML artifacts: {str(e)}")
    model = None
    encoder = None

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
        if not model or not encoder:
            raise RuntimeError("ML system not initialized")

        data = request.json
        
        # Validate input structure
        required_fields = ['ambulation', 'stability', 'risk']
        if not all(field in data for field in required_fields):
            return jsonify({
                'error': f'Missing required fields. Required: {required_fields}',
                'received': list(data.keys())
            }), 400

        # Create input DataFrame
        input_df = pd.DataFrame([{
            'ambulation_type': str(data['ambulation']),
            'stability': str(data['stability']),
            'risk': str(data['risk'])
        }])

        # Feature encoding
        encoded_data = input_df.apply(lambda col: encoder.transform(col))

        # Make prediction
        prediction = model.predict(encoded_data)
        probabilities = model.predict_proba(encoded_data)
        confidence = np.max(probabilities)
        
        foot_type = encoder.inverse_transform(prediction)[0]

        return jsonify({
            'recommendation': foot_type,
            'confidence': round(float(confidence), 2),
            'evidence': EVIDENCE_BASE.get(foot_type, []),
            'clinical_rules': get_clinical_rules(data),
            'status': 'success'
        })

    except Exception as e:
        return jsonify({
            'error': str(e),
            'recommendation': 'ESAR Foot',
            'confidence': 0.65,
            'evidence': EVIDENCE_BASE['ESAR'],
            'clinical_rules': ["Fallback to default recommendation"],
            'status': 'partial'
        }), 500

def get_clinical_rules(input_data):
    rules = []
    
    # Ambulation-based rules
    if input_data['ambulation'] == 'variable-speed':
        rules.append("ESAR recommended for variable cadence (K2-K4 users)")
    
    # Risk-based rules
    if input_data['risk'] in ['high', 'moderate']:
        rules.append("High stability component required (Protocol 2.3)")
    
    # Stability rules
    if input_data['stability'] == 'poor':
        rules.append("Consider torque-absorbing components (Ref: Gait Study 2022)")
    
    return rules

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
