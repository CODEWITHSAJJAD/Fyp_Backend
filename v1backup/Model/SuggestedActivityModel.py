from db import db

class SuggestedActivityModel(db.Model):
    __tablename__ = "Suggested_Activity"
    suggested_activity_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cultivation_session_id = db.Column(db.Integer, db.ForeignKey("Cultivation_Session.cultivation_session_id"), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey("Activity.activity_id"), nullable=False)
    days_from_sowing = db.Column(db.Integer, nullable=False)
    suggested_date = db.Column(db.String(255), nullable=False)
    priority = db.Column(db.String(20), default="medium")
    status = db.Column(db.String(20), default="pending")
    weather_delay_reason = db.Column(db.String(255))

    cultivation_session = db.relationship("CultivationSessionModel", back_populates="suggested_activities")
