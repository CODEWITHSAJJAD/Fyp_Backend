from db import db
class FarmerModel(db.Model):
    __tablename__ = "Farmer"

    farmer_id = db.Column(db.Integer, primary_key=True, nullable=False,autoincrement=True)
    farmer_name = db.Column(db.String(100))
    phone = db.Column(db.String(11),unique=True)
    email = db.Column(db.String(255),unique=True)
    city_id = db.Column(db.Integer, db.ForeignKey("City.city_id"))

    farmer_image = db.Column(db.String(255))
    landmark = db.Column(db.String(255))
    password = db.Column(db.String(100))
    years_of_experience = db.Column(db.String(2))

    city_rls = db.relationship("CityModel", back_populates="farmer_rls")
    land_rls = db.relationship("LandModel", back_populates="farmer_rls")
    chat_rls = db.relationship("ChatModel", back_populates="farmer_rls")

