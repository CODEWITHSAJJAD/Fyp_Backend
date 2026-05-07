"""
Combine and clean all agriculture knowledge base CSV files
Normalize intents to match datasets/intents.csv
"""
import pandas as pd
import os

# Define valid intents from datasets/intents.csv
VALID_INTENTS = [
    'Cultivation', 'Fertilizer', 'Pesticide', 'Irrigation', 'Soil', 
    'Yield', 'Diseases', 'Varieties', 'MarketPrice', 'HarvestTime', 'SowingTime',
    'Greeting', 'Wassup', 'Wellness', 'AskingHelp', 'OutOfScope', 'Weather',
    'MyActivities', 'MyCrops', 'MyLands', 'MyNeighbors', 
    'CropRecommendation', 'LandRecommendation', 'ActivityRecommendation', 'ContextGathering',
    'SeedRate', 'SeedTreatment', 'LandPrep', 'WeedControl', 'Storage', 'Economics'
]

# Intent mapping for normalization
INTENT_MAPPING = {
    # Map variations to standard intents
    'Cultivation': 'Cultivation',
    'cultivation': 'Cultivation',
    'Cultivate': 'Cultivation',
    'Fertilizer': 'Fertilizer',
    'fertilizer': 'Fertilizer',
    'Fertilizers': 'Fertilizer',
    'Pesticide': 'Pesticide',
    'pesticide': 'Pesticide',
    'Pesticides': 'Pesticide',
    'Pests': 'Pesticide',
    'Irrigation': 'Irrigation',
    'irrigation': 'Irrigation',
    'Water': 'Irrigation',
    'Soil': 'Soil',
    'soil': 'Soil',
    'Yield': 'Yield',
    'yield': 'Yield',
    'Production': 'Yield',
    'Diseases': 'Diseases',
    'diseases': 'Diseases',
    'Disease': 'Diseases',
    'Varieties': 'Varieties',
    'varieties': 'Varieties',
    'Variety': 'Varieties',
    'MarketPrice': 'MarketPrice',
    'market price': 'MarketPrice',
    'Price': 'MarketPrice',
    'HarvestTime': 'HarvestTime',
    'harvest': 'HarvestTime',
    'Harvest': 'HarvestTime',
    'SowingTime': 'SowingTime',
    'sowing': 'SowingTime',
    'Sowing': 'SowingTime',
    'Planting': 'SowingTime',
    'Greeting': 'Greeting',
    'Hello': 'Greeting',
    'hello': 'Greeting',
    'Hi': 'Greeting',
    'hi': 'Greeting',
    'Wassup': 'Wassup',
    'Wellness': 'Wellness',
    'HowAreYou': 'Wellness',
    'AskingHelp': 'AskingHelp',
    'Help': 'AskingHelp',
    'help': 'AskingHelp',
    'OutOfScope': 'OutOfScope',
    'Weather': 'Weather',
    'weather': 'Weather',
    'SeedRate': 'SeedRate',
    'SeedTreatment': 'SeedTreatment',
    'LandPrep': 'LandPrep',
    'WeedControl': 'WeedControl',
    'Weeds': 'WeedControl',
    'Storage': 'Storage',
    'Economics': 'Economics',
    'Cost': 'Economics',
    'Profit': 'Economics',
    # Context-aware intents
    'MyActivities': 'MyActivities',
    'MyCrops': 'MyCrops',
    'MyLands': 'MyLands',
    'MyNeighbors': 'MyNeighbors',
    'CropRecommendation': 'CropRecommendation',
    'LandRecommendation': 'LandRecommendation',
    'ActivityRecommendation': 'ActivityRecommendation',
    'ContextGathering': 'ContextGathering',
}

def normalize_intent(intent):
    """Normalize intent to valid format"""
    if not intent or pd.isna(intent):
        return 'Cultivation'  # Default
    
    intent = str(intent).strip()
    
    # Try direct mapping
    if intent in INTENT_MAPPING:
        return INTENT_MAPPING[intent]
    
    # Try case-insensitive
    intent_lower = intent.lower()
    for key, value in INTENT_MAPPING.items():
        if key.lower() == intent_lower:
            return value
    
    # Check if it's a valid intent
    for valid in VALID_INTENTS:
        if valid.lower() == intent_lower:
            return valid
    
    # Default to Cultivation if unknown
    print(f"Warning: Unknown intent '{intent}' - mapping to Cultivation")
    return 'Cultivation'

