from db import db
class ChatSessionModel(db.Model):
    __tablename__ = "chat_session"
    chat_session_id=db.Column(db.Integer, primary_key=True,nullable=False,autoincrement=True)
    Farmer_id=db.Column(db.Integer, db.ForeignKey("Farmer.farmer_id"))
    chat_rls=db.relationship("ChatModel",back_populates="chatSession_rls")
    farmer_rls = db.relationship("FarmerModel", back_populates="chatSession_rls")