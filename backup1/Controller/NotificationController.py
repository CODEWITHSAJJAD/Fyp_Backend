from flask import jsonify
from Model.NotificationModel import NotificationModel
from db import db

class NotificationController:
    @staticmethod
    def get_notifications(farmer_id):
        try:
            notifs = NotificationModel.query.filter(NotificationModel.farmer_id==farmer_id).order_by(NotificationModel.notification_id.desc()).all()
            Notifications=[]
            for n in notifs:
                Notifications.append({
                        'notification_id': n.notification_id,
                        'type': n.notification_type,
                        'title': n.title,
                        'message': n.message,
                        'is_read': n.is_read,
                        'created_at': n.created_at
                    })

            return jsonify(Notifications), 200
        except Exception as e:
            return jsonify(str(e)), 500

    @staticmethod
    def mark_read(notification_id):
        try:
            n = NotificationModel.query.filter(NotificationModel.notification_id==notification_id).first()
            if not n:
                return jsonify({"error": "Notification not found"}), 404
            n.is_read = True
            db.session.commit()
            return jsonify({"notification_id": notification_id, "is_read": True}), 200
        except Exception as e:
            return jsonify(str(e)), 500
