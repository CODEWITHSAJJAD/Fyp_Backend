import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
os.environ['KERAS_BACKEND'] = 'tensorflow'

# Just test import, don't run full chatbot
try:
    from Services.chatbot import AgricultureRAGChatbot
    print("Import successful!")
except Exception as e:
    print(f"Import error: {e}")


