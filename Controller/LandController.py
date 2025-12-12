from Model.ChatModel import ChatModel
from Model.CityModel import CityModel
from Model.FarmerModel import FarmerModel
from Model.LandModel import LandModel
from db import db
from flask import jsonify,request

class LandController:
    @staticmethod
    def AddLand():
        try:
            data=request.get_json()
            city_name = data['city_id']
            city = CityModel.query.filter(CityModel.city_name == city_name).first()
            city_id = city.city_id
            data['city_id'] = city_id
            NewLand=LandModel(**data)
            db.session.add(NewLand)
            db.session.commit()
            return jsonify('Land added!'),200
        except Exception as e:
            return jsonify( str(e)),500

    @staticmethod
    def DeleteLand():
        lid=request.form['id']
        try:
            LandModel.query.filter(LandModel.land_id==lid).delete()
            db.session.commit()
            return jsonify('Land deleted!'),200
        except Exception as e:
            return jsonify( str(e)),500

    @staticmethod
    def editLand():
        data=request.get_json()
        lid=data['id']
        city_name=data['city_name']
        try:
            city=CityModel.query.filter(CityModel.city_name==city_name).first()
            city_id=city.city_id
            existingland=LandModel.query.filter(LandModel.land_id==lid).first()
            if existingland and city_id:
                existingland.land_id=lid
                existingland.land_name=data['land_name']
                existingland.years_of_cultivation=data['years_of_cultivation']
                existingland.soil_type=data['soil_type']
                existingland.source_of_water=data['source_of_water']
                existingland.land_in_acres=data['land_in_acres']
                existingland.city_id=city_id
                existingland.landmark=data['landmark']
                db.session.commit()
                return jsonify('Land edited!'),200
            else:
                return jsonify('Land not found!'),404
        except Exception as e:
            return jsonify( str(e)),500

    @staticmethod
    def GetallLands():
        f_id=request.form['f_id']
        landsLsit=[]
        try:

            Lands=LandModel.query.filter(LandModel.farmer_id==f_id).all()

            if Lands:
                for l in Lands:
                    city=CityModel.query.filter(CityModel.city_id==l.city_id).first()
                    landsLsit.append({
                        'land_id':l.land_id,
                        'land_name':l.land_name,
                        'years_of_cultivation':l.years_of_cultivation,
                        'soil_type':l.soil_type,
                        'source_of_water':l.source_of_water,
                        'land_in_acres':l.land_in_acres,
                        'city_Name':city.city_name,
                        'landMark':l.landmark,
                    })
                return jsonify(landsLsit),200
            else:
                return jsonify('Land not found against farmer!'),404
        except Exception as e:
            return jsonify( str(e)),500
