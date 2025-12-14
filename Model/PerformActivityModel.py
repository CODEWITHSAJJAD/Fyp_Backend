from db import db
class PerformedActivityModel(db.Model):
    __tablename__ = "Performed_Activity"

    p_activity_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    cultivation_session_id = db.Column(db.Integer, db.ForeignKey("Cultivation_Session.cultivation_session_id"))
    Activity_id=db.Column(db.Integer, db.ForeignKey("Activity.activity_id"))
    activity_date = db.Column(db.Date)
    Activity_type=db.Column(db.String(255))
    quantity_per_acre = db.Column(db.String(20))
    activity_rls=db.relationship("ActivityModel", back_populates="per_activity_rls")
    crop_rls = db.relationship("CultivationSessionModel", back_populates="per_activity_rls")
