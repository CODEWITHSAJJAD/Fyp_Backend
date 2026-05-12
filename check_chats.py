import base64
from sqlalchemy import create_engine, text
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

engine = create_engine('mssql+pyodbc://sa:123456@DESKTOP-2GIJV0P\\SUQOON/fyp_ORM1?driver=ODBC+Driver+17+for+SQL+Server')

def decode_base64(text):
    try:
        return base64.b64decode(text.encode('utf-8')).decode('utf-8')
    except:
        return text

with engine.connect() as conn:
    result = conn.execute(text("SELECT TOP 15 chat_id, question, answer, chat_type, time_stamp, chat_session_id FROM Chat ORDER BY time_stamp DESC"))
    print('=== RECENT CHATS (Latest First) ===\n')
    for row in result:
        q = decode_base64(row[1]) if row[1] else ''
        a = decode_base64(row[2]) if row[2] else ''
        print(f'Q: {q}')
        try:
            print(f'A: {a[:200]}...')
        except:
            print(f'A: (binary data)')
        print(f'Intent: {row[3]} | Session: {row[5]} | Time: {row[4]}')
        print('-' * 80)