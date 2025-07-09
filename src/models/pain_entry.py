from src.models.user import db
from datetime import datetime
import json

class PainEntry(db.Model):
    __tablename__ = 'pain_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False)
    intensity = db.Column(db.Integer, nullable=False)  # 0-10 scale
    location = db.Column(db.Text, nullable=True)  # JSON string for body locations
    symptoms = db.Column(db.Text, nullable=True)  # Associated symptoms
    notes = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'intensity': self.intensity,
            'location': json.loads(self.location) if self.location else [],
            'symptoms': self.symptoms,
            'notes': self.notes,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Medication(db.Model):
    __tablename__ = 'medications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    dosage = db.Column(db.String(100), nullable=True)
    frequency = db.Column(db.String(100), nullable=False)  # e.g., "8h", "12h", "daily"
    times = db.Column(db.Text, nullable=False)  # JSON string for reminder times
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'dosage': self.dosage,
            'frequency': self.frequency,
            'times': json.loads(self.times) if self.times else [],
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Therapy(db.Model):
    __tablename__ = 'therapies'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(100), nullable=False)  # breathing, relaxation, heat, etc.
    duration = db.Column(db.Integer, nullable=True)  # in minutes
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    effectiveness = db.Column(db.Integer, nullable=True)  # 1-5 scale
    notes = db.Column(db.Text, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'duration': self.duration,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'effectiveness': self.effectiveness,
            'notes': self.notes
        }

class CaregiverAccess(db.Model):
    __tablename__ = 'caregiver_access'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(100), nullable=False)
    caregiver_id = db.Column(db.String(100), nullable=False)
    access_level = db.Column(db.String(50), default='read')  # read, write, admin
    granted_at = db.Column(db.DateTime, default=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'caregiver_id': self.caregiver_id,
            'access_level': self.access_level,
            'granted_at': self.granted_at.isoformat() if self.granted_at else None,
            'active': self.active
        }

