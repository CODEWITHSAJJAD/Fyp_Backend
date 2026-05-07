import os
from flask import Flask, jsonify, send_file, abort
from werkzeug.security import safe_join
from Controller.ActivityController import ActivityController
from Controller.CropController import CropController
from Controller.LandController import LandController
from Controller.NeighbourController import NeighbourController
from Controller.SessionController import SessionController
from Controller.taskController import TaskContoller
from Model.CityModel import CityModel
from Model.ProvinceModel import ProvinceModel
from db import db, init_db
from Controller.FarmerController import FarmerController
from Controller.ChatController import ChatController
from Controller.RecommendationController import RecommendationController
from Controller.ActivitiesSuggestionsController import ActivitiesSuggestionsController
import pandas as pd
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

app = Flask(__name__,static_folder="uploads")
app.config['UPLOAD_FOLDER'] = "uploads"
init_db(app)

with app.app_context():
    db.create_all()
    print("created")


# @app.get('/get-image/<path:filename>')
# def serve_image(filename):
#     """
#     Serve images from different directories based on the path
#     Examples:
#     - /get-image/uploads/crops/Rabi/Beans.jpg
#     - /get-image/crops/Rabi/Beans.jpg (without uploads prefix)
#     - /get-image/farmer/profile_123.jpg
#     """
#     try:
#         filename = filename.lstrip('/')
#         base_dir = 'uploads'
#         if filename.startswith('uploads/'):
#             filename = filename[len('uploads/'):]
#         file_path = safe_join(base_dir, filename)
#         base_abs = os.path.abspath(base_dir)
#         file_abs = os.path.abspath(file_path)
#         if not os.path.commonpath([base_abs, file_abs]) == base_abs:
#             abort(403, description="Access denied")
#         if not os.path.exists(file_path):
#             if os.path.exists(filename):
#                 file_path = filename
#             else:
#                 name_without_ext, current_ext = os.path.splitext(file_path)
#                 if not current_ext:
#                     for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
#                         temp_path = f"{name_without_ext}{ext}"
#                         if os.path.exists(temp_path):
#                             file_path = temp_path
#                             break
#             if not os.path.exists(file_path):
#                 directory = os.path.dirname(file_path)
#                 if os.path.exists(directory):
#                     available_files = os.listdir(directory)
#
#                 return jsonify({
#                     "error": "Image not found",
#                     "requested": filename,
#                     "searched_path": file_path
#                 }), 404
#         if not os.path.isfile(file_path):
#             return jsonify({"error": "Path is not a file"}), 400
#         mime_type = 'image/jpeg'
#         ext = os.path.splitext(file_path)[1].lower()
#         if ext == '.png':
#             mime_type = 'image/png'
#         elif ext == '.gif':
#             mime_type = 'image/gif'
#         elif ext == '.webp':
#             mime_type = 'image/webp'
#         elif ext == '.bmp':
#             mime_type = 'image/bmp'
#         elif ext in ['.jpg', '.jpeg']:
#             mime_type = 'image/jpeg'
#         else:
#             import mimetypes
#             guessed_type = mimetypes.guess_type(file_path)[0]
#             if guessed_type and guessed_type.startswith('image/'):
#                 mime_type = guessed_type
#         return send_file(
#             file_path,
#             mimetype=mime_type,
#             as_attachment=False,
#             download_name=os.path.basename(filename)
#         )
#
#     except Exception as e:
#         import traceback
#         print(f"ERROR: {str(e)}")
#         traceback.print_exc()
#         return jsonify({"error": str(e)}), 500

@app.get('/getCities/<id>')
def getCitiy(id):
    return FarmerController.getCities(id)

@app.post('/signup')
def signup():
    return FarmerController.Signup()

@app.post('/login')
def login():
    return FarmerController.Login()

@app.put('/FarmerSetting')
def FarmerSetting():
    return FarmerController.edit()

@app.get('/getFarmerById/<id>')
def get(id):
    return FarmerController.getbyid(id)

#########--Land--############

@app.post('/addFarmerLand')
def addLand():
    return LandController.AddLand()

@app.put('/editFarmerLand')
def editLand():
    return LandController.editLand()

@app.get('/getFarmerAllLands/<id>')
def FarmerAllLands(id):
    return LandController.GetallLands(id)

@app.get('/getLandByID/<id>')
def getLandByID(id):
   return LandController.getLandByID(id)

@app.delete('/deleteLand')
def deleteLand():
    return LandController.DeleteLand()

@app.get('/getAllCrops')
def AllCrops():
    return CropController.getAllCrops()

#########--Cultivation Session--############
@app.get('/getLandsWithCurrentSession/<id>')
def landswithcurrentsession(id):
    return LandController.getLandWithCurrentSession(id)

@app.post('/addFarmerCropSession')
def addFarmerCropSession():
    return SessionController.AddSession()

@app.get("/CurrentSessionOfFarmer/<id>")
def currentsessionofFarmer(id):
    return SessionController.GetCurrentSessionOfFarmer(id)

@app.get('/getAllSessionsOfFarmerLand/<id>')
def getAllSessionsOfFarmerLand(id):
    return SessionController.getAllSesssionsOfLand(id)

@app.get('/getCurrentSessionOfFarmerLand/<id>')
def getCurrentSessionOfFarmerLand(id):
    return SessionController.getCurrentSessionOfFarmerLand(id)

