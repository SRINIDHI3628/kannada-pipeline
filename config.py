# SQLALCHEMY_DATABASE_URI = "postgresql://postgres:YOUR_PASSWORD@localhost:5432/civic_reporting_db"
# SQLALCHEMY_TRACK_MODIFICATIONS = False
# UPLOAD_FOLDER = 'uploads/issues'




# import os

# class Config:
#     # SQLALCHEMY_DATABASE_URI = "postgresql://pgadmin4:Nidhi@3628@localhost:5432/civic_reporting"
#     SQLALCHEMY_DATABASE_URI = "postgresql://postgres:3628@localhost:5432/civic_reporting"

#     SQLALCHEMY_TRACK_MODIFICATIONS = False

#     UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads", "issues")



from urllib.parse import quote_plus
import os

class Config:
    DB_USERNAME = "postgres"
    DB_PASSWORD = quote_plus("Nidhi@3628")   # 🔴 replace with your REAL password
    DB_HOST = "localhost"
    DB_PORT = "5432"
    DB_NAME = "civic_reporting"               # 🔴 replace with your DB name

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{DB_USERNAME}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads", "issues")
