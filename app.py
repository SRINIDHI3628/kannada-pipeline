# from flask import Flask
# import config
# from routes.issue_routes import issue_bp

# app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER

# app.register_blueprint(issue_bp, url_prefix='/api/issues')

# if __name__ == "__main__":
#     app.run(debug=True)

from flask import Flask, jsonify
from config import Config
from models import db
from routes.issue_routes import issue_bp
from routes.map_routes import map_bp
from flask import send_from_directory
from flask_cors import CORS


app = Flask(__name__)
app.config.from_object(Config)

# CORS(app)
CORS(app, resources={r"/*": {"origins": "*"}})

db.init_app(app)

app.register_blueprint(issue_bp, url_prefix="/api/issues")
app.register_blueprint(map_bp, url_prefix="/api")

@app.route('/uploads/issues/<filename>')
def uploaded_file(filename):
    return send_from_directory('uploads/issues', filename)

@app.route("/cors-test")
def cors_test():
    return jsonify({"message": "CORS WORKING"})


if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000,debug=True)
