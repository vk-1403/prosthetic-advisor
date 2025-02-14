import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
import joblib

# Load clinical rules
df = pd.read_csv('data/prosthetic_rules.csv')

# Feature engineering
encoder = LabelEncoder()
features = df[['ambulation_type', 'stability', 'risk']]
X = features.apply(encoder.fit_transform)
y = encoder.fit_transform(df['recommended_foot'])

# Train model
model = DecisionTreeClassifier(max_depth=4)
model.fit(X, y)

# Save artifacts
joblib.dump(model, 'clinical_model.joblib')
joblib.dump(encoder, 'label_encoder.joblib')
print("Model trained and saved!")
