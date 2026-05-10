import email

from flask import jsonify
from Model.CropModel import CropModel
from db import  db
from url import imageurl


class CropController:
    @staticmethod
    def getAllCrops():
        try:
            crops=CropModel.query.all()
            if crops:
                allCrops=[]
                for c in crops:
                    allCrops.append({
                        "id":c.crop_id,
                        "Name":c.crop_name,
                        "Image":imageurl+c.crop_image,
                        "Season":"Rabi" if c.season_name==0 else "Kharif",
                    })
                return jsonify(allCrops),200
        except Exception as e:
            return jsonify(str(e)),500
