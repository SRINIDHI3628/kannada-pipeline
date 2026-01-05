from flask import Blueprint, request, jsonify
from models import db, CivicIssue
from datetime import datetime
import uuid
import os
from flask import current_app
from werkzeug.utils import secure_filename
from models import db, CivicIssue , IssueStatusHistory
# from services.ai_service import get_ai_prediction
from services.hash_service import compute_image_hash
from .map_routes import haversine
from services.auth_service import role_required
from services.ai_service import get_ai_caption
from services.caption_mapper import infer_category_from_caption



print("✅ issue_routes.py LOADED")


issue_bp = Blueprint("issue_bp", __name__)

# Simple rule-based department mapping
DEPARTMENT_MAP = {
    "pothole": "PWD",
    "garbage": "Municipal",
    "water leakage": "Water Board",
    "streetlight": "Electricity Dept"
}

@issue_bp.route("/report", methods=["POST"])
def report_issue():
    try:
        data = request.json

        # 1️⃣ Extract fields safely
        category = data.get("category")
        if not category:
            return jsonify({"error": "Category is required"}), 400

        department = DEPARTMENT_MAP.get(category.lower(), "General")

        # 2️⃣ Create ORM object (NO manual UUID)
        issue = CivicIssue(
            user_id=data.get("user_id"),
            category=category,
            description=data.get("description"),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            department=department,
            status="Reported",
            created_at=datetime.now()
        )

        # 3️⃣ Save to DB
        db.session.add(issue)
        db.session.commit()

        # 4️⃣ SUCCESS response
        return jsonify({
            "message": "Issue reported successfully",
            "issue_id": str(issue.issue_id)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500



# ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

# def allowed_file(filename):
#     return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# @issue_bp.route("/upload-image/<issue_id>", methods=["POST"])
# def upload_image(issue_id):

#     if "image" not in request.files:
#         return jsonify({"error": "No image file"}), 400

#     file = request.files["image"]

#     if file.filename == "":
#         return jsonify({"error": "Empty filename"}), 400

#     if file and allowed_file(file.filename):
#         filename = secure_filename(file.filename)
#         filename = f"{issue_id}_{filename}"

#         save_path = os.path.join(
#             current_app.config["UPLOAD_FOLDER"], filename
#         )
#         file.save(save_path)

#         issue = CivicIssue.query.get(issue_id)
#         if not issue:
#             return jsonify({"error": "Issue not found"}), 404

#         issue.image_path = save_path
#         db.session.commit()

#         return jsonify({"message": "Image uploaded successfully"}), 200
    
    
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@issue_bp.route("/upload-image/<issue_id>", methods=["POST"])
def upload_image(issue_id):
    try:
        issue_id = issue_id.strip()
        # 1️⃣ Check file presence
        if "image" not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        file = request.files["image"]

        if file.filename == "":
            return jsonify({"error": "Empty filename"}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type"}), 400

        # 2️⃣ Ensure upload folder exists
        upload_folder = current_app.config["UPLOAD_FOLDER"]
        os.makedirs(upload_folder, exist_ok=True)

        # 3️⃣ Create unique filename
        ext = file.filename.rsplit(".", 1)[1].lower()
        filename = f"{issue_id}.{ext}"
        
        
        # save_path = os.path.join(upload_folder, filename)
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

        file.save(save_path)
        
        # issue.image_path = f"uploads/issues/{filename}"

        # db.session.commit()

        # 4️⃣ Fetch issue (UUID-safe)
        issue = CivicIssue.query.filter_by(issue_id=uuid.UUID(issue_id)).first()
        if not issue:
            return jsonify({"error": "Issue not found"}), 404
        
        # store hash
        
        issue.image_path = f"uploads/issues/{filename}"

        db.session.commit()
        
        
        image_hash = compute_image_hash(issue.image_path)
        issue.image_hash = image_hash
        
        duplicate_id = is_duplicate_issue(issue)

        if duplicate_id:
           issue.status = "Duplicate"
           issue.department = "Merged"

        db.session.commit()
        if duplicate_id:
           return jsonify({
        "message": "Duplicate issue detected",
        "duplicate_of": str(duplicate_id)
    }), 200

        
        # ai get prediction 
        # prediction = get_ai_prediction(issue.image_path)

        # issue.category = prediction["issue"]
        # issue.ai_confidence = prediction["confidence"]
        # 🔹 AI Caption Generation
        caption = get_ai_caption(issue.image_path)
        issue.ai_caption = caption

# 🔹 Infer category from caption
        category = infer_category_from_caption(caption)
        issue.category = category

        # if issue.ai_confidence >= 0.75:
        #    issue.department = DEPARTMENT_MAP.get(issue.category, "General")
        # else:
        #    issue.department = "Manual Review"
        
        # 🔹 Department assignment
        if category in DEPARTMENT_MAP:
              issue.department = DEPARTMENT_MAP[category]
        else:
             issue.department = "Manual Review"

        db.session.commit()


        # 5️⃣ Update DB
        # issue.image_path = save_path
        # issue.image_path = os.path.relpath(save_path)
        
        
        
    #     issue.image_path = f"uploads/issues/{filename}"

    #     db.session.commit()
        
        
    #     image_hash = compute_image_hash(issue.image_path)
    #     issue.image_hash = image_hash
        
    #     duplicate_id = is_duplicate_issue(issue)

    #     if duplicate_id:
    #        issue.status = "Duplicate"
    #        issue.department = "Merged"

    #     db.session.commit()
    #     if duplicate_id:
    #        return jsonify({
    #     "message": "Duplicate issue detected",
    #     "duplicate_of": str(duplicate_id)
    # }), 200

        return jsonify({
            "message": "Image uploaded successfully",
            "image_path": save_path
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500    


def is_duplicate_issue(issue):
    duplicates = CivicIssue.query.filter_by(
        image_hash=issue.image_hash
    ).all()

    for dup in duplicates:
        if dup.issue_id == issue.issue_id:
            continue

        distance = haversine(
            issue.latitude, issue.longitude,
            dup.latitude, dup.longitude
        )

        if distance <= 0.05:  # 50 meters
            return dup.issue_id

    return None

    
@issue_bp.route("/", methods=["GET"])
def get_issues():
    status = request.args.get("status")
    category = request.args.get("category")

    query = CivicIssue.query

    if status:
        query = query.filter_by(status=status)

    if category:
        query = query.filter_by(category=category)

    issues = query.all()

    result = []
    for issue in issues:
        result.append({
            "issue_id": str(issue.issue_id),   # 🔴 UUID → string
            "category": issue.category,
            "latitude": issue.latitude,
            "longitude": issue.longitude,
            "status": issue.status,
            "image_path": issue.image_path
        })

    return jsonify(result), 200

ALLOWED_STATUSES = ["Reported", "In Progress", "Resolved", "Rejected"]

@issue_bp.route("/<issue_id>/status", methods=["PUT"])
@role_required(["official", "admin"])
def update_status(issue_id):
    try:
        issue_id = issue_id.strip()
        data = request.json

        new_status = data.get("new_status")
        changed_by = data.get("changed_by")

        if new_status not in ALLOWED_STATUSES:
            return jsonify({"error": "Invalid status"}), 400

        issue = CivicIssue.query.filter_by(
            issue_id=uuid.UUID(issue_id)
        ).first()

        if not issue:
            return jsonify({"error": "Issue not found"}), 404

        old_status = issue.status
        issue.status = new_status

        history = IssueStatusHistory(
            issue_id=issue.issue_id,
            old_status=old_status,
            new_status=new_status,
            changed_by=changed_by,
            timestamp=datetime.now()
        )

        db.session.add(history)
        db.session.commit()

        return jsonify({
            "message": "Status updated successfully",
            "old_status": old_status,
            "new_status": new_status
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# @issue_bp.route("/<issue_id>/status", methods=["PUT"])
# def update_status(issue_id):
#     return {
#         "message": "STATUS ROUTE HIT",
#         "issue_id": issue_id
#     }, 200

    
@issue_bp.route("/<issue_id>/timeline", methods=["GET"])
def issue_timeline(issue_id):
    issue_id = issue_id.strip()

    history = IssueStatusHistory.query.filter_by(
        issue_id=uuid.UUID(issue_id)
    ).order_by(IssueStatusHistory.timestamp).all()

    timeline = []
    for h in history:
        timeline.append({
            "old_status": h.old_status,
            "new_status": h.new_status,
            "changed_by": h.changed_by,
            "timestamp": h.timestamp
        })

    return jsonify(timeline), 200
  

@issue_bp.route("/test", methods=["GET"])
def test():
    return jsonify({"message": "issue blueprint working"})

@issue_bp.route("/ping", methods=["GET"])
def ping():
    return {"message": "issue blueprint alive"}, 200



