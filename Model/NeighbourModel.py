from db import db
class NeighbourModel(db.Model):
    __tablename__ = "Neighbour"

    neighbour_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey("Farmer.farmer_id"))
    farmer_neighbour_id = db.Column(db.Integer, db.ForeignKey("Farmer.farmer_id"))
    land_id = db.Column(db.Integer, db.ForeignKey("Land.land_id"))

    land_rls = db.relationship("LandModel", back_populates="neighbour_rls")