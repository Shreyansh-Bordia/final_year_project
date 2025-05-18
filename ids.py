from flask import Blueprint, render_template, request, jsonify
from flask_socketio import emit
import pandas as pd
import numpy as np
import pickle

from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
# from twilio.rest import Client
from extensions import socketio

import os
ids_bp = Blueprint('ids', __name__, template_folder='templates/ids')


df = pd.read_csv('final_year_project\KDDTrain+.csv')

# Preprocess the data
df.loc[df['Class'] == "normal", "Class"] = 'normal'
df.loc[df['Class'] != 'normal', "Class"] = 'attack'
df['Class'] = df['Class'].apply(lambda x: 0 if x == "normal" else 1)

# Separate categorical and numerical columns
categorical_columns = ['Protocol_type', 'Service', 'Flag']
numerical_columns = [col for col in df.columns if col not in categorical_columns + ['Class']]

# Apply one-hot encoding to categorical columns
encoder = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
encoded_cols = encoder.fit_transform(df[categorical_columns])
encoded_cols = pd.DataFrame(encoded_cols, columns=encoder.get_feature_names_out(categorical_columns))

# Concatenate encoded columns with numerical columns
df_encoded = pd.concat([encoded_cols, df[numerical_columns], df['Class']], axis=1)

# Split data into features and target
X = df_encoded.drop('Class', axis=1)
y = df_encoded['Class'].values

# Scale numerical features
scaler = MinMaxScaler()
encoder = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
pca = PCA(n_components=0.95)
clf = RandomForestClassifier(n_estimators=100, max_depth=3, random_state=42)

# Define function to train model
def train_model():
    global X_train, X_test, y_train, y_test, scaler, encoder, clf, pca
    
    # Scale numerical features
    X_scaled = scaler.fit_transform(X)
    
    # Apply PCA
    X_pca = pca.fit_transform(X_scaled)
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X_pca, y, test_size=0.2, random_state=42)
    
    # Train the model
    clf.fit(X_train, y_train)

# Train the model initially
train_model()

# Save the model and preprocessing objects
with open('model.pkl', 'wb') as f:
    pickle.dump(clf, f)
with open('scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)
with open('encoder.pkl', 'wb') as f:
    pickle.dump(encoder, f)
with open('pca.pkl', 'wb') as f:
    pickle.dump(pca, f)

# Twilio credentials (replace with your actual credentials)
# account_sid = ''
# auth_token = ''
# twilio_phone_number = ''
# recipient_phone_number = ''

# client = Client(account_sid, auth_token)

# def send_sms_notification(record):
#     message = client.messages.create(
#         body=f"Alert!! Someone is trying to intrude your server!",
#         from_=twilio_phone_number,
#         to=recipient_phone_number
#     )
#     print(f"Message sent: {message.sid}")

@ids_bp.route('/ids')
def index():
    return render_template('ids/index.html')

@ids_bp.route('/monitor')
def monitor():
    return render_template('monitor.html')

@ids_bp.route('/action', methods=['POST'])
def action():
    global accuracy
    action_type = request.form.get('type')
    if action_type == 'attack':
        attack_indices = np.where(y_test == 1)[0]
        random_index = np.random.choice(attack_indices, size=1, replace=False)[0]
        record = df.iloc[random_index].to_dict()
    else:
        normal_indices = np.where(y_test == 0)[0]
        random_index = np.random.choice(normal_indices, size=1, replace=False)[0]
        record = df.iloc[random_index].to_dict()

    accuracy = clf.score(X_test, y_test) * 100
    
    # Send SMS notification if attack is detected
    features = X_test[random_index].reshape(1, -1)
    prediction = clf.predict(features)[0]
    prediction_label = "attack" if prediction == 1 else "normal"
    # if prediction_label == "attack":
    #     send_sms_notification(record)
    
    result = {
        'record': record,
        'prediction': prediction_label,
        'accuracy': accuracy
    }
    
    socketio.emit('action_event', result)
    return jsonify(result)