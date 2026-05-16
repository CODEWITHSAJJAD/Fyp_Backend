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
from datetime import datetime
from Services.ActivitySuggestionService import ActivitySuggestionService
from url import imageurl


class ActivityController:

    @staticmethod
    def getListofActivities():
        try:
            Activities=ActivityModel.query.all()
            activitiesList=[]
            if Activities:
                for activity in Activities:
                    activitiesList.append({"name":activity.activity_name,"id":activity.activity_id})
                return jsonify(activitiesList),200
        except Exception as e:
            return jsonify(str(e)), 500

    @staticmethod
    def AddActivity():
        try:
            Activity_info=request.form["Activity"]
            activityJson=json.loads(Activity_info)
            existingSession= CultivationSessionModel.query.filter(CultivationSessionModel.cultivation_session_id==activityJson['cultivation_session_id'],or_(
                CultivationSessionModel.session_status != "Harvest",
                CultivationSessionModel.session_status == None
            )).first()
            if existingSession:
                ActivitySuggestionService.record_performed(session_id=activityJson['cultivation_session_id'],activity_id=activityJson['Activity_id'],performed_date_str=activityJson['activity_date'])
                if activityJson['Activity_id']==7:
                    session_info = request.form["session_info"]
                    sessionJson = json.loads(session_info)
                    newPerformedActivity = PerformedActivityModel(**activityJson)
                    db.session.add(newPerformedActivity)
                    existingSession.crop_id=existingSession.crop_id
                    existingSession.land_id=existingSession.land_id
                    existingSession.seed_name=existingSession.seed_name
                    existingSession.session_status="Harvest"
                    existingSession.is_profit=sessionJson["is_profit"]
                    existingSession.amount_per_acre=sessionJson["amount_per_acre"]
                    db.session.commit()
                    return jsonify("Activity Added"),200
                elif activityJson['Activity_id']==2:
                    newPerformedActivity = PerformedActivityModel(**activityJson)
                    db.session.add(newPerformedActivity)
                    existingSession.crop_id = existingSession.crop_id
                    existingSession.land_id = existingSession.land_id
                    existingSession.seed_name = existingSession.seed_name
                    existingSession.session_status = "Sown"
                    existingSession.is_profit =  existingSession.is_profit
                    existingSession.amount_per_acre = existingSession.amount_per_acre
                    db.session.commit()
                    return jsonify("Activity Added"), 200
                else:
                    newPerformedActivity = PerformedActivityModel(**activityJson)
                    db.session.add(newPerformedActivity)
                    db.session.commit()
                    return jsonify("Activity Added"), 200

            else:
                return jsonify("invalid Land id"),404
        except Exception as e:
            return jsonify(str(e)), 500
    @staticmethod
    def EditActivity():
        try:
            Activity_info=request.form["Activity"]
            activityJson=json.loads(Activity_info)
            existingSession= CultivationSessionModel.query.filter(CultivationSessionModel.cultivation_session_id==activityJson['cultivation_session_id']).first()
            existingActivity=PerformedActivityModel.query.filter(PerformedActivityModel.p_activity_id==activityJson['Performed_id']).first()
            if existingSession and existingActivity:
                if activityJson['Activity_id']==7:
                    session_info = request.form["session_info"]
                    sessionJson = json.loads(session_info)
                    existingActivity.p_activity_id=activityJson['Performed_id']
                    existingActivity.Activity_id=activityJson['Activity_id']
                    existingActivity.quantity_per_acre=activityJson['quantity_per_acre']
                    existingActivity.Activity_type=activityJson['Activity_type']
                    existingActivity.activity_date=activityJson['activity_date']
                    existingActivity.cultivation_session_id=activityJson['cultivation_session_id']
                    existingSession.crop_id=existingSession.crop_id
                    existingSession.land_id=existingSession.land_id
                    existingSession.seed_name=existingSession.seed_name
                    existingSession.session_status="Harvest"
                    existingSession.is_profit=sessionJson["is_profit"]
                    existingSession.amount_per_acre=sessionJson["amount_per_acre"]
                    db.session.commit()
                    return jsonify("Activity Updated"),200
                elif activityJson['Activity_id']==2:
                    existingActivity.p_activity_id = activityJson['Performed_id']
                    existingActivity.Activity_id = activityJson['Activity_id']
                    existingActivity.quantity_per_acre = activityJson['quantity_per_acre']
                    existingActivity.Activity_type = activityJson['Activity_type']
                    existingActivity.activity_date = activityJson['activity_date']
                    existingActivity.cultivation_session_id = activityJson['cultivation_session_id']
                    existingSession.crop_id = existingSession.crop_id
                    existingSession.land_id = existingSession.land_id
                    existingSession.seed_name = existingSession.seed_name
                    existingSession.session_status = "Sown"
                    existingSession.is_profit =  existingSession.is_profit
                    existingSession.amount_per_acre = existingSession.amount_per_acre
                    db.session.commit()
                    return jsonify("Activity Updated"), 200
                else:
                    existingActivity.p_activity_id = activityJson['Performed_id']
                    existingActivity.Activity_id = activityJson['Activity_id']
                    existingActivity.quantity_per_acre = activityJson['quantity_per_acre']
                    existingActivity.Activity_type = activityJson['Activity_type']
                    existingActivity.activity_date = activityJson['activity_date']
                    existingActivity.cultivation_session_id = activityJson['cultivation_session_id']
                    db.session.commit()
                    return jsonify("Activity Updated"),200
            else:
                return jsonify("invalid Land id"),404
        except Exception as e:
            return jsonify(str(e)), 500

    @staticmethod
    def getAllActivitiesOfFarmer(id):
        try:
            f_id=id
            Activities=(db.session.query(FarmerModel.farmer_name,
                                         PerformedActivityModel.Activity_id,PerformedActivityModel.Activity_type,PerformedActivityModel.activity_date,PerformedActivityModel.p_activity_id,PerformedActivityModel.quantity_per_acre,
                                         LandModel.land_name,CropModel.crop_name,CropModel.crop_image,ActivityModel.activity_name,
                                         CultivationSessionModel.cultivation_session_id).
                         join(LandModel,LandModel.farmer_id==FarmerModel.farmer_id).
                        join(CultivationSessionModel,CultivationSessionModel.land_id==LandModel.land_id).
                        join(PerformedActivityModel,PerformedActivityModel.cultivation_session_id==CultivationSessionModel.cultivation_session_id).
                        join(ActivityModel,ActivityModel.activity_id==PerformedActivityModel.Activity_id).
                        join(CropModel,CropModel.crop_id==CultivationSessionModel.crop_id).
                        filter(FarmerModel.farmer_id==f_id).order_by(PerformedActivityModel.p_activity_id.desc())).all()

            ListOfActivities=[]
            if Activities:
                for a in Activities:
                    if a.activity_name=="Harvesting":
                        Cultivationsession=CultivationSessionModel.query.filter(CultivationSessionModel.cultivation_session_id==a.cultivation_session_id).first()
                        ListOfActivities.append({
                            "session_id": a.cultivation_session_id,
                            "Performed_id": a.p_activity_id,
                            'Activity_id':a.Activity_id,
                            "Farmer": a.farmer_name,
                            "Land Name": a.land_name,
                            "Crop Name": a.crop_name,
                            "Crop Image": imageurl+a.crop_image,
                            "Activity Name": a.activity_name,
                            "Activity Type": a.Activity_type,
                            "Activity Date": a.activity_date,
                            "Quantity Per Acre": a.quantity_per_acre,
                            "is_Profit":Cultivationsession.is_profit,
                            "amount_per_acre":Cultivationsession.amount_per_acre
                        })
                    else:
                        ListOfActivities.append({
                            "session_id":a.cultivation_session_id,
                            "Performed_id":a.p_activity_id,
                            'Activity_id': a.Activity_id,
                            "Farmer":a.farmer_name,
                            "Land Name":a.land_name,
                            "Crop Name":a.crop_name,
                            "Crop Image": imageurl+a.crop_image,
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

    @staticmethod
    def getSessionPerformedActivities(id):
        try:
            performedActivities=(db.session.query(PerformedActivityModel.p_activity_id,PerformedActivityModel.activity_date,PerformedActivityModel.Activity_type,PerformedActivityModel.quantity_per_acre,
                                                  ActivityModel.activity_name).join(ActivityModel,PerformedActivityModel.Activity_id==ActivityModel.activity_id).
                                 filter(PerformedActivityModel.cultivation_session_id==id).order_by(PerformedActivityModel.p_activity_id.desc())).all()
            if performedActivities:
                activities=[]
                for p in performedActivities:
                    activities.append({
                        "Performed id":p.p_activity_id,
                        "Activity Name": p.activity_name,
                        "Activity Type": p.Activity_type,
                        "Activity Date": p.activity_date,
                        "Quantity Per Acre": p.quantity_per_acre,
                    })
                return jsonify(activities),200
            return jsonify("No Activities"),404
        except Exception as e:
            return jsonify(str(e)), 500
