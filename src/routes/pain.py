from flask import Blueprint, request, jsonify
from src.models.pain_entry import db, PainEntry, Medication, Therapy, CaregiverAccess
from datetime import datetime, timedelta
import json

pain_bp = Blueprint('pain', __name__)

# Pain Entry Routes
@pain_bp.route('/pain-entries', methods=['POST'])
def create_pain_entry():
    try:
        data = request.get_json()
        
        pain_entry = PainEntry(
            user_id=data.get('user_id', 'default_user'),
            intensity=data.get('intensity'),
            location=json.dumps(data.get('location', [])),
            symptoms=data.get('symptoms'),
            notes=data.get('notes'),
            timestamp=datetime.fromisoformat(data.get('timestamp')) if data.get('timestamp') else datetime.utcnow()
        )
        
        db.session.add(pain_entry)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': pain_entry.to_dict(),
            'message': 'Registro de dor criado com sucesso'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao criar registro: {str(e)}'
        }), 400

@pain_bp.route('/pain-entries', methods=['GET'])
def get_pain_entries():
    try:
        user_id = request.args.get('user_id', 'default_user')
        days = request.args.get('days', 30, type=int)
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        entries = PainEntry.query.filter(
            PainEntry.user_id == user_id,
            PainEntry.timestamp >= start_date
        ).order_by(PainEntry.timestamp.desc()).all()
        
        return jsonify({
            'success': True,
            'data': [entry.to_dict() for entry in entries],
            'count': len(entries)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar registros: {str(e)}'
        }), 400

@pain_bp.route('/pain-entries/<int:entry_id>', methods=['PUT'])
def update_pain_entry(entry_id):
    try:
        data = request.get_json()
        entry = PainEntry.query.get_or_404(entry_id)
        
        entry.intensity = data.get('intensity', entry.intensity)
        entry.location = json.dumps(data.get('location', json.loads(entry.location or '[]')))
        entry.symptoms = data.get('symptoms', entry.symptoms)
        entry.notes = data.get('notes', entry.notes)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': entry.to_dict(),
            'message': 'Registro atualizado com sucesso'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao atualizar registro: {str(e)}'
        }), 400

# Medication Routes
@pain_bp.route('/medications', methods=['POST'])
def create_medication():
    try:
        data = request.get_json()
        
        medication = Medication(
            user_id=data.get('user_id', 'default_user'),
            name=data.get('name'),
            dosage=data.get('dosage'),
            frequency=data.get('frequency'),
            times=json.dumps(data.get('times', []))
        )
        
        db.session.add(medication)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': medication.to_dict(),
            'message': 'Medicamento adicionado com sucesso'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao adicionar medicamento: {str(e)}'
        }), 400

@pain_bp.route('/medications', methods=['GET'])
def get_medications():
    try:
        user_id = request.args.get('user_id', 'default_user')
        
        medications = Medication.query.filter(
            Medication.user_id == user_id,
            Medication.active == True
        ).all()
        
        return jsonify({
            'success': True,
            'data': [med.to_dict() for med in medications]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar medicamentos: {str(e)}'
        }), 400

# Therapy Routes
@pain_bp.route('/therapies', methods=['POST'])
def create_therapy():
    try:
        data = request.get_json()
        
        therapy = Therapy(
            user_id=data.get('user_id', 'default_user'),
            type=data.get('type'),
            duration=data.get('duration'),
            effectiveness=data.get('effectiveness'),
            notes=data.get('notes')
        )
        
        db.session.add(therapy)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': therapy.to_dict(),
            'message': 'Terapia registrada com sucesso'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao registrar terapia: {str(e)}'
        }), 400

@pain_bp.route('/therapies', methods=['GET'])
def get_therapies():
    try:
        user_id = request.args.get('user_id', 'default_user')
        days = request.args.get('days', 30, type=int)
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        therapies = Therapy.query.filter(
            Therapy.user_id == user_id,
            Therapy.completed_at >= start_date
        ).order_by(Therapy.completed_at.desc()).all()
        
        return jsonify({
            'success': True,
            'data': [therapy.to_dict() for therapy in therapies]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar terapias: {str(e)}'
        }), 400

# Analytics Routes
@pain_bp.route('/analytics/pain-trends', methods=['GET'])
def get_pain_trends():
    try:
        user_id = request.args.get('user_id', 'default_user')
        days = request.args.get('days', 30, type=int)
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        entries = PainEntry.query.filter(
            PainEntry.user_id == user_id,
            PainEntry.timestamp >= start_date
        ).order_by(PainEntry.timestamp.asc()).all()
        
        # Calculate trends
        daily_averages = {}
        for entry in entries:
            date_key = entry.timestamp.date().isoformat()
            if date_key not in daily_averages:
                daily_averages[date_key] = []
            daily_averages[date_key].append(entry.intensity)
        
        trends = []
        for date, intensities in daily_averages.items():
            trends.append({
                'date': date,
                'average_intensity': sum(intensities) / len(intensities),
                'max_intensity': max(intensities),
                'min_intensity': min(intensities),
                'entries_count': len(intensities)
            })
        
        return jsonify({
            'success': True,
            'data': trends,
            'summary': {
                'total_entries': len(entries),
                'average_pain': sum(entry.intensity for entry in entries) / len(entries) if entries else 0,
                'days_analyzed': days
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao calcular tendências: {str(e)}'
        }), 400

# Voice Commands Route
@pain_bp.route('/voice-command', methods=['POST'])
def process_voice_command():
    try:
        data = request.get_json()
        command = data.get('command', '').lower()
        user_id = data.get('user_id', 'default_user')
        
        response = {'success': True, 'action': None, 'message': ''}
        
        # Simple command processing
        if 'dor forte' in command or 'dor intensa' in command:
            # Create high pain entry
            pain_entry = PainEntry(
                user_id=user_id,
                intensity=8,
                notes=f'Registro por comando de voz: {command}'
            )
            db.session.add(pain_entry)
            db.session.commit()
            
            response['action'] = 'pain_recorded'
            response['message'] = 'Dor forte registrada. Que tal tentar uma terapia de respiração?'
            
        elif 'dor fraca' in command or 'pouca dor' in command:
            pain_entry = PainEntry(
                user_id=user_id,
                intensity=3,
                notes=f'Registro por comando de voz: {command}'
            )
            db.session.add(pain_entry)
            db.session.commit()
            
            response['action'] = 'pain_recorded'
            response['message'] = 'Dor leve registrada. Continue cuidando bem de você!'
            
        elif 'medicamento' in command or 'remédio' in command:
            response['action'] = 'medication_reminder'
            response['message'] = 'Vou mostrar seus medicamentos. Lembre-se de tomar conforme prescrito.'
            
        elif 'terapia' in command or 'exercício' in command:
            response['action'] = 'therapy_suggestion'
            response['message'] = 'Vou abrir as terapias guiadas para você. Escolha a que preferir.'
            
        else:
            response['message'] = 'Não entendi o comando. Tente dizer "dor forte", "medicamento" ou "terapia".'
        
        return jsonify(response), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao processar comando: {str(e)}'
        }), 400

