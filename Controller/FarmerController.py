from flask import request,jsonify
from db import db
from sqlalchemy import or_
from Model.FarmerModel import FarmerModel
from Model.CityModel import CityModel
import json
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
        try:
            city = CityModel.query.filter(CityModel.city_name ==city).first()
            city_id=city.city_id
            print(city_id)
            newFarmer=FarmerModel(farmer_name=Farmer_name,phone=Farmer_number,email=Farmer_email,city_id=city_id,farmer_image=None,landmark=landmark,password=password,years_of_experience=2)
            db.session.add(newFarmer)
            db.session.commit()
            return jsonify({'message': 'Farmer Signup successfully'}),200
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
                return jsonify({
                    "message":"login Successfull"
                }),200
            return jsonify({
                "message":"invalid username or pwd"
            }),404
        except Exception as e:
            return jsonify(str(e)),500
    @staticmethod
    def edit():
        try:
            data = request.form['farmer']
            image = request.files['image']
            json_data = json.loads(data)
            id=json_data['id']
            farmer_name = json_data['name']
            farmer_number = json_data['number']
            farmer_email = json_data['email']
            landmark = json_data['landmark']
            password = json_data['password']
            city_name = json_data['city']
            file_path = image.filename
            city = CityModel.query.filter(CityModel.city_name == city_name).first()
            if not city:
                return jsonify({"error": f"City '{city_name}' not found"}), 404
            city_id = city.city_id
            existing_farmer = FarmerModel.query.filter(
                FarmerModel.farmer_id == id
            ).first()

            if not existing_farmer:
                return jsonify({"error": "Farmer not found"}), 404
            existing_farmer.farmer_name=farmer_name
            existing_farmer.phone = farmer_number
            existing_farmer.email = farmer_email
            existing_farmer.city_id = city_id
            existing_farmer.farmer_image = file_path
            existing_farmer.landmark = landmark
            existing_farmer.password = password
            existing_farmer.years_of_experience = 2
            db.session.commit()
            return jsonify({"message": "Farmer Updated successfully"}), 200
        except KeyError as e:
            return jsonify({"error": f"Missing field: {str(e)}"}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def getbyid():
        fid=request.form['id']
        try:
            data=FarmerModel.query.filter(FarmerModel.farmer_id==fid).first()
            city = CityModel.query.filter(CityModel.city_id == data.city_id).first()
            if data:
                return jsonify({
                    "Name":data.farmer_name,
                    "Phone":data.phone,
                    "Email":data.email,
                    "City":city.city_name,
                    "Landmark":data.landmark,
                    "years_of_experience":data.years_of_experience
                }),200
            return jsonify({
                "message":"not found"
            }),404
        except Exception as e:
            return jsonify(str(e)), 500
    @staticmethod
    def delete():
        fid=request.form['id']
        FarmerModel.query.filter(FarmerModel.farmer_id==fid).delete()
        db.session.commit()
        return ({"message":"Farmer delete successfully"}),200
    @staticmethod
    def getallFarmerRecord():
        try:
            allfarmers=FarmerModel.query.all()
            if allfarmers:
                farmerList=[]
                for f in allfarmers:
                    city=CityModel.query.filter(CityModel.city_id==f.city_id).first()
                    farmerList.append({
                        "Name":f.farmer_name,
                        "Phone":f.phone,
                        "Email":f.email,
                        "City":city.city_name,
                        "Landmark":f.landmark,
                        "years_of_experience":f.years_of_experience
                    })
                return jsonify(farmerList),200
            return jsonify("No record Found"),404
        except Exception as e:
            return jsonify(str(e)),500


