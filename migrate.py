from datetime import datetime
from flask import Flask
from db import db
from Model.SuggestedActivityModel import SuggestedActivityModel
from Model.NotificationModel import NotificationModel

def run_migrations(app=None):
    if app is None:
        app = Flask(__name__)
        # rely on existing app/context config; user can supply an app if loaded elsewhere
        db.init_app(app)
    with app.app_context():
        # create tables if not exist (idempotent)
        try:
            SuggestedActivityModel.__table__.create(_db.session.get_bind(), checkfirst=True)
            NotificationModel.__table__.create(_db.session.get_bind(), checkfirst=True)
            # Seed migration version acceptance could go here
            print("Migrations applied (if needed).")
        except Exception as e:
            print("Migration failed:", e)

if __name__ == '__main__':
    run_migrations()
