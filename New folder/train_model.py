# train_model.py
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import Trainer, TrainingArguments
import pandas as pd
from sklearn.model_selection import train_test_split
import json


class AgricultureDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)


def train_intent_classifier():
    """Fine-tune a model for agriculture intent classification"""

    # Load dataset
    with open("data/full_dataset.json", 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Prepare data
    questions = []
    labels = []

    for item in data:
        questions.append(item['question'])
        # Binary classification: 1 for agriculture, 0 for out-of-domain
        labels.append(0 if item['type'] == 'out_of_domain' else 1)

    # Split data
    train_texts, val_texts, train_labels, val_labels = train_test_split(
        questions, labels, test_size=0.2, random_state=42
    )

    # Load tokenizer and model
    model_name = "bert-base-uncased"  # or "distilbert-base-uncased" for faster training
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)

    # Tokenize data
    train_encodings = tokenizer(train_texts, truncation=True, padding=True, max_length=128)
    val_encodings = tokenizer(val_texts, truncation=True, padding=True, max_length=128)

    # Create datasets
    train_dataset = AgricultureDataset(train_encodings, train_labels)
    val_dataset = AgricultureDataset(val_encodings, val_labels)

    # Training arguments
    training_args = TrainingArguments(
        output_dir='./models/intent_classifier',
        num_train_epochs=3,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir='./logs',
        logging_steps=10,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
    )

    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
    )

    # Train
    print("Starting training...")
    trainer.train()

    # Save model
    model.save_pretrained('./models/intent_classifier_final')
    tokenizer.save_pretrained('./models/intent_classifier_final')

    print("Training completed! Model saved to ./models/intent_classifier_final")


if __name__ == "__main__":
    train_intent_classifier()