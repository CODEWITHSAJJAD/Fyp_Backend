from Model.NotificationModel import NotificationModel
from db import db
from Services.DateUtils import get_current_datetime_string

class NotificationService:
    @staticmethod
    def create_notification(farmer_id, notification_type, title, message, extra_data):
        try:
            notification = NotificationModel(
                farmer_id=farmer_id,
                notification_type=notification_type,
                title=title,
                message=message,
                created_at=get_current_datetime_string(),
                extra_data=extra_data
            )
            db.session.add(notification)
            db.session.commit()
            return {"notification_id": notification.notification_id, "status": "created"}, 201
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

    @staticmethod
    def get_notifications(farmer_id):
        try:
            notifications = NotificationModel.query.filter(
                NotificationModel.farmer_id==farmer_id
            ).all()
            result = []
            for n in notifications:
                result.append({
                    "notification_id": n.notification_id,
                    "notification_type": n.notification_type,
                    "title": n.title,
                    "message": n.message,
                    "is_read": n.is_read,
                    "created_at": n.created_at,
                    "extra_data": n.extra_data
                })
            return result, 200
        except Exception as e:
            return {"error": str(e)}, 500

    @staticmethod
    def mark_as_read(notification_id):
        try:
            notification = NotificationModel.query.filter(NotificationModel.notification_id==notification_id).first()
            if not notification:
                return {"error": "Not found"}, 404
            
            notification.is_read = True
            db.session.commit()
            return {"status": "marked as read"}, 200
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

    @staticmethod
    def mark_all_as_read(farmer_id):
        try:
            NotificationModel.query.filter(
                NotificationModel.farmer_id==farmer_id,
                NotificationModel.is_read==False
            ).update({"is_read": True})
            db.session.commit()
            return {"status": "all marked as read"}, 200
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

    @staticmethod
    def delete_notification(notification_id):
        try:
            notification = NotificationModel.query.filter(NotificationModel.notification_id==notification_id).first()
            if not notification:
                return {"error": "Not found"}, 404
            
            db.session.delete(notification)
            db.session.commit()
            return {"status": "deleted"}, 200
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500