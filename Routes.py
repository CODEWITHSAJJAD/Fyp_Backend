from flask import Flask, jsonify, request
from Controller.LandController import LandController
from Controller.NeighbourController import NeighbourController
from Controller.SessionController import SessionController
from db import db, init_db
from Controller.FarmerController import FarmerController
from Model.FarmerModel import FarmerModel
from Model.ChatModel import ChatModel
from Model.CityModel import CityModel
from Model.ActivityModel import ActivityModel
from Model.CropModel import CropModel
from Model.ProvinceModel import ProvinceModel
from Model.PerformActivityModel import PerformedActivityModel
from Model.CultivationSessionModel import CultivationSessionModel
from Model.LandModel import LandModel
from Model.NeighbourModel import NeighbourModel

app = Flask(__name__)
init_db(app)
with app.app_context():
    db.create_all()
    print("created")

@app.route('/')
def welcome():
    return jsonify({"body": "welcome"})

@app.route('/signup', methods=['POST'])
def signup():
    return FarmerController.Signup()

@app.route('/login', methods=['POST'])
def login():
    return FarmerController.Login()

@app.route('/FarmerSetting', methods=['PUT'])
def edit():
    return FarmerController.edit()

@app.route('/delete',methods=['DELETE'])
def delete():
    return FarmerController.delete()

@app.route('/getFarmerById',methods=['POST'])
def get():
    return FarmerController.getbyid()

@app.route('/getAllFarmers',methods=['GET'])
def allFarmers():
    return FarmerController.getallFarmerRecord()

@app.route('/addFarmerLand',methods=['POST'])
def addLand():
    return LandController.AddLand()

@app.route('/editFarmerLand',methods=['PUT'])
def editLand():
    return LandController.editLand()

@app.route('/getFarmerAllLands',methods=['GET'])
def FarmerAllLands():
    return LandController.GetallLands()

@app.route('/deleteLand',methods=['DELETE'])
def deleteLand():
    return LandController.DeleteLand()

@app.route('/addCropSession',methods=['POST'])
def addCropSession():
    return SessionController.AddSession()

@app.route('/addNeighbour',methods=['POST'])
def addNeighbour():
    return NeighbourController.AddNeighbour()

@app.route('/GetAllNeighboursWithLatestCrop',methods=['POST'])
def AllNeighboursWithLatestCrop():
    return NeighbourController.GetAllNeighboursWithLatestCrop()

@app.route('/GetAllNeighboursWithAllCorps',methods=['POST'])
def AllNeighboursWithAllCorps():
    return NeighbourController.GetAllNeighboursWithAllCorps()


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5001,debug=True)
