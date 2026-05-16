import os
from datetime import datetime
from flask import request,jsonify,send_file
from tomlkit.items import Null
from Services.NotificationHelper import NotificationHelper
from Model.ProvinceModel import ProvinceModel
from db import db
from sqlalchemy import or_
from Model.FarmerModel import FarmerModel
from Model.CityModel import CityModel
import json

from url import imageurl


class FarmerController:
    @staticmethod
    def Signup():
        data=request.get_json()
        Farmer_name=data['name']
        Farmer_number=data['number']
        Farmer_email=data['email']
        landmark=data['landmark']
        password=data['password']
        city=data['city']
        years0f=data['yearsofexp']
        try:
            city = CityModel.query.filter(CityModel.city_name ==city).first()
            city_id=city.city_id
            print(city_id)
            newFarmer=FarmerModel(farmer_name=Farmer_name,phone=Farmer_number,email=Farmer_email,city_id=city_id,farmer_image=None,landmark=landmark,password=password,years_of_experience=years0f,Prefered_Date=datetime.today())
            db.session.add(newFarmer)
            db.session.commit()
            
            NotificationHelper.welcome_notification(newFarmer.farmer_id, Farmer_name)
            
            return jsonify(newFarmer.farmer_id),200
        except Exception as e:
            return jsonify(str(e)), 500

    @staticmethod
    def Login():
        data=request.get_json()
        user_info=data['info']
        pwd=data['pwd']
        try:
            user=FarmerModel.query.filter(
                or_(
                FarmerModel.email == user_info,
                FarmerModel.phone == user_info
            ), FarmerModel.password==pwd).first()
            if user:
                NotificationHelper.login_notification(user.farmer_id)
                
                return jsonify(
                    {"name": user.farmer_name,
                     "id":user.farmer_id}
                ),200
            return jsonify(
                "invalid username or pwd"
            ),404
        except Exception as e:
            return jsonify(str(e)),500

    @staticmethod
    def edit():
        try:
            data = request.form['farmer']
            update = request.form.get('update_image', 'false').lower() == 'true'
            print(update)
            image = request.files.get('image')
            print(image)
            json_data = json.loads(data)
            id=json_data['id']
            farmer_name = json_data['name']
            farmer_number = json_data['number']
            farmer_email = json_data['email']
            landmark = json_data['landmark']
            password = json_data['password']
            city_name = json_data['city']
            experiemce=json_data['experiemce']
            uploads_dir = "uploads/farmers"
            save_path=None
            if image and update :
                if not os.path.exists(uploads_dir):
                    os.makedirs(uploads_dir)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
                extension = image.filename.split('.')[-1] if '.' in image.filename else 'jpg'
                unique_filename = f"{timestamp}.{extension}"
                save_path = os.path.join(uploads_dir, unique_filename)
                image.save(save_path)
            city = CityModel.query.filter(CityModel.city_name == city_name).first()
            if not city:
                return jsonify(f"City '{city_name}' not found"), 404
            city_id = city.city_id
            existing_farmer = FarmerModel.query.filter(
                FarmerModel.farmer_id == id
            ).first()

            if not existing_farmer:
                return jsonify( "Farmer not found"), 404
            existing_farmer.farmer_name=farmer_name
            existing_farmer.phone = farmer_number
            existing_farmer.email = farmer_email
            existing_farmer.city_id = city_id
            existing_farmer.farmer_image = save_path if update else existing_farmer.farmer_image
            existing_farmer.landmark = landmark
            existing_farmer.password = password
            existing_farmer.Prefered_Date=existing_farmer.Prefered_Date
            existing_farmer.years_of_experience = experiemce

            db.session.commit()
            NotificationHelper.Setting_notification(farmer_id=existing_farmer.farmer_id)
            return jsonify("Farmer Updated successfully"), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def getbyid(id):
        fid = id
        try:
            # data = FarmerModel.query.filter(FarmerModel.farmer_id == fid).first()
            data=(db.session.query(FarmerModel.farmer_image,FarmerModel.farmer_name,FarmerModel.phone,FarmerModel.landmark,FarmerModel.email,FarmerModel.years_of_experience,FarmerModel.Prefered_Date,CityModel.city_name,ProvinceModel.province_name).join(CityModel,FarmerModel.city_id==CityModel.city_id).join(ProvinceModel,CityModel.province_id==ProvinceModel.province_id).filter(FarmerModel.farmer_id == fid)).first()
            if data:
                image_path = data.farmer_image.replace("\\", "/") if data.farmer_image else None
                print(image_path)
                return jsonify({
                    "Name": data.farmer_name,
                    "image": imageurl+image_path if image_path else None,
                    "Phone": data.phone,
                    "Email": data.email,
                    "City": data.city_name,
                    "Province": data.province_name,
                    "Landmark": data.landmark,
                    "years_of_experience": data.years_of_experience,
                    "Prefered_Date":data.Prefered_Date
                }), 200
            return jsonify("not found"), 404
        except Exception as e:
            return jsonify(str(e)), 500

    @staticmethod
    def getCities(id):
        province=id
        city = []
        try:
            cities=CityModel.query.filter(CityModel.province_id == province).all()
            if cities:
                for c in cities:
                    city.append(c.city_name)
                return jsonify(city),200
            return jsonify("Not Found"),404
        except Exception as e:
            return jsonify(str(e)), 500

    @staticmethod
    def RecordPreferdDate():
        data=request.get_json()
        try:
            existing_farmer = FarmerModel.query.filter(FarmerModel.farmer_id==data['farmer_id']).first()
            if not existing_farmer:
                return jsonify("Farmer not found"), 404
            existing_farmer.farmer_name = existing_farmer.farmer_name
            existing_farmer.phone = existing_farmer.phone
            existing_farmer.email = existing_farmer.email
            existing_farmer.city_id = existing_farmer.city_id
            existing_farmer.farmer_image = existing_farmer.farmer_image
            existing_farmer.landmark = existing_farmer.landmark
            existing_farmer.password = existing_farmer.password
            existing_farmer.years_of_experience = existing_farmer.years_of_experience
            existing_farmer.Prefered_Date=data['Prefered_Date']
            db.session.commit()
            # NotificationHelper.Setting_notification(farmer_id=existing_farmer.farmer_id)
            return jsonify("Farmer Updated successfully"), 200
        except Exception as e:
            return jsonify(str(e)), 500