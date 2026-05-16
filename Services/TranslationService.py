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


# import base64
# import re
# from langdetect import detect, LangDetectException
# from deep_translator import GoogleTranslator
# import warnings
#
# warnings.filterwarnings('ignore')
#
#
# class TranslationService:
#     def __init__(self):
#         # Language code mapping
#         self.LANGUAGE_MAP = {
#             'ur': 'Urdu',
#             'en': 'English',
#             'rom': 'Roman Urdu'  # Added Roman Urdu
#         }
#
#         # Supported languages for translation
#         self.SUPPORTED_LANGUAGES = ['ur', 'en']
#
#         # Common Roman Urdu patterns (for detection)
#         self.ROMAN_URDU_KEYWORDS = [
#             'aap', 'kaise', 'hai', 'kya', 'main', 'tum', 'woh', 'yeh',
#             'acha', 'theek', 'namaste', 'salam', 'khuda', 'hafiz',
#             'kitna', 'kahan', 'kab', 'kyun', 'kaun', 'kis', 'kisko',
#             'mujhe', 'tujhe', 'usne', 'humne', 'apna', 'tera', 'mera'
#         ]
#
#     def is_roman_urdu(self, text):
#         """
#         Detect if text is Roman Urdu (Urdu written in Latin script)
#         Features: Contains Urdu-specific words in Latin script,
#                  doesn't contain Urdu/Arabic characters
#         """
#         if not text or not text.strip():
#             return False
#
#         # Check if text contains Urdu/Arabic Unicode characters
#         urdu_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]')
#         if urdu_pattern.search(text):
#             return False  # Contains actual Urdu script
#
#         # Check for Roman Urdu keywords
#         words = text.lower().split()
#         roman_urdu_matches = sum(1 for word in words if word in self.ROMAN_URDU_KEYWORDS)
#
#         # If more than 2 keywords match or percentage > 20%
#         if roman_urdu_matches >= 2 or (len(words) > 0 and roman_urdu_matches / len(words) > 0.2):
#             return True
#
#         return False
#
#     def detect_language(self, text):
#         """Detect language of the given text (supports Roman Urdu)"""
#         try:
#             if not text or not text.strip():
#                 return 'en'
#
#             # First check for Roman Urdu
#             if self.is_roman_urdu(text):
#                 return 'ur'  # Roman Urdu maps to Urdu code
#
#             # Use langdetect for standard languages
#             lang_code = detect(text[:500])
#             return lang_code
#         except LangDetectException:
#             return 'en'
#
#     def get_language_name(self, lang_code):
#         """Get language name from code"""
#         if lang_code == 'rom':
#             return 'Roman Urdu'
#         return self.LANGUAGE_MAP.get(lang_code, 'Unknown')
#
#     def is_english(self, text):
#         """Check if text is primarily English"""
#         lang = self.detect_language(text)
#         return lang == 'en'
#
#     def roman_urdu_to_urdu_script(self, text):
#         """
#         Convert Roman Urdu to actual Urdu script using Google Translate
#         Google Translate handles Roman Urdu as 'ur' source language
#         """
#         if not text or not text.strip():
#             return text
#
#         try:
#             # Google Translate recognizes Roman Urdu when source is 'ur'
#             translator = GoogleTranslator(source='ur', target='ur')
#             result = translator.translate(text)
#             return result if result else text
#         except Exception as e:
#             print(f"Roman Urdu conversion error: {e}")
#             return text
#
#     def translate_to_english(self, text):
#         """Translate non-English text to English (handles Roman Urdu)"""
#         if not text or not text.strip():
#             return text
#
#         # Check if already English
#         if self.is_english(text) and not self.is_roman_urdu(text):
#             return text
#
#         try:
#             lang_code = self.detect_language(text)
#
#             if lang_code not in self.SUPPORTED_LANGUAGES:
#                 return text
#
#             # Map to Google Translate language codes
#             lang_map = {'ur': 'ur'}
#             src_lang = lang_map.get(lang_code, 'auto')
#
#             translator = GoogleTranslator(source=src_lang, target='en')
#             result = translator.translate(text)
#             return result if result else text
#         except Exception as e:
#             print(f"Translation error (to English): {e}")
#             return text
#
#     def translate_from_english(self, text, target_lang):
#         """Translate English text to target language"""
#         if not text or not text.strip():
#             return text
#
#         if target_lang == 'en':
#             return text
#
#         if target_lang not in self.SUPPORTED_LANGUAGES:
#             return text
#
#         try:
#             lang_map = {'ur': 'ur'}
#             dest_lang = lang_map.get(target_lang, 'en')
#
#             translator = GoogleTranslator(source='en', target=dest_lang)
#             result = translator.translate(text)
#             return result if result else text
#         except Exception as e:
#             print(f"Translation error (from English): {e}")
#             return text
#
#     def translate(self, text, target_lang):
#         """Translate text from English to target language"""
#         return self.translate_from_english(text, target_lang)
#
#     def process_query(self, query):
#         """
#         Process a query: detect language and translate to English
#         Returns: (english_query, original_language_code)
#         """
#         if not query or not query.strip():
#             return query, 'en'
#
#         lang_code = self.detect_language(query)
#
#         if lang_code == 'en' and not self.is_roman_urdu(query):
#             return query, 'en'
#
#         english_query = self.translate_to_english(query)
#         return english_query, lang_code
#
#     def process_response(self, response, target_lang):
#         """Translate response back to the original language"""
#         if target_lang == 'en' or not target_lang:
#             return response
#
#         return self.translate_from_english(response, target_lang)
#
#     @staticmethod
#     def decode_text(text):
#         """
#         Decode Base64 encoded text.
#         Handles both encoded and plain text.
#         """
#         if not text:
#             return text
#
#         try:
#             # Try to decode as Base64
#             decoded = base64.b64decode(text.encode('utf-8')).decode('utf-8')
#             return decoded
#         except Exception:
#             # Return as-is if not Base64 (plain text)
#             return text
#
#     @staticmethod
#     def encode_text(text):
#         """
#         Encode text to Base64.
#         Useful for storing messages in the database.
#         """
#         if not text:
#             return text
#
#         try:
#             encoded = base64.b64encode(text.encode('utf-8')).decode('utf-8')
#             return encoded
#         except Exception as e:
#             print(f"Encoding error: {e}")
#             return text
#
#     def decode_and_translate(self, encoded_text, translate_to_english=False):
#         """
#         Decode Base64 text and optionally translate to English.
#         This is useful for processing stored chat messages.
#         """
#         # Step 1: Decode from Base64
#         decoded_text = self.decode_text(encoded_text)
#
#         # Step 2: Optionally translate to English
#         if translate_to_english:
#             return self.translate_to_english(decoded_text)
#
#         return decoded_text
#
#     def encode_and_prepare_response(self, response_text, original_lang_code):
#         """
#         Translate response to original language and encode to Base64.
#         """
#         # Step 1: Translate response to original language if needed
#         translated = self.process_response(response_text, original_lang_code)
#
#         # Step 2: Encode to Base64 for storage
#         encoded = self.encode_text(translated)
#
#         return encoded, translated
#
#     def process_chat_message(self, encoded_question, target_lang='en'):
#         """
#         Complete pipeline for processing a chat message:
#         1. Decode Base64 question
#         2. Detect language (handles Roman Urdu)
#         3. Translate to English for processing
#         4. Return processed query and original language
#         """
#         # Decode the question
#         question = self.decode_text(encoded_question)
#
#         # Process query (detect language and translate to English)
#         english_query, original_lang = self.process_query(question)
#
#         return {
#             'original_question': question,
#             'encoded_question': encoded_question,
#             'english_query': english_query,
#             'original_language': original_lang,
#             'is_roman_urdu': self.is_roman_urdu(question)
#         }
#
#     def prepare_response_for_storage(self, response_text, original_lang_code):
#         """
#         Prepare response for database storage:
#         1. Translate response to original language
#         2. Encode to Base64
#         """
#         encoded_answer, translated_answer = self.encode_and_prepare_response(
#             response_text, original_lang_code
#         )
#
#         return {
#             'encoded_answer': encoded_answer,
#             'translated_answer': translated_answer,
#             'original_language': original_lang_code
#         }
#
#
#     @staticmethod
#     def decode_unicode(text):
#         """Decode base64 or return original if plain text"""
#         try:
#             return base64.b64decode(text.encode('utf-8')).decode('utf-8')
#         except:
#             return text  # Return as-is if not base64
#
#     @staticmethod
#     def encode_unicode(text):
#         """Decode base64 or return original if plain text"""
#         try:
#             return base64.b64encode(text.encode('utf-8')).decode('utf-8')
#         except:
#             return text  # Return as-is if not base64
#
#
# # Singleton instance
# _translation_service = None
#
# def get_translation_service():
#     global _translation_service
#     if _translation_service is None:
#         _translation_service = TranslationService()
#     return _translation_service