# train_models.py
import pandas as pd
import numpy as np
import pickle
import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split
from nltk.stem.porter import PorterStemmer
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import os

print("="*60)
print("TRAINING AGRICULTURE CHATBOT MODELS")
print("="*60)

os.makedirs("saved_state", exist_ok=True)
ps = PorterStemmer()

# ============================================
# MODEL 1: INTENT CLASSIFICATION (NEURAL NETWORK)
# ============================================

print("\n[TRAINING] Intent Classification Model...")

# Load intent data
df_intent = pd.read_csv('datasets/intents.csv', names=["Query", "Intent"])
X_intent = df_intent["Query"].values
y_intent = df_intent["Intent"].values

# Preprocess queries
corpus = []
for query in X_intent:
    query = re.sub('[^a-zA-Z]', ' ', str(query))
    query = query.split()
    query = [ps.stem(word.lower()) for word in query]
    query = ' '.join(query)
    corpus.append(query)

# Create Bag of Words
cv_intent = CountVectorizer(max_features=800)
X = cv_intent.fit_transform(corpus).toarray()
print(f"   BoW shape: {X.shape}")

# Save vectorizer
pickle.dump(cv_intent, open('saved_state/IntentCountVectorizer.sav', 'wb'))
print("   [OK] Saved IntentCountVectorizer.sav")

# Encode labels
le_intent = LabelEncoder()
y = le_intent.fit_transform(y_intent)
y_categorical = to_categorical(y)

# Save label encoder
pickle.dump(le_intent, open('saved_state/intent_label_encoder.sav', 'wb'))
print("   [OK] Saved intent_label_encoder.sav")

# Save label mapping
intent_label_map = {cls: idx for idx, cls in enumerate(le_intent.classes_)}
pickle.dump(intent_label_map, open('saved_state/intent_label_map.sav', 'wb'))
print(f"   [OK] Saved intent_label_map.sav ({len(intent_label_map)} intents)")

# Train Neural Network
model = Sequential()
model.add(Dense(96, activation='relu', input_dim=X.shape[1]))
model.add(Dense(96, activation='relu'))
model.add(Dense(len(le_intent.classes_), activation='softmax'))

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
model.fit(X, y_categorical, batch_size=10, epochs=100, verbose=0)

# Save model
model.save('saved_state/intent_model.h5')
print("   [OK] Saved intent_model.h5")

# Test accuracy
y_pred = model.predict(X)
y_pred_classes = np.argmax(y_pred, axis=1)
accuracy = np.mean(y_pred_classes == y)
print(f"   [ACC] Training Accuracy: {accuracy:.2%}")

# ============================================
# MODEL 2: ENTITY EXTRACTION (NAIVE BAYES)
# ============================================

print("\n📌 Training Entity Extraction Model...")

# Load entity data
df_entity = pd.read_csv('datasets/data-tags.csv')
words = df_entity['Word'].values.astype(str)
tags = df_entity['Tag'].values.astype(str)

# Stem words
stemmed_words = []
for word in words:
    try:
        stemmed = ps.stem(word.lower())
        stemmed_words.append(stemmed)
    except:
        stemmed_words.append(word.lower())

# Create BoW for entities
cv_entity = CountVectorizer(max_features=500)
X_entity = cv_entity.fit_transform(stemmed_words).toarray()
print(f"   BoW shape: {X_entity.shape}")

# Save entity vectorizer
pickle.dump(cv_entity, open('saved_state/EntityCountVectorizer.sav', 'wb'))
print("   [OK] Saved EntityCountVectorizer.sav")

# Encode entity tags
le_entity = LabelEncoder()
y_entity = le_entity.fit_transform(tags)

# Save entity label encoder
pickle.dump(le_entity, open('saved_state/entity_label_encoder.sav', 'wb'))
print("   [OK] Saved entity_label_encoder.sav")

# Save entity label mapping
entity_label_map = {cls: idx for idx, cls in enumerate(le_entity.classes_)}
pickle.dump(entity_label_map, open('saved_state/entity_label_map.sav', 'wb'))
print(f"   [OK] Saved entity_label_map.sav ({len(entity_label_map)} entity types)")

# Train Naive Bayes classifier
nb_classifier = GaussianNB()
nb_classifier.fit(X_entity, y_entity)

# Save classifier
pickle.dump(nb_classifier, open('saved_state/entity_model.sav', 'wb'))
print("   [OK] Saved entity_model.sav")

# Test accuracy
y_pred_entity = nb_classifier.predict(X_entity)
accuracy = np.mean(y_pred_entity == y_entity)
print(f"   [ACC] Training Accuracy: {accuracy:.2%}")

print("\n" + "="*60)
print("[OK] ALL MODELS TRAINED SUCCESSFULLY!")
print("="*60)
print("\n📁 Saved files in 'saved_state' directory:")
print("   - IntentCountVectorizer.sav")
print("   - intent_label_encoder.sav")
print("   - intent_label_map.sav")
print("   - intent_model.h5")
print("   - EntityCountVectorizer.sav")
print("   - entity_label_encoder.sav")
print("   - entity_label_map.sav")
print("   - entity_model.sav")