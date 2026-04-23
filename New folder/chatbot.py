# chatbot_fixed.py
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import torch
from typing import Dict, List, Tuple, Optional
import re
import logging
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AgricultureChatbot:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize agriculture chatbot with local models
        """
        logger.info(f"Loading sentence transformer model: {model_name}")
        try:
            self.embedder = SentenceTransformer(model_name)
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            # Try smaller model as fallback
            logger.info("Trying smaller model...")
            self.embedder = SentenceTransformer("paraphrase-MiniLM-L3-v2")

        # Initialize data structures
        self.knowledge_base = []
        self.embeddings = None
        self.index = None

        # Agriculture keywords for quick filtering
        self.agriculture_keywords = {
            'crop', 'soil', 'farm', 'plant', 'harvest', 'irrigation', 'fertilizer',
            'pesticide', 'seed', 'cultivation', 'agriculture', 'farming', 'field',
            'wheat', 'rice', 'maize', 'corn', 'cotton', 'sugarcane', 'barley',
            'vegetable', 'fruit', 'pulse', 'legume', 'compost', 'manure',
            'watering', 'sowing', 'plough', 'tractor', 'harvester', 'yield',
            'disease', 'pest', 'weed', 'organic', 'inorganic', 'hybrid',
            'monsoon', 'rainfall', 'drought', 'flood', 'climate', 'temperature'
        }

        # Soil types
        self.soil_keywords = {
            'sandy', 'clay', 'loam', 'loamy', 'black', 'red', 'laterite',
            'alluvial', 'mountain', 'desert', 'peat', 'chalk', 'silt'
        }

        # Known crop names
        self.known_crops = {
            'wheat', 'rice', 'maize', 'corn', 'cotton', 'sugarcane',
            'barley', 'soybean', 'mustard', 'groundnut', 'sunflower',
            'paddy', 'millet', 'sorghum', 'jowar', 'bajra', 'ragi',
            'potato', 'tomato', 'onion', 'garlic', 'ginger', 'turmeric',
            'chilli', 'brinjal', 'ladyfinger', 'cauliflower', 'cabbage',
            'carrot', 'radish', 'beetroot', 'spinach', 'lettuce'
        }

        logger.info("Agriculture chatbot initialized successfully!")

    def load_knowledge_base(self, filepath: str = "data/full_dataset.json"):
        """Load Q&A pairs from generated dataset"""
        logger.info(f"Loading knowledge base from {filepath}...")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.knowledge_base = data

            # Create embeddings for all questions
            questions = [item['question'] for item in data]
            logger.info(f"Creating embeddings for {len(questions)} questions...")
            self.embeddings = self.embedder.encode(questions, show_progress_bar=True)

            # Create FAISS index for fast similarity search
            dimension = self.embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(self.embeddings.astype('float32'))

            logger.info(f"Knowledge base loaded with {len(data)} Q&A pairs")

        except FileNotFoundError:
            logger.error(f"Knowledge base file not found: {filepath}")
            logger.info("Creating a small sample knowledge base...")
            self._create_sample_knowledge_base()
        except Exception as e:
            logger.error(f"Error loading knowledge base: {e}")
            self._create_sample_knowledge_base()

    def _create_sample_knowledge_base(self):
        """Create a small sample knowledge base for testing"""
        sample_data = [
            {
                "question": "How to grow wheat?",
                "answer": "Wheat grows best in loamy soil with pH 6.0-7.5. Plant in rabi season with temperature 10-25°C. Requires moderate water (500-700mm annually). Use NPK fertilizer 120:60:40.",
                "type": "crop_general",
                "entities": ["wheat"]
            },
            {
                "question": "Best soil for rice?",
                "answer": "Rice grows best in clay or clay loam soil that can hold water. Ideal pH is 5.5-6.5. Requires high water (1200-2000mm). Plant in kharif season.",
                "type": "crop_specific",
                "entities": ["rice"]
            },
            {
                "question": "How to improve clay soil?",
                "answer": "To improve clay soil: 1. Add sand for better drainage 2. Apply gypsum 3. Deep ploughing 4. Add organic matter regularly. Clay soil has poor drainage but high nutrients.",
                "type": "soil_general",
                "entities": ["clay"]
            }
        ]

        self.knowledge_base = sample_data
        questions = [item['question'] for item in sample_data]
        self.embeddings = self.embedder.encode(questions)

        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(self.embeddings.astype('float32'))

        logger.info(f"Created sample knowledge base with {len(sample_data)} Q&A pairs")

    def is_agriculture_related(self, question: str) -> bool:
        """
        Check if question is related to agriculture using multiple methods
        Returns True if agriculture-related, False otherwise
        """
        question_lower = question.lower()

        # Method 1: Direct keyword matching
        question_words = set(question_lower.split())
        if self.agriculture_keywords.intersection(question_words):
            return True

        if self.soil_keywords.intersection(question_words):
            return True

        if self.known_crops.intersection(question_words):
            return True

        # Method 2: Pattern matching
        agriculture_patterns = [
            r'how.*(grow|plant|cultivate|farm).*',
            r'best.*(soil|fertilizer|pesticide).*',
            r'when.*(harvest|sow|plant|water).*',
            r'how.*(water|irrigate|fertilize).*',
            r'control.*(pest|disease|weed).*',
            r'what.*(crop|soil|yield).*',
            r'which.*(fertilizer|seed|variety).*',
            r'improve.*(soil|yield|growth).*',
            r'treat.*(disease|infection).*',
            r'problem.*(plant|crop|soil).*'
        ]

        for pattern in agriculture_patterns:
            if re.search(pattern, question_lower):
                return True

        # Method 3: Check for agriculture-related phrases
        agriculture_phrases = [
            'plant growth', 'crop rotation', 'soil testing', 'farm management',
            'water management', 'organic farming', 'crop yield', 'harvest time',
            'seed treatment', 'land preparation', 'drip irrigation', 'crop protection'
        ]

        for phrase in agriculture_phrases:
            if phrase in question_lower:
                return True

        return False

    def find_similar_questions(self, question: str, k: int = 5) -> List[Tuple[int, float]]:
        """
        Find similar questions using semantic search
        Returns list of (index, similarity_score) pairs
        """
        if self.index is None or len(self.knowledge_base) == 0:
            return []

        try:
            # Encode the question
            query_embedding = self.embedder.encode([question])

            # Search in FAISS index
            distances, indices = self.index.search(query_embedding.astype('float32'), k)

            # Return (index, similarity_score) pairs
            results = []
            for idx, distance in zip(indices[0], distances[0]):
                if idx < len(self.knowledge_base):  # Valid index
                    # Convert distance to similarity score (higher is better)
                    similarity = 1 / (1 + distance)
                    if similarity > 0.3:  # Only include reasonably similar results
                        results.append((int(idx), float(similarity)))

            return results

        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            return []

    def get_fallback_response(self, question: str) -> Dict[str, any]:
        """Get fallback response when no good matches found"""
        # Suggest agriculture topics
        suggestions = [
            "How to grow wheat?",
            "Best soil for rice cultivation?",
            "When to harvest maize?",
            "How to improve clay soil?",
            "Water requirements for cotton?"
        ]

        # If question seems like it might be agriculture-related but unclear
        unclear_indicators = ['grow', 'plant', 'soil', 'water', 'harvest', 'crop']
        if any(indicator in question.lower() for indicator in unclear_indicators):
            return {
                "answer": "I think you're asking about agriculture, but I'm not sure exactly what you need. Could you please be more specific? For example, mention the crop name or be more detailed about your question.",
                "confidence": 0.2,
                "source": "unclear_agriculture",
                "suggestions": random.sample(suggestions, 3)
            }

        # Generic fallback
        return {
            "answer": "I specialize only in agriculture-related topics. Please ask about crops, soil types, farming practices, irrigation methods, pest control, or harvest techniques.",
            "confidence": 0.9,
            "source": "fallback",
            "suggestions": suggestions
        }

    def generate_response(self, question: str) -> Dict[str, any]:
        """
        Generate response for a given question
        Returns dictionary with answer and metadata
        """
        # Clean and normalize question
        question = question.strip()
        if not question:
            return {
                "answer": "Please ask a question about agriculture.",
                "confidence": 1.0,
                "source": "empty_question"
            }

        logger.info(f"Processing question: {question}")

        # First check if it's agriculture-related
        is_agri = self.is_agriculture_related(question)

        if not is_agri:
            logger.info(f"Question classified as non-agriculture: {question}")
            return {
                "answer": "I specialize only in agriculture-related topics. Please ask about crops, soil types, farming practices, irrigation methods, pest control, harvest techniques, or any other agriculture subject.",
                "confidence": 0.95,
                "source": "domain_filter",
                "suggestions": [
                    "How to grow wheat?",
                    "Best soil for rice cultivation?",
                    "When to harvest maize?",
                    "How to control pests in cotton?"
                ]
            }

        logger.info(f"Question classified as agriculture-related: {question}")

        # Find similar questions
        similar = self.find_similar_questions(question)

        if not similar:
            logger.info("No similar questions found in knowledge base")
            return self.get_fallback_response(question)

        # Get the most similar question and its answer
        best_idx, confidence = similar[0]
        best_match = self.knowledge_base[best_idx]

        logger.info(f"Best match found: {best_match['question']} (confidence: {confidence:.2f})")

        # If confidence is too low, provide a cautious response
        if confidence < 0.5:
            answer = f"""Based on your question about agriculture, here's some related information:

