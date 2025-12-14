from Model.CultivationSessionModel import CultivationSessionModel
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

