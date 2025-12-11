from flask import Flask, jsonify, request

from Controller.LandController import LandController
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

@app.route('/edit', methods=['PUT'])
def edit():
    return FarmerController.edit()

@app.route('/login', methods=['POST'])
def login():
    return FarmerController.Login()

@app.route('/delete',methods=['DELETE'])
def delete():
    return FarmerController.delete()

@app.route('/getbyid',methods=['POST'])
def get():
    return FarmerController.getbyid()

@app.route('/getallFarmers',methods=['GET'])
def allFarmers():
    return FarmerController.getallFarmerRecord()

@app.route('/addLand',methods=['POST'])
def addLand():
    return LandController.AddLand()

@app.route('/editLand',methods=['PUT'])
def editLand():
    return LandController.editLand()

@app.route('/getallLands',methods=['GET'])
def getLands():
    return LandController.GetallLands()

@app.route('/deleteLand',methods=['DELETE'])
def deleteLand():
    return LandController.DeleteLand()

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True)
