from flask import request,jsonify
from datetime import datetime
from Model.ChatModel import ChatModel
from Model.ChatSessionModel import ChatSessionModel
from db import db
from Services.TranslationService import get_translation_service

class ChatController:

    @staticmethod
    def get_chatbot():
        """Get singleton chatbot instance from chatbot.py"""
        from Services.chatbot import get_chatbot
        return get_chatbot(use_llm=False)

    @staticmethod
    def chat():
        data = request.get_json()
        try:
            session = ChatSessionModel.query.filter(ChatSessionModel.chat_session_id == data['chat_session_id']).first()
            Farmer_id = session.Farmer_id
            session_id = session.chat_session_id
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data['time_stamp'] = current_time
            chatbot = ChatController.get_chatbot()

            obj = get_translation_service()
            query, lang = obj.process_query(data['question'])
            response = chatbot.generate_response(query, farmer_id=Farmer_id, session_id=session_id)
            required_response = obj.process_response(response['answer'], lang)
            encoded_answer = obj.encode_unicode(required_response)
            encoded_question=obj.encode_unicode(data['question'])
            answer = encoded_answer
            intent = response['intent']
            data['answer'] = answer
            data['chat_type'] = intent
            if data['question']:
                data['question']=encoded_question
                newchat = ChatModel(**data)
                db.session.add(newchat)
                db.session.commit()
                return jsonify({'id': newchat.chat_id,
                                'session_id': newchat.chat_session_id,
                                'question': obj.decode_unicode(encoded_question),
                                'answer': obj.decode_unicode(encoded_answer),
                                'chat_type': intent,
                                'time': newchat.time_stamp,
                                'farmer': Farmer_id}), 200
        except Exception as e:
            return jsonify(str(e)), 500

    @staticmethod
    def getChatBySession(id):
        obj = get_translation_service()
        chat_session_id=id
        try:
            chats=(db.session.query(ChatModel.chat_type,ChatModel.question,ChatModel.answer,ChatModel.time_stamp,ChatSessionModel.Farmer_id,ChatSessionModel.chat_session_id,ChatModel.chat_id).join(ChatModel,ChatSessionModel.chat_session_id==ChatModel.chat_session_id).filter(ChatSessionModel.chat_session_id==chat_session_id)).all()
            chatlist=[]
            if chats:
                for c in chats:
                    chatlist.append({
                        'id':c.chat_id,
                        'session_id':c.chat_session_id,
                        'question': obj.decode_unicode(c.question),
                        'answer': obj.decode_unicode(c.answer),
                        'chat_type':c.chat_type,
                        'time':c.time_stamp,
                        'farmer':c.Farmer_id
                    })
                return jsonify(chatlist),200
            return ("No Chats found"),404
        except Exception as e:
            return jsonify(str(e)),500

    @staticmethod
    def getChats(id):
        obj = get_translation_service()
        Farmer_id = id
        try:
            chats = (db.session.query(ChatModel.chat_type, ChatModel.question, ChatModel.answer, ChatModel.time_stamp,
                                      ChatSessionModel.Farmer_id, ChatSessionModel.chat_session_id,
                                      ChatModel.chat_id).join(ChatModel,
                                                              ChatSessionModel.chat_session_id == ChatModel.chat_session_id).filter(
                ChatSessionModel.Farmer_id == Farmer_id).order_by(ChatModel.time_stamp.desc())).all()
            ChatList = {}
            if chats:
                for c in chats:
                    if c.chat_session_id not in ChatList:
                        ChatList[c.chat_session_id] = {
                            'id': c.chat_id,
                            'session_id': c.chat_session_id,
                            'question': obj.decode_unicode(c.question),
                            'answer': obj.decode_unicode(c.answer),
                            'chat_type': c.chat_type,
                            'time': c.time_stamp,
                            'farmer': c.Farmer_id
                        }
                ChatList=list(ChatList.values())
                return jsonify(ChatList), 200
            return ("No Chats found"), 404
        except Exception as e:
            return jsonify(str(e)), 500

    @staticmethod
    def createSession():
        data=request.get_json()
        try:
            newsession=ChatSessionModel(**data)
            db.session.add(newsession)
            db.session.commit()
            return jsonify({"session_id":newsession.chat_session_id}),200
        except Exception as e:
            return jsonify(str(e)),500