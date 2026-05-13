from db import db
class ChatModel(db.Model):
    __tablename__ = "Chat"

    chat_id = db.Column(db.Integer, primary_key=True,nullable=False,autoincrement=True)
    question = db.Column(db.String(500))
    answer = db.Column(db.String(4000))
    chat_type = db.Column(db.String(40))
    chat_session_id = db.Column(db.Integer, db.ForeignKey("chat_session.chat_session_id"))
    time_stamp = db.Column(db.String(40))
    chatSession_rls=db.relationship("ChatSessionModel", back_populates="chat_rls")

