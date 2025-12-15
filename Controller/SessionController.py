from os.path import join

from Model.LandModel import LandModel
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

    @staticmethod
    def getAllSesssionsOfLand():
        try:
            lid=request.form["id"]
            Sessions=(db.session.query(CultivationSessionModel.cultivation_session_id,CultivationSessionModel.session_status,CultivationSessionModel.seed_name,CultivationSessionModel.sowing_date,CultivationSessionModel.harwesting_date,CultivationSessionModel.production_in_tons,CultivationSessionModel.is_profit,CultivationSessionModel.amount_per_acre,CropModel.crop_name).
                      join(CropModel,CropModel.crop_id==CultivationSessionModel.crop_id).filter(CultivationSessionModel.land_id==lid)).all()
            if Sessions:
                session_list=[]
                for s in Sessions:
                    if s.session_status == "Harvest":
                        session_list.append({
                            "Session_id":s.cultivation_session_id,
                            "Crop":s.crop_name,
                            "session_status":s.session_status,
                            "seed_name":s.seed_name,
                            "Sowing_date":s.sowing_date,
                            "Harvesting_date":s.harwesting_date,
                            "Production":s.production_in_tons,
                            "Profit":"Yes" if s.is_profit==1 else "No",
                            "Revenue":s.amount_per_acre
                        })
                    else:
                        session_list.append({
                            "Session_id": s.cultivation_session_id,
                            "Crop": s.crop_name,
                            "session_status": "Sown",
                            "seed_name": s.seed_name,
                            "Sowing_date": s.sowing_date,
                        })
                return jsonify(session_list),200
            return jsonify("No Session Found against this land id"),404
        except Exception as e:
            return jsonify(str(e)),500

    @staticmethod
    def getCurrentSessionOfFarmerLand():
        try:
            lid=request.form["id"]
            currenSession=(db.session.query(CultivationSessionModel.cultivation_session_id,CultivationSessionModel.session_status,CultivationSessionModel.seed_name,CultivationSessionModel.sowing_date,CultivationSessionModel.harwesting_date,CultivationSessionModel.production_in_tons,CultivationSessionModel.is_profit,CultivationSessionModel.amount_per_acre,CropModel.crop_name).
                      join(CropModel,CropModel.crop_id==CultivationSessionModel.crop_id).filter(CultivationSessionModel.land_id==lid).order_by(CultivationSessionModel.sowing_date.desc())).first()
            if currenSession:
                session_list=[]
                if currenSession.session_status == "Harvest":
                    session_list.append({
                        "Session_id":currenSession.cultivation_session_id,
                        "Crop":currenSession.crop_name,
                        "session_status":currenSession.session_status,
                        "seed_name":currenSession.seed_name,
                        "Sowing_date":currenSession.sowing_date,
                        "Harvesting_date":currenSession.harwesting_date,
                        "Production":currenSession.production_in_tons,
                        "Profit":"Yes" if currenSession.is_profit==1 else "No",
                        "Revenue":currenSession.amount_per_acre
                        })
                else:
                    session_list.append({
                        "Session_id": currenSession.cultivation_session_id,
                        "Crop": currenSession.crop_name,
                        "session_status": "Sown",
                        "seed_name": currenSession.seed_name,
                        "Sowing_date": currenSession.sowing_date,
                    })
                return jsonify(session_list),200
            return jsonify("No Session Found against this land id"),404
        except Exception as e:
            return jsonify(str(e)),500