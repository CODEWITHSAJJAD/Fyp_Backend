from db import db
class NeighbourModel(db.Model):
    __tablename__ = "Neighbour"

    neighbour_id = db.Column(db.Integer, primary_key=True,nullable=False,autoincrement=True)
    land_id = db.Column(db.Integer, db.ForeignKey("Land.land_id"))
    neighbour_land_id = db.Column(db.Integer, db.ForeignKey("Land.land_id"))
    status = db.Column(db.Integer)
    land = db.relationship("LandModel", foreign_keys=[land_id], back_populates="neighbour_rls")
    neighbour_land = db.relationship("LandModel", foreign_keys=[neighbour_land_id])
