from Services.NotificationService import NotificationService
from Services.DateUtils import get_current_datetime_string

class NotificationHelper:
    """Helper class for creating common notifications"""
    
    @staticmethod
    def notify_farmer(farmer_id, title, message, notif_type="general", extra_data=None):
        """Create a notification for farmer"""
        return NotificationService.create_notification(
            farmer_id=farmer_id,
            notification_type=notif_type,
            title=title,
            message=message,
            extra_data=extra_data
        )
    
    @staticmethod
    def welcome_notification(farmer_id, farmer_name):
        """Welcome notification for new farmer"""
        return NotificationHelper.notify_farmer(
            farmer_id=farmer_id,
            title="Welcome to Kisan Guide!",
            message=f"Assalam-o-Alaikum {farmer_name}! Welcome to our agriculture system. Add your first land to start tracking crops.",
            notif_type="welcome"
        )
    
    @staticmethod
    def login_notification(farmer_id, device_info=None):
        """Login notification"""
        msg = "You have logged in successfully."
        if device_info:
            msg += f" Device: {device_info}"
        
        return NotificationHelper.notify_farmer(
            farmer_id=farmer_id,
            title="Login Successful",
            message=msg,
            notif_type="login",
            extra_data={"device": device_info}
        )

    @staticmethod
    def Setting_notification(farmer_id, device_info=None):
        """Settings notification"""
        msg = "Profile updated successfully."
        if device_info:
            msg += f" Device: {device_info}"

        return NotificationHelper.notify_farmer(
            farmer_id=farmer_id,
            title="Profile Updated",
            message=msg,
            notif_type="Settings",
            extra_data={"device": device_info}
        )
    
    @staticmethod
    def land_added_notification(farmer_id, land_name, location):
        """Notification when new land is added"""
        return NotificationHelper.notify_farmer(
            farmer_id=farmer_id,
            title="Land Added Successfully",
            message=f"Your land '{land_name}' has been added at {location}. You can now start a cultivation session.",
            notif_type="land_added",
            extra_data={"land_name": land_name, "location": location}
        )
    
    @staticmethod
    def land_updated_notification(farmer_id, land_name):
        """Notification when land is updated"""
        return NotificationHelper.notify_farmer(
            farmer_id=farmer_id,
            title="Land Updated",
            message=f"Your land '{land_name}' has been updated successfully.",
            notif_type="land_updated"
        )
    
    @staticmethod
    def land_deleted_notification(farmer_id, land_name):
        """Notification when land is deleted"""
        return NotificationHelper.notify_farmer(
            farmer_id=farmer_id,
            title="Land Removed",
            message=f"Your land '{land_name}' has been removed from your account.",
            notif_type="land_deleted"
        )
    
    @staticmethod
    def session_started_notification(farmer_id, crop_name, land_name):
        """Notification when cultivation session starts"""
        return NotificationHelper.notify_farmer(
            farmer_id=farmer_id,
            title="Cultivation Started",
            message=f"Cultivation for {crop_name} has been started on {land_name}. Activities have been generated.",
            notif_type="session_started",
            extra_data={"crop": crop_name, "land": land_name}
        )
    
    @staticmethod
    def activity_performed_notification(farmer_id, activity_name, crop_name):
        """Notification when activity is performed"""
        return NotificationHelper.notify_farmer(
            farmer_id=farmer_id,
            title="Activity Completed",
            message=f"{activity_name} for {crop_name} has been marked as completed.",
            notif_type="activity_completed",
            extra_data={"activity": activity_name, "crop": crop_name}
        )
    
    @staticmethod
    def activity_postponed_notification(farmer_id, activity_name, new_date, reason):
        """Notification when activity is postponed due to weather"""
        return NotificationHelper.notify_farmer(
            farmer_id=farmer_id,
            title="Activity Postponed",
            message=f"{activity_name} has been postponed to {new_date}. Reason: {reason}",
            notif_type="activity_postponed",
            extra_data={"activity": activity_name, "new_date": new_date, "reason": reason}
        )
    
    @staticmethod
    def activity_reminder_notification(farmer_id, activity_name, days_left):
        """Notification for upcoming activity"""
        msg = f"Reminder: {activity_name} is due in {days_left} day(s)."
        if days_left == 1:
            msg = f"Reminder: {activity_name} is due tomorrow!"
        elif days_left == 0:
            msg = f"Reminder: {activity_name} is due today!"
        
        return NotificationHelper.notify_farmer(
            farmer_id=farmer_id,
            title="Activity Reminder",
            message=msg,
            notif_type="activity_reminder",
            extra_data={"activity": activity_name, "days_left": days_left}
        )
    
    @staticmethod
    def session_harvested_notification(farmer_id, crop_name, yield_amount):
        """Notification when harvest is completed"""
        return NotificationHelper.notify_farmer(
            farmer_id=farmer_id,
            title="Harvest Completed",
            message=f"Harvest for {crop_name} completed! Yield: {yield_amount}",
            notif_type="harvest_completed",
            extra_data={"crop": crop_name, "yield": yield_amount}
        )
    
    @staticmethod
    def neighbor_request_notification(farmer_id, neighbor_name):
        """Notification for neighbor request"""
        return NotificationHelper.notify_farmer(
            farmer_id=farmer_id,
            title="New Neighbor Request",
            message=f"{neighbor_name} wants to connect as neighbor.",
            notif_type="neighbor_request"
        )
    
    @staticmethod
    def neighbor_accepted_notification(farmer_id, neighbor_name):
        """Notification when neighbor request is accepted"""
        return NotificationHelper.notify_farmer(
            farmer_id=farmer_id,
            title="Neighbor Request Accepted",
            message=f"{neighbor_name} accepted your neighbor request.",
            notif_type="neighbor_accepted"
        )