def load_agriculture_knowledge_base():
    """Load agriculture_knowledge_base.csv"""
    print("Loading agriculture_knowledge_base.csv...")
    try:
        df = pd.read_csv('data/agriculture_knowledge_base.csv')
        print(f"  Loaded {len(df)} rows")
        
        # Select and rename columns
        df = df[['crop', 'intent', 'question', 'answer', 'soil']].copy()
        df['source'] = 'agriculture_knowledge_base'
        
        return df
    except Exception as e:
        print(f"Error loading agriculture_knowledge_base.csv: {e}")
        return pd.DataFrame()

def load_d_files():
    """Load and combine d1.csv, d2.csv, d3.csv, d4.csv"""
    combined = []
    
    for filename in ['d1.csv', 'd2.csv', 'd3.csv', 'd4.csv']:
        filepath = f'data/{filename}'
        if not os.path.exists(filepath):
            print(f"Skipping {filename} - not found")
            continue
            
        print(f"Loading {filename}...")
        try:
            # Read with different approaches
            df = pd.read_csv(filepath, on_bad_lines='skip')
            print(f"  Loaded {len(df)} rows, columns: {list(df.columns[:5])}...")
            
            # Find the relevant columns
            cols = df.columns.tolist()
            
            # Look for crop, intent, question, answer columns
            crop_col = None
            intent_col = None
            question_col = None
            answer_col = None
            
            for col in cols:
                col_lower = col.lower().strip()
                if 'crop' in col_lower and crop_col is None:
                    crop_col = col
                elif 'intent' in col_lower and intent_col is None:
                    intent_col = col
                elif 'question' in col_lower and question_col is None:
                    question_col = col
                elif 'answer' in col_lower and answer_col is None:
                    answer_col = col
            
            # Also check without " Column" suffix
            if crop_col is None:
                for col in cols:
                    if col.split(',')[0].strip().lower() == 'crop':
                        crop_col = col
                        break
            
            if crop_col and intent_col and question_col and answer_col:
                temp_df = df[[crop_col, intent_col, question_col, answer_col]].copy()
                temp_df.columns = ['crop', 'intent', 'question', 'answer']
                temp_df['soil'] = ''
                temp_df['source'] = filename
                combined.append(temp_df)
                print(f"  Extracted {len(temp_df)} rows")
            else:
                print(f"  Warning: Could not find all columns in {filename}")
                # Try first 4 columns
                if len(cols) >= 4:
                    temp_df = df.iloc[:, :4].copy()
                    temp_df.columns = ['crop', 'intent', 'question', 'answer']
                    temp_df['soil'] = ''
                    temp_df['source'] = filename
                    combined.append(temp_df)
                    print(f"  Used first 4 columns: {len(temp_df)} rows")
                    
        except Exception as e:
            print(f"  Error loading {filename}: {e}")
    
    if combined:
        return pd.concat(combined, ignore_index=True)
    return pd.DataFrame()

def clean_dataframe(df):
    """Clean and normalize the dataframe"""
    print("Cleaning data...")
    
    # Remove rows with missing essential data
    df = df.dropna(subset=['question', 'answer'])
    df = df[df['question'].str.strip() != '']
    df = df[df['answer'].str.strip() != '']
    
    # Normalize intents
    df['intent'] = df['intent'].apply(normalize_intent)
    
    # Clean crop names
    df['crop'] = df['crop'].fillna('').str.strip().str.title()
    
    # Clean questions and answers
    df['question'] = df['question'].str.strip()
    df['answer'] = df['answer'].str.strip()
    
    # Clean soil
    df['soil'] = df['soil'].fillna('').str.strip()
    
    print(f"  Cleaned dataset: {len(df)} rows")
    return df

def main():
    print("=" * 60)
    print("COMBINING AGRICULTURE KNOWLEDGE BASE FILES")
    print("=" * 60)
    
    # Load all files
    df1 = load_agriculture_knowledge_base()
    df2 = load_d_files()
    
    # Combine
    all_data = []
    if not df1.empty:
        all_data.append(df1)
    if not df2.empty:
        all_data.append(df2)
    
    if not all_data:
        print("No data found!")
        return
    
    combined_df = pd.concat(all_data, ignore_index=True)
    print(f"\nTotal combined before cleaning: {len(combined_df)} rows")
    
    # Clean
    cleaned_df = clean_dataframe(combined_df)
    
    # Show intent distribution
    print("\nIntent distribution:")
    print(cleaned_df['intent'].value_counts().head(15))
    
    # Save
    output_path = 'data/agriculture_knowledge_base_combined.csv'
    cleaned_df.to_csv(output_path, index=False)
    print(f"\n✅ Saved combined dataset to {output_path}")
    print(f"   Total rows: {len(cleaned_df)}")
    print(f"   Unique intents: {cleaned_df['intent'].nunique()}")
    print(f"   Unique crops: {cleaned_df['crop'].nunique()}")

if __name__ == "__main__":
    main()