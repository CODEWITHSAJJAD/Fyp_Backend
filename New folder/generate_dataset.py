import os
import pandas as pd
import json
import time
import requests
from tqdm import tqdm


# ============================================
# CONFIGURATION
# ============================================
OPENROUTER_API_KEY = "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"
MODEL_ID = "arcee-ai/trinity-large-preview:free"

RABI_DIR = r"d:\BackendDevelopment\New folder\uploads\crops\Rabi"
KHARIF_DIR = r"d:\BackendDevelopment\New folder\uploads\crops\Kharif"
OUTPUT_FILE = r"d:\BackendDevelopment\data\pakistan_agriculture_dataset_large.csv"

# Intents defined in s3.py
INTENTS = [
    "Cultivation", "Fertilizer", "Pesticide", "Irrigation",
    "Soil", "Yield", "Diseases", "Varieties",
    "MarketPrice", "HarvestTime", "SowingTime"
]

def get_crop_names():
    rabi_crops = [os.path.splitext(f)[0] for f in os.listdir(RABI_DIR) if f.endswith('.jpg')]
    kharif_crops = [os.path.splitext(f)[0] for f in os.listdir(KHARIF_DIR) if f.endswith('.jpg')]
    return list(set(rabi_crops + kharif_crops))

import ollama  # add this at top if not already

def query_llm(prompt):
    try:
        response = ollama.chat(
            model="llama3:8b",   # same model that worked for you
            messages=[
                {"role": "system", "content": "You are an expert agricultural scientist specialized in Pakistan farming."},
                {"role": "user", "content": prompt}
            ],
        )
        return response["message"]["content"].strip()

    except Exception as e:
        print(f"❌ Ollama Error: {e}")
        return ""


def generate_qa_pair(crop, intent):
    prompt = f"""
    You are an expert agricultural scientist specialized in Pakistan's farming.
    Task: Generate a detailed Question and Answer pair for the crop '{crop}' related to the intent '{intent}'.
    The answer should be factual, specific to Pakistan's environment, and include numbers (yields, kg/acre, months, etc.) if applicable.
    
    Format:
    Question: [A natural user question about {intent} for {crop}]
    Answer: [A 3-5 sentence detailed professional answer]
    
    Intent Descriptions:
    - Cultivation: General guide on how to grow.
    - Fertilizer: NPK requirements, urea/DAP bags per acre.
    - Pesticide: Common pests and their chemical/biological control.
    - Irrigation: Water frequency and critical stages.
    - Soil: Ideal soil type, pH, and preparation.
    - Yield: Average and potential yield per acre in Pakistan.
    - Diseases: Common diseases and their symptoms/management.
    - Varieties: Popular high-yielding or resistant varieties in Pakistan.
    - MarketPrice: How to get the best price or average market trends.
    - HarvestTime: When and how to harvest.
    - SowingTime: Ideal months for sowing in Pakistan.

    Generated Pair:
    """

    response = query_llm(prompt)

    question = ""
    answer = ""

    if "Question:" in response and "Answer:" in response:
        parts = response.split("Answer:")
        question = parts[0].replace("Question:", "").strip()
        answer = parts[1].strip()

    return question, answer

def main():
    crops = get_crop_names()
    print(f"🌾 Found {len(crops)} crops. Starting generation for {len(crops) * len(INTENTS)} pairs...")

    data = []

    # Check if directory exists
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    if not OPENROUTER_API_KEY:
        print("⚠️ OPENROUTER_API_KEY is empty. Please edit the script to add your token.")
        return

    for crop in tqdm(crops, desc="Crops"):
        for intent in INTENTS:
            q, a = generate_qa_pair(crop, intent)
            if q and a:
                data.append({
                    "crop": crop.lower(),
                    "intent": intent,
                    "question": q,
                    "answer": a,
                    "soil": "" # To be filled if applicable, but RAG uses crop/intent mostly
                })
            time.sleep(1) # Rate limiting for free tier
            
            # Save every 20 pairs to not lose progress
            if len(data) % 20 == 0:
                pd.DataFrame(data).to_csv(OUTPUT_FILE, index=False)

    df = pd.DataFrame(data)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"✅ Successfully generated {len(data)} Q&A pairs.")
    print(f"📁 Saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
