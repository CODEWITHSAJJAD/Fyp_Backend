from flask import request, jsonify
from sqlalchemy import or_, and_

from Model.ActivityModel import ActivityModel
from Model.CityModel import CityModel
from Model.PerformActivityModel import PerformedActivityModel
from db import db
from Model.FarmerModel import FarmerModel
from Model.LandModel import LandModel
from Model.CropModel import CropModel
from Model.CityModel import CityModel
from Model.CultivationSessionModel import CultivationSessionModel
from url import imageurl


class TaskContoller:
    @staticmethod
    def SearchFarmer():
        data = request.get_json()
        fid = data['fid']
        name = data['name']
        try:
            Lands = (db.session.query(FarmerModel.farmer_name, FarmerModel.farmer_image, FarmerModel.phone,
                                           LandModel.land_name, LandModel.land_id, LandModel.source_of_water,
                                           LandModel.landmark,CityModel.city_name,
                                           CultivationSessionModel.cultivation_session_id, CropModel.crop_name,
                                           CropModel.crop_image).
                          join(LandModel, FarmerModel.farmer_id == LandModel.farmer_id).
                          join(CultivationSessionModel, LandModel.land_id == CultivationSessionModel.land_id).
                          join(CropModel, CultivationSessionModel.crop_id == CropModel.crop_id).
            join(CityModel,CityModel.city_id==LandModel.city_id).
                          filter(FarmerModel.farmer_name == name,FarmerModel.farmer_id!=fid).order_by(
                CultivationSessionModel.cultivation_session_id.desc())).all()
            FarmerLands = {}
            if Lands:
                for land in Lands:
                    FarmerLands[land.land_id] = {
                            "Farmer_Name": land.farmer_name,
                            "Farmer_Image": imageurl+land.farmer_image,
                            "Phone": land.phone,
                            "Land_id": land.land_id,
                            "Land_Name": land.land_name,
                            "Source_Of_Water": land.source_of_water,
                            "LandMark": land.landmark,
                            "Crop_Name": land.crop_name,
                            "Crop_Image": imageurl+land.crop_image,
                            "Session_id": land.cultivation_session_id,
                            "city_name": land.city_name,
                        }
                FarmerLands = list(FarmerLands.values())
                return jsonify(FarmerLands), 200
            return jsonify({'message': 'Land not found'}), 404
        except Exception as e:
            return jsonify(str(e)), 500

    @staticmethod
    def ActivityCount():
        data=request.get_json()
        lid=data['id']
        a_id=data['a_id']
        date=['date']
        try:
            City=LandModel.query.filter(LandModel.land_id==lid).first()
            c_id=City.city_id
            count=(db.session.query(
                                LandModel.land_id, LandModel.land_name,CityModel.city_name,CultivationSessionModel.cultivation_session_id,
                                    PerformedActivityModel.Activity_id,PerformedActivityModel.activity_date).
                   join(CultivationSessionModel,CultivationSessionModel.land_id==LandModel.land_id).
                   join(PerformedActivityModel, PerformedActivityModel.cultivation_session_id == CultivationSessionModel.cultivation_session_id).
            join(CityModel,CityModel.city_id==LandModel.city_id).
                   filter(LandModel.city_id==c_id,PerformedActivityModel.Activity_id==a_id,PerformedActivityModel.activity_date.like(f"%{date}%"))
                   ).all()
            countofactivities = len(count)
            return jsonify(countofactivities), 200
        except Exception as e:
            return jsonify(str(e)), 500