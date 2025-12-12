from flask import request, jsonify
from sqlalchemy import Null

from db import db
import json
from Model.LandModel import LandModel
from Model.FarmerModel import FarmerModel
from Model.NeighbourModel import NeighbourModel


class NeighbourController:
    @staticmethod
    def AddNeighbour():
        try:
            lid = int(request.form['id'])
            neighbour = json.loads(request.form['neighbour'])
            neighbour_name = neighbour['name']
            neighbour_number = neighbour['number']
            exp=neighbour['exp']
            yearsOfCultivation=neighbour['yearsOfCultivation']
            WaterSource=neighbour['WaterSource']
            LandInAcrs=neighbour['LandInAcrs']

            land = LandModel.query.filter(LandModel.land_id==lid).first()
            if not land:
                return jsonify("Invalid land id"), 400

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
    def Getallneighbours():
        try:
            lid = int(request.form['id'])
            Neighbour=(db.session.query(FarmerModel.farmer_name,FarmerModel.years_of_experience,FarmerModel.phone,LandModel.source_of_water,LandModel.years_of_cultivation).filter(LandModel.land_id == lid)
                       .join(NeighbourModel,NeighbourModel.farmer_neighbour_id==FarmerModel.farmer_id).
                       join(LandModel,LandModel.land_id==NeighbourModel.land_id)
                       .all())
            Neighbours=[]
            if not Neighbour:
                return jsonify("Invalid land id"), 400
            for i in Neighbour:
                Neighbours.append({
                    "farmer_name": i.farmer_name,
                    "Phone": i.phone,
                    "years_of_experience": i.years_of_experience,
                    "source_of_water": i.source_of_water,
                    "years_of_cultivation": i.years_of_cultivation,
                })
            return jsonify(Neighbours), 200
        except Exception as e:
            db.session.rollback()
            return jsonify(str(e)), 500
