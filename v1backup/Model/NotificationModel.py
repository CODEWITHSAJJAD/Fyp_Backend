from db import db

class NotificationModel(db.Model):
    __tablename__ = "Notification"
    notification_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey("Farmer.farmer_id"))
    notification_type = db.Column(db.String(50))
    title = db.Column(db.String(255))
    message = db.Column(db.Text)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.String(255))
    extra_data = db.Column(db.JSON, nullable=True)

    farmer = db.relationship("FarmerModel", back_populates="notification_rls")
