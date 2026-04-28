from flask import request, jsonify
from sqlmodel import or_, and_
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
from url import imageurl


class NeighbourController:

    @staticmethod
    def SeachNeighbour():
        data=request.get_json()
        lid=data['id']
        phone=data['phone']
        try:
            Land=LandModel.query.filter(LandModel.land_id==lid).first()
            city_id=Land.city_id
            Nieghbours=(db.session.query(FarmerModel.farmer_name,FarmerModel.farmer_image,FarmerModel.phone,
                                         LandModel.land_name,LandModel.land_id,LandModel.source_of_water,LandModel.landmark,
                                         CultivationSessionModel.cultivation_session_id,CropModel.crop_name,CropModel.crop_image).
                        join(LandModel,FarmerModel.farmer_id==LandModel.farmer_id).
                        join(CultivationSessionModel,LandModel.land_id==CultivationSessionModel.land_id).
                        join(CropModel,CultivationSessionModel.crop_id==CropModel.crop_id).
                        filter(LandModel.city_id==city_id,FarmerModel.phone==phone).order_by(CultivationSessionModel.cultivation_session_id.desc())).all()
            NeighbouringLands= {}
            if Nieghbours:
                for n in Nieghbours:
                    existingcheck = NeighbourModel.query.filter(
                        or_(
                            and_(NeighbourModel.land_id == lid, NeighbourModel.neighbour_land_id == n.land_id),
                            and_(NeighbourModel.land_id == n.land_id, NeighbourModel.neighbour_land_id == lid)
                        )).first()
                    if n.land_id not in NeighbouringLands and not existingcheck:
                        NeighbouringLands[n.land_id]={
                            "Farmer_Name":n.farmer_name,
                            "Farmer_Image":imageurl+n.farmer_image,
                            "Phone":n.phone,
                            "Land_id":n.land_id,
                            "Land_Name":n.land_name,
                            "Source_Of_Water":n.source_of_water,
                            "LandMark":n.landmark,
                            "Crop_Name":n.crop_name,
                            "Crop_Image":imageurl+n.crop_image,
                            "Session_id":n.cultivation_session_id
                        }
                NeighbouringLands=list(NeighbouringLands.values())
                return jsonify(NeighbouringLands),200
            return jsonify({'message': 'Land not found'}), 404
        except Exception as e:
            return jsonify(str(e)),500

    @staticmethod
    def AddNeighbour():
        try:
            data=request.get_json()
            lid=data["land_id"]
            neighbour_land_id=data["neighbour_land_id"]
            land = LandModel.query.filter(LandModel.land_id==lid).first()
            neighbour_land=LandModel.query.filter(LandModel.land_id==neighbour_land_id).first()
            if not land and not neighbour_land:
                return jsonify("Invalid land id"), 404
            else:
                existingcheck=NeighbourModel.query.filter(and_(
                    or_(
                        and_(NeighbourModel.land_id==lid,NeighbourModel.neighbour_land_id==neighbour_land_id),
                        and_(NeighbourModel.land_id==neighbour_land_id,NeighbourModel.neighbour_land_id==lid)
                    ),NeighbourModel.status==1)).first()
                if existingcheck:
                    return jsonify("already exist"),208
                data["status"]=0
                newNeighbour=NeighbourModel(**data)
                db.session.add(newNeighbour)
                db.session.commit()
                return jsonify({'message': 'Neighbour added successfully'}), 200
        except Exception as e:
            return jsonify(str(e)), 500

    @staticmethod
    def GetAllLandsOfNeighbour(id):
        try:
            f_id=id
            Lands=(db.session.query(LandModel.land_name,LandModel.land_in_acres,LandModel.years_of_cultivation,LandModel.source_of_water,LandModel.landmark,CityModel.city_name).
                   join(CityModel,CityModel.city_id==LandModel.land_id)
                   .filter(LandModel.farmer_id==f_id)).all()
            landsList=[]
            if Lands:
                for l in Lands:
                    landsList.append({
                        "land name":l.land_name,
                        "Years Of Cultivation":l.years_of_cultivation,
                        "Land in Acres":l.land_in_acres,
                        "source_of_water":l.source_of_water,
                        "City":l.city_name,
                        "landmark":l.landmark

                    })
                return jsonify(landsList),200
            return jsonify("No lands of this Neighbour"),404
        except Exception as e:
            return jsonify(str(e)),500

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
    def GetAllNeighboursWithLatestCrop(lid):
        try:
            Neighbour = (
                db.session.query(FarmerModel.farmer_id, FarmerModel.farmer_name, FarmerModel.years_of_experience,FarmerModel.farmer_image,
                                 FarmerModel.phone, LandModel.land_in_acres,LandModel.source_of_water, LandModel.years_of_cultivation,LandModel.land_name,LandModel.land_id,
                                 CropModel.crop_name,CropModel.crop_image)
                .join(NeighbourModel, or_(
                    and_(NeighbourModel.land_id == lid, NeighbourModel.neighbour_land_id == LandModel.land_id),
                    and_(NeighbourModel.neighbour_land_id == lid, NeighbourModel.land_id == LandModel.land_id)
                )).
                join(FarmerModel, LandModel.farmer_id == FarmerModel.farmer_id).
                join(CultivationSessionModel, LandModel.land_id == CultivationSessionModel.land_id).
                join(CropModel, CultivationSessionModel.crop_id == CropModel.crop_id).
                filter(CultivationSessionModel.session_status != 'Harvest').
                filter(NeighbourModel.status == 1).
                all())

            if not Neighbour:
                return jsonify("Invalid land id"), 404

            Neighbours = {}

            for i in Neighbour:
                if i.farmer_id not in Neighbours:
                    Neighbours[i.land_id] = {
                        "farmer_id": i.farmer_id,
                        "farmer_name": i.farmer_name.capitalize(),
                        "farmer_image":imageurl+i.farmer_image,
                        "land_id":i.land_id,
                        "land_name":i.land_name.capitalize(),
                        "Phone": i.phone,
                        "Crop": i.crop_name.capitalize(),
                        "land_in_acres":i.land_in_acres,
                        "Crop_image":imageurl+i.crop_image,
                        "years_of_experience": i.years_of_experience,
                        "source_of_water": i.source_of_water.capitalize(),
                        "years_of_cultivation": i.years_of_cultivation,
                    }
            Neighbours = list(Neighbours.values())
            # Neighbours = []
            #
            # for i in Neighbour:
            #     Neighbours.append({
            #             "farmer_id": i.farmer_id,
            #             "farmer_name": i.farmer_name.capitalize(),
            #             "farmer_image": imageurl+i.farmer_image,
            #             "land_id": i.land_id,
            #             "land_name": i.land_name.capitalize(),
            #             "Phone": i.phone,
            #             "Crop": i.crop_name.capitalize(),
            #             "Crop_image": imageurl+i.crop_image,
            #             "years_of_experience": i.years_of_experience,
            #             "source_of_water": i.source_of_water.capitalize(),
            #             "years_of_cultivation": i.years_of_cultivation,
            #         })
            return jsonify(Neighbours), 200
        except Exception as e:
            return jsonify(str(e)), 500

    # def GetAllNeighboursWithLatestCrop(lid):
    #     try:
    #         Nieghbours = (db.session.query(FarmerModel.farmer_name, FarmerModel.farmer_image, FarmerModel.phone,
    #                                        LandModel.land_name, LandModel.land_id, LandModel.source_of_water,
    #                                        LandModel.landmark,
    #                                        CultivationSessionModel.cultivation_session_id, CropModel.crop_name,
    #                                        CropModel.crop_image).
    #                       join(LandModel, FarmerModel.farmer_id == LandModel.farmer_id).
    #                       join(CultivationSessionModel, LandModel.land_id == CultivationSessionModel.land_id).
    #                       join(CropModel, CultivationSessionModel.crop_id == CropModel.crop_id).
    #                       order_by(CultivationSessionModel.cultivation_session_id.desc())).all()
    #         NeighbouringLands = {}
    #         if Nieghbours:
    #             for n in Nieghbours:
    #                 existingcheck = NeighbourModel.query.filter(
    #                     or_(
    #                         and_(NeighbourModel.land_id == lid, NeighbourModel.neighbour_land_id == n.land_id),
    #                         and_(NeighbourModel.land_id == n.land_id, NeighbourModel.neighbour_land_id == lid)
    #                     )).first()
    #                 if n.cultivation_session_id not in NeighbouringLands and existingcheck:
    #                     NeighbouringLands[n.cultivation_session_id] = {
    #                         "farmer_name": n.farmer_name,
    #                         "farmer_image": imageurl+n.farmer_image,
    #                         "Phone": n.phone,
    #                         "land_id": n.land_id,
    #                         "land_name": n.land_name,
    #                         "source_of_water": n.source_of_water,
    #                         "LandMark": n.landmark,
    #                         "Crop": n.crop_name,
    #                         "Crop_image": imageurl+n.crop_image,
    #                         "Session_id": n.cultivation_session_id
    #                     }
    #             NeighbouringLands = list(NeighbouringLands.values())
    #             return jsonify(NeighbouringLands), 200
    #         return jsonify({'message': 'Land not found'}), 404
    #     except Exception as e:
    #         return jsonify(str(e)), 500

    @staticmethod
    def GetAllCropsOfNeighbour(id):
        try:
            Neighbour_Farmer_id =id
            Neighbour = (db.session.query(FarmerModel.farmer_name,CropModel.crop_name,CultivationSessionModel.production_in_tons,CultivationSessionModel.is_profit,CultivationSessionModel.amount_per_acre,CultivationSessionModel.sowing_date,CultivationSessionModel.harwesting_date).
                         join(LandModel,LandModel.farmer_id==FarmerModel.farmer_id).
                         join(NeighbourModel,or_(NeighbourModel.neighbour_land_id==LandModel.land_id,NeighbourModel.land_id==LandModel.land_id)).
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
    def ProfitableCropOfLandNeigbours(id):
        try:
            lid =id
            Neighbour=(db.session.query(FarmerModel.farmer_id,FarmerModel.farmer_name,FarmerModel.years_of_experience,FarmerModel.phone,LandModel.source_of_water,LandModel.years_of_cultivation,CropModel.crop_name,CultivationSessionModel.production_in_tons)
                       .join(NeighbourModel, or_(
                           and_(NeighbourModel.land_id == lid, NeighbourModel.neighbour_land_id == LandModel.land_id),
                           and_(NeighbourModel.neighbour_land_id == lid, NeighbourModel.land_id == LandModel.land_id)
                       )).
                       join(LandModel,LandModel.farmer_id==FarmerModel.farmer_id).
                       join(CultivationSessionModel,CultivationSessionModel.land_id==LandModel.land_id).
                       join(CropModel,CropModel.crop_id==CultivationSessionModel.crop_id).
                       filter(CultivationSessionModel.session_status=='Harvest',CultivationSessionModel.is_profit==1).
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
    def GetAllNeighboursWithAllCorps(id):
        try:
            lid =id
            Neighbour=(db.session.query(FarmerModel.farmer_id,FarmerModel.farmer_name,FarmerModel.years_of_experience,FarmerModel.phone,LandModel.source_of_water,LandModel.years_of_cultivation,CropModel.crop_name)
                       .join(NeighbourModel, or_(
                           and_(NeighbourModel.land_id == lid, NeighbourModel.neighbour_land_id == LandModel.land_id),
                           and_(NeighbourModel.neighbour_land_id == lid, NeighbourModel.land_id == LandModel.land_id)
                       )).
                       join(FarmerModel,FarmerModel.farmer_id==LandModel.farmer_id).
                       join(CultivationSessionModel,CultivationSessionModel.land_id==LandModel.land_id).
                       join(CropModel,CropModel.crop_id==CultivationSessionModel.crop_id).
                       filter(CultivationSessionModel.session_status=='Harvest').
                       order_by(CultivationSessionModel.sowing_date.desc()).
                       all())
            Neighbours=[]
            if not Neighbour:
                return jsonify("Invalid land id"), 404
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
    def getMostProfitableNeighbour(id):
        try:
            lid = id
            Neighbour=(db.session.query(FarmerModel.farmer_id,FarmerModel.farmer_name,FarmerModel.years_of_experience,FarmerModel.phone,LandModel.source_of_water,LandModel.years_of_cultivation,CropModel.crop_name,CultivationSessionModel.production_in_tons)
                       .join(NeighbourModel, or_(
                           and_(NeighbourModel.land_id == lid, NeighbourModel.neighbour_land_id == LandModel.land_id),
                           and_(NeighbourModel.neighbour_land_id == lid, NeighbourModel.land_id == LandModel.land_id)
                       )).
                       join(LandModel,LandModel.farmer_id==FarmerModel.farmer_id).
                       join(CultivationSessionModel,CultivationSessionModel.land_id==LandModel.land_id).
                       join(CropModel,CropModel.crop_id==CultivationSessionModel.crop_id).
                       filter(CultivationSessionModel.session_status=='Harvest',CultivationSessionModel.is_profit==1).
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

    @staticmethod
    def GetNeighbourRequests(id):
        try:
            farmerLands = LandModel.query.filter(LandModel.farmer_id == id).all()
            if not farmerLands:
                return jsonify("No lands found for this farmer"), 404
            ReqList = []
            for fl in farmerLands:
                print("farmer lands:",fl.land_id)
                requests = NeighbourModel.query.filter(
                    NeighbourModel.neighbour_land_id == fl.land_id,
                    NeighbourModel.status == 0
                ).all()
                for r in requests:
                    print("neighbor:",r.land_id)
                    request_ownnerland=LandModel.query.filter(LandModel.land_id == r.land_id).first()
                    request_owner=FarmerModel.query.filter(FarmerModel.farmer_id == request_ownnerland.farmer_id).first()
                    if request_ownnerland and request_owner:
                        ReqList.append({
                            "farmer_id": request_owner.farmer_id,
                            "farmer_name": request_owner.farmer_name,
                            "phone": request_owner.phone,
                            "farmer_image": imageurl+request_owner.farmer_image if request_owner.farmer_image else None,
                            "land_id":request_ownnerland.land_id,
                            "land_name": request_ownnerland.land_name,
                            "land_mark":request_ownnerland.landmark,
                            "Neighbour_id": r.neighbour_id,
                        })
                    # requesting_land_owner = (db.session.query(
                    #     FarmerModel.farmer_id,
                    #     FarmerModel.farmer_name,
                    #     FarmerModel.farmer_image,
                    #     FarmerModel.phone,
                    #     LandModel.land_name,
                    #     LandModel.landmark
                    # )
                    # .join(LandModel, LandModel.farmer_id == FarmerModel.farmer_id)
                    # .filter(LandModel.land_id == r.land_id)
                    # .first()
                    # )
                    #
                    # if requesting_land_owner:
                    #     ReqList.append({
                    #         "farmer_id": requesting_land_owner.farmer_id,
                    #         "farmer_name": requesting_land_owner.farmer_name,
                    #         "phone": requesting_land_owner.phone,
                    #         "farmer_image": imageurl+requesting_land_owner.farmer_image,
                    #         "land_id":r.neighbour_land_id,
                    #         "land_name": requesting_land_owner.land_name,
                    #         "land_mark":requesting_land_owner.landmark,
                    #         "Neighbour_id": r.neighbour_id,
                    #     })

            if ReqList:
                return jsonify(ReqList), 200
            else:
                return jsonify("No pending neighbour requests found"), 404

        except Exception as e:
            return jsonify(str(e)), 500

    @staticmethod
    def AcceptRequest(id):
        try:
            existing_request=NeighbourModel.query.filter(NeighbourModel.neighbour_id==id).first()
            if existing_request:
                existing_request.status=1
                db.session.commit()
                return jsonify("request accepted"), 200
        except Exception as e:
            return jsonify(str(e)), 500

    @staticmethod
    def RejectRequest(id):
        try:
            reject_request = NeighbourModel.query.filter(NeighbourModel.neighbour_id == id).first()
            if reject_request:
                db.session.delete(reject_request)
                db.session.commit()
                return jsonify("request rejected"), 200
            return jsonify("Invalid request"), 404
        except Exception as e:
            return jsonify(str(e)), 500