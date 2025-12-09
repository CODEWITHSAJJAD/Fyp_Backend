from db import db
class CultivationSessionModel(db.Model):
    __tablename__ = "Cultivation_Session"

    cultivation_session_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    crop_id = db.Column(db.Integer, db.ForeignKey("Crop.crop_id"))
    land_id = db.Column(db.Integer, db.ForeignKey("Land.land_id"))

    sowing_date = db.Column(db.Date)
    harwesting_date = db.Column(db.Date)
    seed_name = db.Column(db.String(100))
    session_status = db.Column(db.String(100))
    production_in_tons = db.Column(db.String(100))
    is_profit = db.Column(db.Integer)
    amount_per_acre = db.Column(db.String(20))

    land_rls = db.relationship("LandModel", back_populates="cultivation_rls")
    crop_rls = db.relationship("CropModel", back_populates="cultivation_rls")
