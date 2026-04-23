from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

def init_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        "mssql+pyodbc://sa:123456@DESKTOP-2GIJV0P\\SUQOON/fyp_ORM1"
        "?driver=ODBC Driver 17 for SQL Server"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # app.config['SQLALCHEMY_ECHO'] = True

    db.init_app(app)
