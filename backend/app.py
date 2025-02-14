from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import os
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Configuration
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'prosthetic_model.joblib')
ENCODER_PATH = os.path.join(os.path.dirname(__file__), 'label_encoder.joblib')

# Initialize ML components
model = None
label_encoder = None

# Load ML artifacts with proper error handling
try:
    model = joblib.load(MODEL_PATH)
    print("✅ ML model loaded successfully")
except Exception as e:
    print(f"❌ Model loading failed: {str(e)}")
    model = None

try:
    label_encoder = joblib.load(ENCODER_PATH)
    print("✅ Label encoder loaded successfully")
except Exception as e:
    print(f"❌ Encoder loading failed: {str(e)}")
    label_encoder = None

def rule_based_recommendation(data):
    """Fallback recommendation system"""
    ambulation = data.get('ambulation', 'single-speed')
    stability = data.get('stability', 'stable')
    risk = data.get('risk', 'low')

    if ambulation == 'variable-speed':
        return {'recommendation': 'ESAR Foot', 'confidence': 0.85}
    
    if stability in ['moderate', 'unstable']:
        return {'recommendation': 'Single-Axis Foot', 'confidence': 0.80}
    
    if risk == 'high':
        return {'recommendation': 'ESAR Foot', 'confidence': 0.75}
    
    return {'recommendation': 'SACH Foot', 'confidence': 0.70}

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        
        # Validate input
        required_fields = ['ambulation', 'stability', 'risk']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        # Try ML prediction first
        if model and label_encoder:
            # Prepare input DataFrame
            input_df = pd.DataFrame([{
                'ambulation': data['ambulation'],
                'stability': data['stability'],
                'risk': data['risk']
            }])
            
            # Encode features
            encoded_input = input_df.apply(lambda col: label_encoder.transform(col))
            
            # Make prediction
            prediction = model.predict(encoded_input)
            confidence = model.predict_proba(encoded_input).max()
            
            return jsonify({
                'recommendation': prediction[0],
                'confidence': float(confidence),
                'source': 'ML Model'
            })
        
        # Fallback to rule-based system
        return jsonify({**rule_based_recommendation(data), 'source': 'Rule-Based'})

    except Exception as e:
        app.logger.error(f"Prediction error: {str(e)}")
        return jsonify({
            'error': str(e),
            'recommendation': 'ESAR Foot',
            'confidence': 0.65,
            'source': 'Fallback'
        }), 500

@app.route('/collect-data', methods=['POST'])
def collect_data():
    try:
        data = request.json
        timestamp = datetime.now().isoformat()
        
        # Anonymize data
        log_entry = {
            'timestamp': timestamp,
            'ambulation': data.get('ambulation'),
            'stability': data.get('stability'),
            'risk': data.get('risk'),
            'recommendation': data.get('recommendation'),
            'source': data.get('source', 'unknown')
        }
        
        # Save to CSV
        with open('training_data.csv', 'a') as f:
            f.write(f"{log_entry}\n")
            
        return jsonify({'status': 'success'})
    
    except Exception as e:
        app.logger.error(f"Data collection error: {str(e)}")
        return jsonify({'status': 'failed'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
