from db import db
class ActivityModel(db.Model):
    __tablename__ = "Activity"
    activity_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    activity_name = db.Column(db.String(100),unique=True)
    per_activity_rls=db.relationship("PerformedActivityModel", back_populates="activity_rls")