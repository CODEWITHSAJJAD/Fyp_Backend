from db import db
class CityModel(db.Model):
    __tablename__ = "City"

    city_id = db.Column(db.Integer, primary_key=True, nullable=False,autoincrement=True)
    city_name = db.Column(db.String(100), nullable=False,unique=True)

    province_id = db.Column(db.Integer, db.ForeignKey("Province.province_id"))

    province_rls = db.relationship("ProvinceModel", back_populates="city_rls")
    farmer_rls = db.relationship("FarmerModel", back_populates="city_rls")
    land_rls = db.relationship("LandModel", back_populates="city_rls")