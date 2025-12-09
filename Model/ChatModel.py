from db import db
class ChatModel(db.Model):
    __tablename__ = "Chat"

    chat_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    question = db.Column(db.String(500))
    answer = db.Column(db.String(4000))
    chat_type = db.Column(db.String(40))
    farmer_id = db.Column(db.Integer, db.ForeignKey("Farmer.farmer_id"))
    time_stamp = db.Column(db.Time)

    farmer_rls = db.relationship("FarmerModel", back_populates="chat_rls")
