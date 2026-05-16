from Model.NeighbourModel import NeighbourModel
from db import db
class LandModel(db.Model):
    __tablename__ = "Land"

    land_id = db.Column(db.Integer, primary_key=True, nullable=False,autoincrement=True)
    land_name = db.Column(db.String(100))
    years_of_cultivation = db.Column(db.String(2))
    soil_type = db.Column(db.String(100))
    source_of_water = db.Column(db.String(100))
    land_in_acres = db.Column(db.String(10))
    landmark = db.Column(db.String(255))
    land_Status=db.Column(db.Integer)
    city_id = db.Column(db.Integer, db.ForeignKey("City.city_id"))
    farmer_id = db.Column(db.Integer, db.ForeignKey("Farmer.farmer_id"))

    city_rls = db.relationship("CityModel", back_populates="land_rls")
    farmer_rls = db.relationship("FarmerModel", back_populates="land_rls")
    cultivation_rls = db.relationship("CultivationSessionModel",back_populates="land_rls")
    neighbour_rls = db.relationship("NeighbourModel",foreign_keys=[NeighbourModel.land_id],back_populates="land")