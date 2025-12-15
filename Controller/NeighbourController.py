from flask import request, jsonify
from sqlmodel import or_

from Model.ActivityModel import ActivityModel
from Model.CityModel import CityModel
from Model.CropModel import CropModel
from Model.CultivationSessionModel import CultivationSessionModel
from Model.PerformActivityModel import PerformedActivityModel
from db import db
import json
from Model.LandModel import LandModel
from Model.FarmerModel import FarmerModel
from Model.NeighbourModel import NeighbourModel

class NeighbourController:
    @staticmethod
    def AddNeighbour():
        try:
            lid = request.form['id']
            neighbour = json.loads(request.form['neighbour'])
            neighbour_name = neighbour['name']
            neighbour_number = neighbour['number']
            exp=neighbour['exp']
            yearsOfCultivation=neighbour['yearsOfCultivation']
            WaterSource=neighbour['WaterSource']
            LandInAcrs=neighbour['LandInAcrs']

            land = LandModel.query.filter(LandModel.land_id==lid).first()
            if not land:
                return jsonify("Invalid land id"), 404

            city_id = land.city_id
            farmer_id = land.farmer_id
            LandMark=land.landmark
            neighbour = FarmerModel.query.filter(FarmerModel.phone==neighbour_number).first()

            if neighbour:
                neighbour_farmer_id = neighbour.farmer_id
            else:
                newfarmer = FarmerModel(
                    farmer_name=neighbour_name,
                    phone=neighbour_number,
                    city_id=city_id,
                    email="c",
                    farmer_image="",
                    landmark=LandMark,
                    password="",
                    years_of_experience=exp
                )
                db.session.add(newfarmer)
                db.session.commit()
                neighbour_farmer_id = newfarmer.farmer_id



            newNeighbour = NeighbourModel(
                farmer_id=farmer_id,
                farmer_neighbour_id=neighbour_farmer_id,
                land_id=lid
            )

            db.session.add(newNeighbour)
            NeighbourLand = LandModel(
                land_name="",
                years_of_cultivation=yearsOfCultivation,
                soil_type="",
                source_of_water=WaterSource,
                land_in_acres=LandInAcrs,
                landmark=LandMark,
                city_id=city_id,
                farmer_id=neighbour_farmer_id
            )
            db.session.add(NeighbourLand)
            db.session.commit()

            return jsonify({'message': 'Neighbour added successfully'}), 200

        except Exception as e:
            db.session.rollback()
            return jsonify(str(e)), 500

    @staticmethod
    def addNeighbourCropSession():
        try:
            Session_info=request.form["session"]
            Activities_list=request.form["Activities"]
            neighbour_session = json.loads(Session_info)
            ActivityJson = json.loads(Activities_list)
            neighbour_session["session_status"]="Harvest"
            existingSession = CultivationSessionModel.query.filter(CultivationSessionModel.land_id == neighbour_session["land_id"], or_(
                CultivationSessionModel.session_status != "Harvest",
                CultivationSessionModel.session_status == None
            )).all()
            if not existingSession:
                newSession = CultivationSessionModel(
                    **neighbour_session
                )
                db.session.add(newSession)
                db.session.commit()
                session_id = newSession.cultivation_session_id
                for a in ActivityJson:
                    activity=ActivityModel.query.filter(ActivityModel.activity_name==a['Activity_id']).first()
                    activity_id=activity.activity_id
                    a['Activity_id']=activity_id
                    a['cultivation_session_id']=session_id
                    newPerformedActivity=PerformedActivityModel(**a)
                    db.session.add(newPerformedActivity)
                db.session.commit()

                return jsonify("Seesion Added"), 200
            return jsonify("Seesion Not Allowed because one is icomplete"), 404
        except Exception as e:
            return jsonify(str(e)), 500

    @staticmethod
    def GetAllNeighboursWithLatestCrop():
        try:
            lid = request.form['id']
            Neighbour=(db.session.query(FarmerModel.farmer_id,FarmerModel.farmer_name,FarmerModel.years_of_experience,FarmerModel.phone,LandModel.source_of_water,LandModel.years_of_cultivation,CropModel.crop_name)
                       .join(NeighbourModel,NeighbourModel.farmer_neighbour_id==FarmerModel.farmer_id).
                       join(LandModel,LandModel.farmer_id==FarmerModel.farmer_id).
                       join(CultivationSessionModel,CultivationSessionModel.land_id==LandModel.land_id).
                       join(CropModel,CropModel.crop_id==CultivationSessionModel.crop_id).
                       filter(NeighbourModel.land_id == lid,CultivationSessionModel.session_status=='Harvest').
                       order_by(CultivationSessionModel.sowing_date.desc()).
                       all())

            if not Neighbour:
                return jsonify("Invalid land id"), 400

            Neighbours = {}

            for i in Neighbour:
                if i.farmer_id not in Neighbours:
                    Neighbours[i.farmer_id] = {
                        "farmer_id": i.farmer_id,
                        "farmer_name": i.farmer_name,
                        "Phone": i.phone,
                        "Crop": i.crop_name,
                        "years_of_experience": i.years_of_experience,
                        "source_of_water": i.source_of_water,
                        "years_of_cultivation": i.years_of_cultivation,
                    }
            Neighbours = list(Neighbours.values())

            return jsonify(Neighbours), 200
        except Exception as e:
            db.session.rollback()
            return jsonify(str(e)), 500

    @staticmethod
    def GetAllCropsOfNeighbour():
        try:
            Neighbour_Farmer_id = request.form['id']
            Neighbour = (db.session.query(FarmerModel.farmer_name,CropModel.crop_name,CultivationSessionModel.production_in_tons,CultivationSessionModel.is_profit,CultivationSessionModel.amount_per_acre,CultivationSessionModel.sowing_date,CultivationSessionModel.harwesting_date).
                         join(NeighbourModel,NeighbourModel.farmer_neighbour_id==FarmerModel.farmer_id).
                         join(LandModel,LandModel.farmer_id==FarmerModel.farmer_id).
                         join(CultivationSessionModel,CultivationSessionModel.land_id==LandModel.land_id).
                         join(CropModel,CropModel.crop_id==CultivationSessionModel.crop_id).
                         filter(FarmerModel.farmer_id==Neighbour_Farmer_id)).all()

            Neighbours = []
            if not Neighbour:
                return jsonify("Invalid Neighbour id"), 400
            for i in Neighbour:
                Neighbours.append({
                    "farmer_name": i.farmer_name,
                    "Crop": i.crop_name,
                    "sowing_date": i.sowing_date,
                    "Harvesting_date": i.harwesting_date,
                    "Production": i.production_in_tons,
                    "Amount per acre": i.amount_per_acre,
                    "Profit":"Yes" if i.is_profit==1 else "No"
                })
            return jsonify(Neighbours), 200
        except Exception as e:
            return jsonify(str(e)), 500

    @staticmethod
    def GetAllNeighboursWithAllCorps():
        try:
            lid = request.form['id']
            Neighbour=(db.session.query(FarmerModel.farmer_id,FarmerModel.farmer_name,FarmerModel.years_of_experience,FarmerModel.phone,LandModel.source_of_water,LandModel.years_of_cultivation,CropModel.crop_name)
                       .join(NeighbourModel,NeighbourModel.farmer_neighbour_id==FarmerModel.farmer_id).
                       join(LandModel,LandModel.farmer_id==FarmerModel.farmer_id).
                       join(CultivationSessionModel,CultivationSessionModel.land_id==LandModel.land_id).
                       join(CropModel,CropModel.crop_id==CultivationSessionModel.crop_id).
                       filter(NeighbourModel.land_id == lid,CultivationSessionModel.session_status=='Harvest').
                       order_by(CultivationSessionModel.sowing_date.desc()).
                       all())
            Neighbours=[]
            if not Neighbour:
                return jsonify("Invalid land id"), 400
            for i in Neighbour:
                Neighbours.append({
                    "farmer_id": i.farmer_id,
                    "farmer_name": i.farmer_name,
                    "Phone": i.phone,
                    "Crop": i.crop_name,
                    "years_of_experience": i.years_of_experience,
                    "source_of_water": i.source_of_water,
                    "years_of_cultivation": i.years_of_cultivation,
                })
            return jsonify(Neighbours), 200
        except Exception as e:
            return jsonify(str(e)), 500

    @staticmethod
    def ProfitableCropOfLandNeigbours():
        try:
            lid = request.form['id']
            Neighbour=(db.session.query(FarmerModel.farmer_id,FarmerModel.farmer_name,FarmerModel.years_of_experience,FarmerModel.phone,LandModel.source_of_water,LandModel.years_of_cultivation,CropModel.crop_name,CultivationSessionModel.production_in_tons)
                       .join(NeighbourModel,NeighbourModel.farmer_neighbour_id==FarmerModel.farmer_id).
                       join(LandModel,LandModel.farmer_id==FarmerModel.farmer_id).
                       join(CultivationSessionModel,CultivationSessionModel.land_id==LandModel.land_id).
                       join(CropModel,CropModel.crop_id==CultivationSessionModel.crop_id).
                       filter(NeighbourModel.land_id == lid,CultivationSessionModel.session_status=='Harvest',CultivationSessionModel.is_profit==1).
                       order_by(CultivationSessionModel.production_in_tons.desc()).
                       all())

            Neighbours = {}

            for i in Neighbour:
                if i.farmer_id not in Neighbours:
                    Neighbours[i.farmer_id] = {
                        "farmer_id": i.farmer_id,
                        "farmer_name": i.farmer_name,
                        "Phone": i.phone,
                        "Crop": i.crop_name,
                        "Production in Tons": i.production_in_tons,
                        "years_of_experience": i.years_of_experience,
                        "source_of_water": i.source_of_water,
                        "years_of_cultivation": i.years_of_cultivation,
                    }
            Neighbours = list(Neighbours.values())

            return jsonify(Neighbours), 200
        except Exception as e:
            return jsonify(str(e)), 500

    @staticmethod
    def getMostProfitableNeighbour():
        try:
            lid = request.form['id']
            Neighbour=(db.session.query(FarmerModel.farmer_id,FarmerModel.farmer_name,FarmerModel.years_of_experience,FarmerModel.phone,LandModel.source_of_water,LandModel.years_of_cultivation,CropModel.crop_name,CultivationSessionModel.production_in_tons)
                       .join(NeighbourModel,NeighbourModel.farmer_neighbour_id==FarmerModel.farmer_id).
                       join(LandModel,LandModel.farmer_id==FarmerModel.farmer_id).
                       join(CultivationSessionModel,CultivationSessionModel.land_id==LandModel.land_id).
                       join(CropModel,CropModel.crop_id==CultivationSessionModel.crop_id).
                       filter(NeighbourModel.land_id == lid,CultivationSessionModel.session_status=='Harvest',CultivationSessionModel.is_profit==1).
                       order_by(CultivationSessionModel.production_in_tons.desc()).
                       first())

            Neighbours = {}

            if Neighbour.farmer_id not in Neighbours:
                Neighbours[Neighbour.farmer_id] = {
                    "farmer_id": Neighbour.farmer_id,
                    "farmer_name": Neighbour.farmer_name,
                    "Phone": Neighbour.phone,
                    "Crop": Neighbour.crop_name,
                    "Production in Tons": Neighbour.production_in_tons,
                    "years_of_experience": Neighbour.years_of_experience,
                    "source_of_water": Neighbour.source_of_water,
                    "years_of_cultivation": Neighbour.years_of_cultivation,
                    }
            Neighbours = list(Neighbours.values())

            return jsonify(Neighbours), 200
        except Exception as e:
            return jsonify(str(e)), 500