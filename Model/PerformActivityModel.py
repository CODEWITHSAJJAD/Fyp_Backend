from db import db
class PerformedActivityModel(db.Model):
    __tablename__ = "Performed_Activity"

    p_activity_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    crop_id = db.Column(db.Integer, db.ForeignKey("Crop.crop_id"))
    Activity_id=db.Column(db.Integer, db.ForeignKey("Activity.activity_id"))
    activity_date = db.Column(db.Date)
    quantity_per_acre = db.Column(db.String(20))
    activity_rls=db.relationship("ActivityModel", back_populates="per_activity_rls")
    crop_rls = db.relationship("CropModel", back_populates="per_activity_rls")
