from db import db
class ProvinceModel(db.Model):
    __tablename__ = "Province"

    province_id = db.Column(db.Integer, primary_key=True, nullable=False,autoincrement=True)
    province_name = db.Column(db.String(100), nullable=False,unique=True)

    city_rls = db.relationship("CityModel", back_populates="province_rls")
