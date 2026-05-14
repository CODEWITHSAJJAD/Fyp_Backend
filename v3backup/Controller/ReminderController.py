from flask import jsonify
from Services.RemindrsService import RemindersService
class ReminderController:
    @staticmethod
    def get_reminders(land_id):
        res, code = RemindersService.get_reminders(land_id)
        return jsonify(res), code

    @staticmethod
    def get_alerts(land_id):
        res,code=RemindersService.get_Disease_and_pest_Alerts(land_id)
        return jsonify(res), code