{best_match['answer']}

Note: If this doesn't fully answer your question, please try:
1. Being more specific about the crop or soil type
2. Asking about a particular farming practice
3. Mentioning your region or climate"""
            source = "low_confidence_match"
        else:
            answer = best_match['answer']
            source = "knowledge_base_match"

        # Find related questions for suggestions
        related_suggestions = []
        for idx, sim_score in similar[1:4]:  # Next 3 similar questions
            if idx < len(self.knowledge_base) and sim_score > 0.4:
                related_suggestions.append(self.knowledge_base[idx]['question'])

        # Add some generic suggestions if needed
        if len(related_suggestions) < 3:
            generic_suggestions = [
                "How to test soil quality?",
                "Best time to plant vegetables?",
                "How to increase crop yield?"
            ]
            related_suggestions.extend(generic_suggestions[:3 - len(related_suggestions)])

        return {
            "answer": answer,
            "confidence": float(confidence),
            "source": source,
            "similar_question": best_match['question'],
            "suggestions": list(set(related_suggestions))[:3],  # Remove duplicates
            "entities": best_match.get('entities', [])
        }

    def interactive_chat(self):
        """Run interactive chat in terminal"""
        print("\n" + "=" * 60)
        print("🌾 AGRICULTURE EXPERT CHATBOT 🌱")
        print("=" * 60)
        print("Ask me anything about crops, soil, farming practices...")
        print("\nI can help with:")
        print("• Crop cultivation (wheat, rice, maize, cotton, sugarcane)")
        print("• Soil types and improvement")
        print("• Irrigation and water management")
        print("• Pest and disease control")
        print("• Harvesting and post-harvest")
        print("• Fertilizer recommendations")
        print("\nCommands:")
        print("• 'quit', 'exit', 'bye' - End chat")
        print("• 'help' - Show help")
        print("• 'examples' - Show example questions")
        print("• 'topics' - Show topics I know about")
        print("=" * 60)

        while True:
            try:
                question = input("\n👤 You: ").strip()

                if not question:
                    continue

                if question.lower() in ['quit', 'exit', 'bye', 'q']:
                    print("\n🤖 Bot: Goodbye! Happy farming! 👨‍🌾")
                    break

                if question.lower() == 'help':
                    print("\n🤖 Bot: Here's how to get the best answers:")
                    print("1. Be specific: Mention crop names (wheat, rice, etc.)")
                    print("2. Ask about specific practices: 'How to control pests in cotton?'")
                    print("3. Mention soil types if relevant: 'Best crops for clay soil?'")
                    print("4. Ask comparative questions: 'Rice vs wheat water requirements'")
                    print("\nI specialize ONLY in agriculture topics.")
                    continue

                if question.lower() == 'examples':
                    print("\n🤖 Bot: Here are example questions you can ask:")
                    print("1. How to grow wheat in clay soil?")
                    print("2. Best fertilizer for rice cultivation?")
                    print("3. How to improve sandy soil?")
                    print("4. When to harvest maize?")
                    print("5. Common diseases in cotton plants?")
                    print("6. Water requirements for sugarcane?")
                    print("7. Difference between loamy and clay soil?")
                    print("8. How to test soil quality?")
                    print("9. Organic farming methods for vegetables?")
                    print("10. Cost of cultivating wheat per acre?")
                    continue

                if question.lower() == 'topics':
                    print("\n🤖 Bot: I know about these topics:")
                    print("\n🌾 CROPS: wheat, rice, maize, cotton, sugarcane")
                    print("🌱 SOILS: sandy, clay, loamy, black")
                    print("💧 WATER: irrigation methods, water requirements")
                    print("🐛 PESTS: common pests and control methods")
                    print("🦠 DISEASES: plant diseases and prevention")
                    print("💊 FERTILIZERS: NPK recommendations, organic options")
                    print("📅 SEASONS: rabi, kharif, growing seasons")
                    print("💰 ECONOMICS: cost, yield, profit estimates")
                    print("🌿 PRACTICES: crop rotation, organic farming")
                    continue

                # Get response
                response = self.generate_response(question)

                # Print answer
                print(f"\n🤖 Bot: {response['answer']}")

                # Print confidence if low
                if response['confidence'] < 0.6:
                    print(f"\n   ⚠️  Confidence: {response['confidence']:.2%}")

                # Print suggestions if available
                if response.get('suggestions'):
                    print("\n   💡 You might also ask:")
                    for i, suggestion in enumerate(response['suggestions'], 1):
                        print(f"     {i}. {suggestion}")

                # Show what was matched (for debugging/transparency)
                if response.get('similar_question'):
                    print(f"\n   🔍 Matched to: \"{response['similar_question']}\"")

            except KeyboardInterrupt:
                print("\n\n🤖 Bot: Chat ended. Goodbye!")
                break
            except Exception as e:
                print(f"\n🤖 Bot: Error processing your question: {str(e)}")
                print("Please try again or rephrase your question.")


# Web Interface using Gradio
try:
    import gradio as gr


    def create_gradio_interface(chatbot):
        """Create Gradio web interface"""

        def respond(message, history):
            response = chatbot.generate_response(message)

            # Format the response
            formatted_response = response['answer']

            # Add confidence indicator
            if response['confidence'] < 0.6:
                formatted_response += f"\n\n⚠️ **Confidence**: {response['confidence']:.2%}"

            # Add suggestions
            if response.get('suggestions'):
                formatted_response += "\n\n💡 **Related questions you might ask:**"
                for i, suggestion in enumerate(response['suggestions'], 1):
                    formatted_response += f"\n{i}. {suggestion}"

            return formatted_response

        # Create interface
        interface = gr.ChatInterface(
            fn=respond,
            title="🌾 Agriculture Expert Chatbot 🌱",
            description="""Ask me anything about crops, soil, farming practices, irrigation, and agriculture techniques.

            **I specialize ONLY in agriculture topics.** I won't answer questions about weather, sports, movies, etc.

            Examples:
            • How to grow wheat?
            • Best soil for rice?
            • How to improve clay soil?
            • Common diseases in cotton?""",
            examples=[
                ["How to grow wheat?"],
                ["Best soil for rice cultivation?"],
                ["How to improve clay soil?"],
                ["Common diseases in cotton plants?"],
                ["Water requirements for maize?"]
            ],
            theme="soft",
            chatbot=gr.Chatbot(height=500),
            textbox=gr.Textbox(placeholder="Ask about crops, soil, farming...", container=False, scale=7),
            submit_btn="Ask 🌾",
            retry_btn="🔄 Retry",
            undo_btn="↩️ Undo",
            clear_btn="🗑️ Clear"
        )

        return interface


    HAS_GRADIO = True
except ImportError:
    HAS_GRADIO = False
    logger.warning("Gradio not installed. Web interface will not be available.")


def main():
    """Main function to run the chatbot"""
    print("\n" + "=" * 60)
    print("🌾 AGRICULTURE CHATBOT SETUP 🌱")
    print("=" * 60)

    # Initialize chatbot
    print("\nInitializing chatbot...")
    chatbot = AgricultureChatbot()

    # Load knowledge base
    dataset_files = [
        "data/full_dataset.json",
        "data/agriculture_dataset_1950.json",
        "data/test_dataset.json"
    ]

    import glob
    import os

    loaded = False
    for pattern in dataset_files:
        if "*" in pattern:
            files = glob.glob(pattern)
            if files:
                # Get the largest file
                latest_file = max(files, key=os.path.getsize)
                chatbot.load_knowledge_base(latest_file)
                loaded = True
                break
        elif os.path.exists(pattern):
            chatbot.load_knowledge_base(pattern)
            loaded = True
            break

    if not loaded:
        print("\n⚠️ No dataset file found!")
        print("Please run dataset_generator.py first to create a dataset.")
        print("Creating small sample knowledge base for now...")

    # Choose interface
    print("\n" + "=" * 60)
    print("SELECT INTERFACE")
    print("=" * 60)

    if HAS_GRADIO:
        print("1. Terminal/Command Line Interface")
        print("2. Web Browser Interface (Gradio)")
        print("\nNote: Web interface will open in your browser at http://localhost:7860")

        while True:
            choice = input("\nEnter choice (1 or 2): ").strip()
            if choice in ['1', '2']:
                break
            print("Please enter 1 or 2")

        if choice == "2":
            print("\nLaunching web interface...")
            print("The interface will open in your browser shortly.")
            print("Press Ctrl+C in this terminal to stop the server.")
            interface = create_gradio_interface(chatbot)
            interface.launch(
                server_name="127.0.0.1",
                server_port=7860,
                share=False,
                show_error=True
            )
        else:
            chatbot.interactive_chat()
    else:
        print("Gradio not installed. Using terminal interface only.")
        print("To install web interface: pip install gradio")
        chatbot.interactive_chat()


if __name__ == "__main__":
    main()