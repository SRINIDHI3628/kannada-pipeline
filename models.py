from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
import uuid

db = SQLAlchemy()

class CivicIssue(db.Model):
    __tablename__ = "civic_issues"

    issue_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = db.Column(db.String(50))
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)

    image_path = db.Column(db.String(255))

    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    department = db.Column(db.String(50))
    status = db.Column(db.String(20))

    ai_confidence = db.Column(db.Float)

    created_at = db.Column(db.DateTime)
    image_hash = db.Column(db.String(64))
    ai_caption = db.Column(db.Text)
    
class GovernmentOffice(db.Model):
    __tablename__ = "government_offices"

    office_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    department = db.Column(db.String(50))
    office_name = db.Column(db.String(100))
    # type = db.Column(db.String(50))  # PWD, Municipal, Police, etc.
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    contact_email= db.Column(db.String(100))
    contact_phone =db.Column(db.String(15))
    
class IssueStatusHistory(db.Model):
    __tablename__ = "issue_status_history"

    history_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    issue_id = db.Column(UUID(as_uuid=True), nullable=False)

    old_status = db.Column(db.String(20))
    new_status = db.Column(db.String(20))

    changed_by = db.Column(db.String(50))   # official/admin id
    timestamp = db.Column(db.DateTime)

class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.String(50), primary_key=True)
    role = db.Column(db.String(20))
