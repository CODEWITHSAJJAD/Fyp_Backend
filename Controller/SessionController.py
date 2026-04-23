from os.path import join

from sqlalchemy import Null

from Model.ActivityModel import ActivityModel
from Model.LandModel import LandModel
from Model.PerformActivityModel import PerformedActivityModel
from  db import db
from sqlmodel import or_,and_
from flask import jsonify,request
from Model.CultivationSessionModel import CultivationSessionModel
from Model.CropModel import CropModel
from url import imageurl


class SessionController:
    @staticmethod
    def AddSession():
        try:
            data=request.get_json()
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
                    seed_name=seed,
                    session_status="Not Active",
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
    def getAllSesssionsOfLand(lid):
        try:
           rows=(db.session.query(CultivationSessionModel.cultivation_session_id,CultivationSessionModel.session_status,CultivationSessionModel.seed_name,CultivationSessionModel,CultivationSessionModel.is_profit,CultivationSessionModel.amount_per_acre,
                                  CropModel.crop_name,CropModel.crop_image,
                                       PerformedActivityModel.quantity_per_acre,PerformedActivityModel.activity_date,PerformedActivityModel.Activity_type,PerformedActivityModel.Activity_id).
                      join(CropModel,CropModel.crop_id==CultivationSessionModel.crop_id).
                      join(PerformedActivityModel,CultivationSessionModel.cultivation_session_id==PerformedActivityModel.cultivation_session_id).
                      filter(CultivationSessionModel.land_id==lid).order_by(CultivationSessionModel.cultivation_session_id.desc())).all()
           if rows:
                sessions = {}
                for r in rows:
                    sid = r.cultivation_session_id
                    if sid not in sessions:
                        sessions[sid] = {
                            "Session_id": sid,
                            "Crop": r.crop_name,
                            "Crop_image": imageurl+r.crop_image,
                            "session_status": r.session_status,
                            "seed_name": r.seed_name,
                            "Sowing_date": None,
                            "Harvesting_date": None,
                            "Production": r.quantity_per_acre,
                            "Profit": "Yes" if r.is_profit == 1 else "No",
                            "Revenue": r.amount_per_acre
                        }
                    if r.Activity_id == 2:
                        sessions[sid]["Sowing_date"] = r.activity_date
                    elif r.Activity_id == 7:
                        sessions[sid]["Harvesting_date"] = r.activity_date
                return jsonify(list(sessions.values())),200
           return jsonify("No Session Found against this land id"),404
        except Exception as e:
            return jsonify(str(e)),500

    @staticmethod
    def GetCurrentSessionOfFarmer(id):
        try:
            currentSession=((db.session.query(CultivationSessionModel.seed_name,CultivationSessionModel.cultivation_session_id,
                                              CropModel.crop_name,CropModel.crop_image,).
                            join(CropModel,CultivationSessionModel.crop_id==CropModel.crop_id).
                             filter(CultivationSessionModel.session_status!="Harvest",CultivationSessionModel.land_id==id)).
                            first())
            if currentSession:
                activitydate = PerformedActivityModel.query.filter(PerformedActivityModel.cultivation_session_id==currentSession.cultivation_session_id,PerformedActivityModel.Activity_id==2).first()
                date_value = "Not Active"
                if activitydate and activitydate.activity_date is not None:
                    date_value = activitydate.activity_date
                return jsonify({"seed_name":currentSession.seed_name,
                                "session_id":currentSession.cultivation_session_id,
                                "crop_name":currentSession.crop_name,
                                "crop_image":imageurl+currentSession.crop_image,
                                "date":date_value
                }),200
            return jsonify("No Current Session found for this land"),404
        except Exception as e:
            return jsonify(str(e)),500

    @staticmethod
    def getCurrentSessionOfFarmerLand(id):
        try:
            lid=id
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

    @staticmethod
    def getActivityListOfProfitableSessionOfFarmerLand(id):
        try:
            lid=id
            ProfitabaleCrop = (db.session.query(CultivationSessionModel.cultivation_session_id,CultivationSessionModel.is_profit, CultivationSessionModel.seed_name,
                                                CultivationSessionModel.amount_per_acre,
                                                CultivationSessionModel.production_in_tons,
                                                CultivationSessionModel.harwesting_date,
                                                CultivationSessionModel.sowing_date, CropModel.crop_name).
                               join(CropModel, CropModel.crop_id == CultivationSessionModel.crop_id).
                               filter(CultivationSessionModel.land_id == lid,
                                      CultivationSessionModel.is_profit == 1)
                               .order_by(CultivationSessionModel.production_in_tons.desc())).first()
            Activities=(db.session.query(PerformedActivityModel.Activity_type,PerformedActivityModel.activity_date,PerformedActivityModel.quantity_per_acre,ActivityModel.activity_name).
                        join(ActivityModel,ActivityModel.activity_id==PerformedActivityModel.Activity_id).
                        filter(PerformedActivityModel.cultivation_session_id==ProfitabaleCrop.cultivation_session_id)).all()

            Activity=[]
            if Activities and ProfitabaleCrop:
                for a in Activities:
                    Activity.append({
                            "Activity_name":a.activity_name,
                            "Activity_type":a.Activity_type,
                            "Activity_date":a.activity_date,
                            "Quantity_per_acre":a.quantity_per_acre,
                        })
                return jsonify({
                        "Crop":ProfitabaleCrop.crop_name,
                        "Sowing date":ProfitabaleCrop.sowing_date,
                        "Harvesting date":ProfitabaleCrop.harwesting_date,
                        "Production":ProfitabaleCrop.production_in_tons,
                        "Profit":"Yes",
                        "Revenue":ProfitabaleCrop.amount_per_acre,
                        "Seed_name":ProfitabaleCrop.seed_name,
                        "Activities":Activity
                    }),200
            return jsonify("No Activities Found against this land id"),404
        except Exception as e:
            return jsonify(str(e)),500

    @staticmethod
    def GetProfitableCropSessionOnFarmerLand(id):
        try:
            lid=id
            ProfitabaleCrop=(db.session.query(CultivationSessionModel.is_profit,CultivationSessionModel.seed_name,CultivationSessionModel.amount_per_acre,CultivationSessionModel.production_in_tons,CultivationSessionModel.harwesting_date,CultivationSessionModel.sowing_date,CropModel.crop_name).
                             join(CropModel,CropModel.crop_id == CultivationSessionModel.crop_id).
                             filter(CultivationSessionModel.land_id==lid, CultivationSessionModel.session_status=='Harvest',CultivationSessionModel.is_profit==1)
                             .order_by(CultivationSessionModel.production_in_tons.desc())).first()
            if ProfitabaleCrop:
                return jsonify({
                    "Crop_name":ProfitabaleCrop.crop_name,
                    "Seed":ProfitabaleCrop.seed_name,
                    "Profit":"Yes" if ProfitabaleCrop.is_profit==1 else "No",
                    "Revenue":ProfitabaleCrop.amount_per_acre,
                    "Production":ProfitabaleCrop.production_in_tons,
                    "Sowing date":ProfitabaleCrop.sowing_date,
                    "Harvesting date":ProfitabaleCrop.harwesting_date,
                }),200
            return jsonify("No Profitable Crops Found against this land id"),404
        except Exception as e:
            return jsonify(str(e)),500