from os.path import join

from  db import db
from sqlmodel import or_
from flask import jsonify,request
from Model.CultivationSessionModel import CultivationSessionModel
from Model.CropModel import CropModel
class SessionController:
    @staticmethod
    def AddSession():
        try:
            data=request.get_json()
            date=data["date"]
            seed=data["seed"]
            land_id=data["land_id"]
            crop_id=data["crop_id"]
            existingSession=CultivationSessionModel.query.filter(CultivationSessionModel.land_id==land_id,or_(
            CultivationSessionModel.session_status != "Harvest",
            CultivationSessionModel.session_status == None
        )).all()
            if not existingSession:
                newSession=CultivationSessionModel(
                    crop_id=crop_id,
                    land_id=land_id,
                    sowing_date=date,
                    seed_name=seed,
                    session_status=None,
                    harwesting_date=None,
                    production_in_tons=None,
                    is_profit=None,
                    amount_per_acre=None
                )
                db.session.add(newSession)
                db.session.commit()
                return jsonify("Seesion Added"),200
            return jsonify("Seesion Not Allowed because one is icomplete"),404
        except Exception as e:
            return jsonify(str(e)),500
