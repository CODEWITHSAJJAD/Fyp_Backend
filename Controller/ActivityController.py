from Model.CropModel import CropModel
from Model.CultivationSessionModel import CultivationSessionModel
from Model.FarmerModel import FarmerModel
from Model.LandModel import LandModel
from Model.PerformActivityModel import PerformedActivityModel
from db import db
from sqlalchemy import or_
from Model.ActivityModel import ActivityModel
from flask import request,jsonify
import json
class ActivityController:

    @staticmethod
    def AddActivity():
        try:
            land_id=request.form["land_id"]
            Activity_info=request.form["Activity"]
            activityJson=json.loads(Activity_info)
            activity = ActivityModel.query.filter(ActivityModel.activity_name == activityJson['Activity_id']).first()
            activity_id = activity.activity_id
            cultivation_session= CultivationSessionModel.query.filter(CultivationSessionModel.land_id==land_id,or_(
                CultivationSessionModel.session_status != "Harvest",
                CultivationSessionModel.session_status == None
            )).first()
            if cultivation_session:
                seed_name = cultivation_session.seed_name
                session_id=cultivation_session.cultivation_session_id
                if activityJson['Activity_id']=="Harvesting":
                    session_info = request.form["session_info"]
                    sessionJson = json.loads(session_info)
                    activityJson['Activity_id'] = activity_id
                    activityJson['cultivation_session_id'] = session_id
                    activityJson['quantity_per_acre'] = ""
                    newPerformedActivity = PerformedActivityModel(**activityJson)
                    db.session.add(newPerformedActivity)
                    existingSession=cultivation_session
                    existingSession.crop_id=cultivation_session.crop_id
                    existingSession.land_id=cultivation_session.land_id
                    existingSession.sowing_date=cultivation_session.sowing_date
                    existingSession.harwesting_date=activityJson['activity_date']
                    existingSession.seed_name=cultivation_session.seed_name
                    existingSession.session_status="Harvest"
                    existingSession.production_in_tons=sessionJson["production_in_tons"]
                    existingSession.is_profit=sessionJson["is_profit"]
                    existingSession.amount_per_acre=sessionJson["amount_per_acre"]
                    db.session.commit()
                    return jsonify("Activity Added"),200

                elif activityJson['Activity_id']=="Seeding":
                    activityJson['Activity_id'] = activity_id
                    activityJson['cultivation_session_id'] = session_id
                    activityJson['Activity_type']=seed_name
                    newPerformedActivity = PerformedActivityModel(**activityJson)
                    db.session.add(newPerformedActivity)
                    db.session.commit()
                    return jsonify("Activity Added"), 200

                else:
                    activityJson['Activity_id'] = activity_id
                    activityJson['cultivation_session_id'] = session_id
                    newPerformedActivity = PerformedActivityModel(**activityJson)
                    db.session.add(newPerformedActivity)
                    db.session.commit()
                    return jsonify("Activity Added"), 200

            else:
                return jsonify("invalid Land id"),404
        except Exception as e:
            return jsonify(str(e)), 500

    @staticmethod
    def getAllActivitiesOfFarmer():
        try:
            f_id=request.form["f_id"]
            Activities=(db.session.query(FarmerModel.farmer_name,PerformedActivityModel.Activity_type,PerformedActivityModel.activity_date,PerformedActivityModel.quantity_per_acre,LandModel.land_name,CropModel.crop_name,ActivityModel.activity_name).
                         join(LandModel,LandModel.farmer_id==FarmerModel.farmer_id).
                        join(CultivationSessionModel,CultivationSessionModel.land_id==LandModel.land_id).
                        join(PerformedActivityModel,PerformedActivityModel.cultivation_session_id==CultivationSessionModel.cultivation_session_id).
                        join(ActivityModel,ActivityModel.activity_id==PerformedActivityModel.Activity_id).
                        join(CropModel,CropModel.crop_id==CultivationSessionModel.crop_id).
                        filter(FarmerModel.farmer_id==f_id)).all()

            ListOfActivities=[]
            if Activities:
                for a in Activities:
                    ListOfActivities.append({
                        "Farmer":a.farmer_name,
                        "Land Name":a.land_name,
                        "Crop Name":a.crop_name,
                        "Activity Name":a.activity_name,
                        "Activity Type":a.Activity_type,
                        "Activity Date":a.activity_date,
                        "Quantity Per Acre":a.quantity_per_acre,
                    })
                return jsonify(ListOfActivities),200
            return jsonify("No Activities"),404
        except Exception as e:
            return jsonify(str(e)), 500

    @staticmethod
    def getLatestCropActivityOfFarmer():
        try:
            f_id=request.form["f_id"]
            Activities=(db.session.query(FarmerModel.farmer_name,PerformedActivityModel.Activity_type,PerformedActivityModel.activity_date,PerformedActivityModel.quantity_per_acre,LandModel.land_name,CropModel.crop_name,ActivityModel.activity_name).
                         join(LandModel,LandModel.farmer_id==FarmerModel.farmer_id).
                        join(CultivationSessionModel,CultivationSessionModel.land_id==LandModel.land_id).
                        join(PerformedActivityModel,PerformedActivityModel.cultivation_session_id==CultivationSessionModel.cultivation_session_id).
                        join(ActivityModel,ActivityModel.activity_id==PerformedActivityModel.Activity_id).
                        join(CropModel,CropModel.crop_id==CultivationSessionModel.crop_id).
                        filter(FarmerModel.farmer_id==f_id).order_by(CultivationSessionModel.sowing_date.desc())).first()

            ListOfActivities=[]
            if Activities:
                for a in Activities:
                    ListOfActivities.append({
                        "Farmer":a.farmer_name,
                        "Land Name":a.land_name,
                        "Crop Name":a.crop_name,
                        "Activity Name":a.activity_name,
                        "Activity Type":a.Activity_type,
                        "Activity Date":a.activity_date,
                        "Quantity Per Acre":a.quantity_per_acre,
                    })
                return jsonify(ListOfActivities),200
            return jsonify("No Activities"),404
        except Exception as e:
            return jsonify(str(e)), 500







