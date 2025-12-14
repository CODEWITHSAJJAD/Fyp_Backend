from flask import Flask, jsonify, request
from Controller.LandController import LandController
from Controller.NeighbourController import NeighbourController
from Controller.SessionController import SessionController
from db import db, init_db
from Controller.FarmerController import FarmerController
from Model.ChatModel import ChatModel
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

@app.route('/getFarmerById',methods=['GET'])
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

@app.route('/addFarmerCropSession',methods=['POST'])
def addFarmerCropSession():
    return SessionController.AddSession()

@app.route('/addNeighbour',methods=['POST'])
def addNeighbour():
    return NeighbourController.AddNeighbour()

@app.route('/addNeighbourCropSession',methods=['POST'])
def addNeighbourCropSession():
    return NeighbourController.addNeighbourCropSession()

@app.route('/GetAllNeighboursWithLatestCrop',methods=['GET'])
def AllNeighboursWithLatestCrop():
    return NeighbourController.GetAllNeighboursWithLatestCrop()

@app.route('/GetAllNeighboursWithAllCorps',methods=['GET'])
def AllNeighboursWithAllCorps():
    return NeighbourController.GetAllNeighboursWithAllCorps()

@app.route('/ProfitableCropOfLandNeigbours',methods=['GET'])
def ProfitableCropOfNeigbours():
    return NeighbourController.ProfitableCropOfLandNeigbours()

@app.route('/getMostProfitableNeighbour',methods=['GET'])
def getProfitableNeighbour():
    return NeighbourController.getMostProfitableNeighbour()

@app.route("/getAllCropsOfNeighbour",methods=['GET'])
def getAllCropsOfNeighbour():
    return NeighbourController.GetAllCropsOfNeighbour()

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5001,debug=True)
