from db import db
class CropModel(db.Model):
    __tablename__ = "Crop"

    crop_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    crop_name = db.Column(db.String(100),unique=True)
    season_name = db.Column(db.Integer)
    crop_image = db.Column(db.String(255))

    cultivation_rls = db.relationship("CultivationSessionModel",
                                      back_populates="crop_rls")
