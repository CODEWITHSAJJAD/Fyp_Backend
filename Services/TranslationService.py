"""
Translation Service for Kisan Guide Chatbot
Supports: Urdu, Punjabi, Sindhi, Pashto <-> English
"""
import base64

from langdetect import detect, LangDetectException
from deep_translator import GoogleTranslator
import warnings
warnings.filterwarnings('ignore')

class TranslationService:
    def __init__(self):
        # Language code mapping
        self.LANGUAGE_MAP = {
            'ur': 'Urdu',
            'en': 'English'
        }
        
        # Supported languages for translation
        self.SUPPORTED_LANGUAGES = ['ur','en']
    
    def detect_language(self, text):
        """Detect language of the given text"""
        try:
            if not text or not text.strip():
                return 'en'
            lang_code = detect(text[:100])
            return lang_code
        except LangDetectException:
            return 'en'
    
    def get_language_name(self, lang_code):
        """Get language name from code"""
        return self.LANGUAGE_MAP.get(lang_code, 'Unknown')
    
    def is_english(self, text):
        """Check if text is primarily English"""
        lang = self.detect_language(text)
        return lang == 'en'
    
    def translate_to_english(self, text):
        """Translate non-English text to English"""
        if not text or not text.strip():
            return text
            
        # Check if already English
        if self.is_english(text):
            return text
        
        try:
            lang_code = self.detect_language(text)
            if lang_code not in self.SUPPORTED_LANGUAGES:
                return text  # Return original if language not supported
            
            # Map to Google Translate language codes
            lang_map = {'ur': 'ur',}
            src_lang = lang_map.get(lang_code, 'auto')
            
            translator = GoogleTranslator(source=src_lang, target='en')
            result = translator.translate(text)
            return result if result else text
        except Exception as e:
            print(f"Translation error (to English): {e}")
            return text
    
    def translate_from_english(self, text, target_lang):
        """Translate English text to target language"""
        if not text or not text.strip():
            return text
        
        # If target is English, return as is
        if target_lang == 'en':
            return text
        
        if target_lang not in self.SUPPORTED_LANGUAGES:
            return text  # Return original if language not supported
            
        try:
            # Map to Google Translate language codes
            lang_map = {'ur': 'ur'}
            dest_lang = lang_map.get(target_lang, 'en')
            
            translator = GoogleTranslator(source='en', target=dest_lang)
            result = translator.translate(text)
            return result if result else text
        except Exception as e:
            print(f"Translation error (from English): {e}")
            return text
    
    def translate(self, text, target_lang):
        """Translate text from English to target language"""
        return self.translate_from_english(text, target_lang)
    
    def process_query(self, query):
        """
        Process a query: detect language and translate to English
        Returns: (english_query, original_language_code)
        """
        if not query or not query.strip():
            return query, 'en'
        
        lang_code = self.detect_language(query)
        
        if lang_code == 'en':
            return query, 'en'
        
        # Translate to English
        english_query = self.translate_to_english(query)
        return english_query, lang_code
    
    def process_response(self, response, target_lang):
        """Translate response back to the original language"""
        if target_lang == 'en' or not target_lang:
            return response
        
        return self.translate_from_english(response, target_lang)

    @staticmethod
    def decode_unicode(text):
        """Decode base64 or return original if plain text"""
        try:
            return base64.b64decode(text.encode('utf-8')).decode('utf-8')
        except:
            return text  # Return as-is if not base64

    @staticmethod
    def encode_unicode(text):
        """Decode base64 or return original if plain text"""
        try:
            return base64.b64encode(text.encode('utf-8')).decode('utf-8')
        except:
            return text  # Return as-is if not base64


# Singleton instance
_translation_service = None

def get_translation_service():
    global _translation_service
    if _translation_service is None:
        _translation_service = TranslationService()
    return _translation_service