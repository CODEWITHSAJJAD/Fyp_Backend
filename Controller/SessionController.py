from os.path import join

from Model.ActivityModel import ActivityModel
from Model.LandModel import LandModel
from Model.PerformActivityModel import PerformedActivityModel
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

    @staticmethod
    def getActivityListOfProfitableSessionOfFarmerLand():
        try:
            lid=request.form["id"]
            Activties=(db.session.query(LandModel.land_name,CultivationSessionModel.sowing_date,CultivationSessionModel.harwesting_date,CultivationSessionModel.production_in_tons,CultivationSessionModel.seed_name,CultivationSessionModel.is_profit,CultivationSessionModel.amount_per_acre,CropModel.crop_name,ActivityModel.activity_name,PerformedActivityModel.activity_date,PerformedActivityModel.Activity_type,PerformedActivityModel.quantity_per_acre).
                       join(CultivationSessionModel,CultivationSessionModel.land_id==LandModel.land_id).
                       join(CropModel, CropModel.crop_id == CultivationSessionModel.crop_id).
                       join(PerformedActivityModel,PerformedActivityModel.cultivation_session_id==CultivationSessionModel.cultivation_session_id).
                       join(ActivityModel,ActivityModel.activity_id==PerformedActivityModel.Activity_id).
                       filter(LandModel.land_id==lid).
                       order_by(CultivationSessionModel.production_in_tons)).all()

            ActivitiesList= {}
            Activity=[]
            if Activties:
                for a in Activties:
                    Activity.append({
                            "Activity_name":a.activity_name,
                            "Activity_type":a.Activity_type,
                            "Activity_date":a.activity_date,
                            "Quantity_per_acre":a.quantity_per_acre,
                        })
                    ActivitiesList[lid] = {
                        "Crop":a.crop_name,
                        "Sowing date":a.sowing_date,
                        "Harvesting date":a.harwesting_date,
                        "Production":a.production_in_tons,
                        "Profit":"Yes" if a.is_profit==1 else "No",
                        "Revenue":a.amount_per_acre,
                        "Seed_name":a.seed_name,
                        "Activities":Activity
                    }
                listOfActivities= list(ActivitiesList.values())
                return jsonify(listOfActivities),200
            return jsonify("No Activities Found against this land id"),404
        except Exception as e:
            return jsonify(str(e)),500
    # def getActivityListOfProfitableSessionOfFarmerLand():
    #     try:
    #         lid=request.form["id"]
    #         ProfitabaleCrop = (db.session.query(CultivationSessionModel.cultivation_session_id,CultivationSessionModel.is_profit, CultivationSessionModel.seed_name,
    #                                             CultivationSessionModel.amount_per_acre,
    #                                             CultivationSessionModel.production_in_tons,
    #                                             CultivationSessionModel.harwesting_date,
    #                                             CultivationSessionModel.sowing_date, CropModel.crop_name).
    #                            join(CropModel, CropModel.crop_id == CultivationSessionModel.crop_id).
    #                            filter(CultivationSessionModel.land_id == lid,
    #                                   CultivationSessionModel.is_profit == 1)
    #                            .order_by(CultivationSessionModel.production_in_tons.desc())).first()
    #         Activities=(db.session.query(PerformedActivityModel.Activity_type,PerformedActivityModel.activity_date,PerformedActivityModel.quantity_per_acre,ActivityModel.activity_name).
    #                     join(ActivityModel,ActivityModel.activity_id==PerformedActivityModel.Activity_id).
    #                     filter(PerformedActivityModel.cultivation_session_id==ProfitabaleCrop.cultivation_session_id)).all()
    #
    #         Activity=[]
    #         if Activities and ProfitabaleCrop:
    #             for a in Activities:
    #                 Activity.append({
    #                         "Activity_name":a.activity_name,
    #                         "Activity_type":a.Activity_type,
    #                         "Activity_date":a.activity_date,
    #                         "Quantity_per_acre":a.quantity_per_acre,
    #                     })
    #             return jsonify({
    #                     "Crop":ProfitabaleCrop.crop_name,
    #                     "Sowing date":ProfitabaleCrop.sowing_date,
    #                     "Harvesting date":ProfitabaleCrop.harwesting_date,
    #                     "Production":ProfitabaleCrop.production_in_tons,
    #                     "Profit":"Yes",
    #                     "Revenue":ProfitabaleCrop.amount_per_acre,
    #                     "Seed_name":ProfitabaleCrop.seed_name,
    #                     "Activities":Activity
    #                 }),200
    #         return jsonify("No Activities Found against this land id"),404
    #     except Exception as e:
    #         return jsonify(str(e)),500

    @staticmethod
    def GetProfitableCropSessionOnFarmerLand():
        try:
            lid=request.form["id"]
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