@app.get('/GetListOfAllActivitiesOfProfitableSession/<id>')
def GetListOfAllActivitiesOfProfitableSession(id):
    return SessionController.getActivityListOfProfitableSessionOfFarmerLand(id)

@app.get('/GetProfitableCropSessionOnFarmerLand/<id>')
def GetProfitableCropSessionOnFarmerLand(id):
    return SessionController.GetProfitableCropSessionOnFarmerLand(id)

@app.post('/HandlePublicSession/<id>')
def HandlePublicSession(id):
    return SessionController.handle_public_session(id)

########Task##################
@app.post('/seacrhFarmerLands')
def seacrhFarmerLands():
    return TaskContoller.SearchFarmer()

@app.post('/count')
def count():
    return TaskContoller.ActivityCount()

##########--Neighbor Handling--#################
@app.post('/seacrhNeighbouringLand')
def searchNeighbouringLands():
    return NeighbourController.SeachNeighbour()

@app.post('/addNeighbour')
def addNeighbour():
    return NeighbourController.AddNeighbour()

@app.get('/getNeighbourRequest/<id>')
def getRequestNeighbour(id):
    return NeighbourController.GetNeighbourRequests(id)

@app.post('/acceptNeighbourRequest/<id>')
def acceptNeighbourRequest(id):
    return NeighbourController.AcceptRequest(id)

@app.delete('/rejectNeighbourRequest/<id>')
def rejectNeighbourRequest(id):
    return NeighbourController.RejectRequest(id)

@app.get('/getAllLandsOfNeighbour/<id>')
def AllLandsOfNeighbour(id):
    return NeighbourController.GetAllLandsOfNeighbour(id)

@app.post('/addNeighbourCropSession')
def addNeighbourCropSession():
    return NeighbourController.addNeighbourCropSession()

@app.get('/GetAllNeighboursWithLatestCrop/<id>')
def AllNeighboursWithLatestCrop(id):
    return NeighbourController.GetAllNeighboursWithLatestCrop(lid=id)

@app.get('/GetAllNeighboursWithAllCorps/<id>')
def AllNeighboursWithAllCorps(id):
    return NeighbourController.GetAllNeighboursWithAllCorps(id)

@app.get('/ProfitableCropOfLandNeigbours/<id>')
def ProfitableCropOfNeigbours(id):
    return NeighbourController.ProfitableCropOfLandNeigbours(id)

@app.get('/getMostProfitableNeighbour/<id>')
def getProfitableNeighbour(id):
    return NeighbourController.getMostProfitableNeighbour(id)

@app.get("/getAllCropsOfNeighbour/<id>")
def getAllCropsOfNeighbour(id):
    return NeighbourController.GetAllCropsOfNeighbour(id)

##########--Activities--#################

@app.get('/getActivitiesList')
def activitieslist():
    return ActivityController.getListofActivities()

@app.post("/AddFarmerSessionActivity")
def AddFarmerSessionActivity():
    return ActivityController.AddActivity()

@app.put('/editActivity')
def editActivity():
    return ActivityController.EditActivity()

@app.get("/getAllActivitiesOfFarmer/<id>")
def getAllActivitiesOfFarmer(id):
    return ActivityController.getAllActivitiesOfFarmer(id)

@app.get('/getSessionPerformedActivities/<id>')
def PerformedActivities(id):
    return ActivityController.getSessionPerformedActivities(id)

##########--Chat--#################

@app.post("/chat")
def chat():
    return ChatController.chat()

@app.get('/getChats/<id>')
def AllChats(id):
    return ChatController.getChats(id)

@app.get("/getChatBySession/<id>")
def getChat(id):
    return ChatController.getChatBySession(id)

@app.post('/createChatSession')
def createChatSession():
    return ChatController.createSession()


##########--Crop Suggestions--#################

@app.get('/recommend-crop/<id>')
def recommend_crop(id):
    return RecommendationController.get_recommendations(id)

###################--Activities Suggestions--#####################
@app.post('/seedSuggestedActivities')
def seed_suggested_activities():
    return ActivitiesSuggestionsController.seed_session()

@app.get('/getSuggestedActivities/<session_id>')
def get_suggested_activities(session_id):
    return ActivitiesSuggestionsController.get_suggested(session_id)

@app.get('/getReminders/<land_id>')
def get_reminders(land_id):
    return ActivitiesSuggestionsController.get_reminders(land_id)

@app.post('/performActivity')
def perform_activity():
    return ActivitiesSuggestionsController.perform()

@app.post('/skipSuggestedActivity')
def skip_suggested_activity():
    return ActivitiesSuggestionsController.skip()

@app.put('/adjustWithWeather/<session_id>')
def adjust_with_weather(session_id):
    return ActivitiesSuggestionsController.adjust_with_weather(session_id)

@app.get('/getWeather/<city_name>')
def get_weather(city_name):
    return ActivitiesSuggestionsController.get_weather(city_name)

##################--Notifications--#######################

@app.get('/getNotifications/<farmer_id>')
def get_notifications(farmer_id):
    return ActivitiesSuggestionsController.get_notifications(farmer_id)

@app.put('/markNotificationRead/<id>')
def mark_notification_read(id):
    return ActivitiesSuggestionsController.mark_notification_read(id)

@app.put('/markAllNotificationsRead/<farmer_id>')
def mark_all_notifications_read(farmer_id):
    return ActivitiesSuggestionsController.mark_all_notifications_read(farmer_id)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True)

