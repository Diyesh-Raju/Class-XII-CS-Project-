from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.models import User, City, AttackLog, DefenseLog

game_bp = Blueprint('game', __name__)

# ==============================================================================
# STEP 6: MASTER SYNC SYSTEM
# ==============================================================================
@game_bp.route('/sync', methods=['GET'])
@jwt_required()
def sync_master_state():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    
    if not user:
        return jsonify({"message": "User context not found!"}), 404

    # Fetch all cities on the map
    all_cities = City.query.all()
    cities_data = []
    for city in all_cities:
        cities_data.append({
            "id": city.id,
            "name": city.name,
            "hp": city.hp,
            "shield_health": city.shield_health,
            "owner_id": city.new_owner_id
        })

    # Fetch this specific player's ongoing attack commitments
    active_attacks = AttackLog.query.filter_by(user_id=user.id, completed=False).all()
    attacks_data = [{
        "attack_id": a.id,
        "city_id": a.city_id,
        "goal_distance": a.goal_distance,
        "committed_km": a.committed
    } for a in active_attacks]

    # Fetch this specific player's active defense contracts
    active_defenses = DefenseLog.query.filter_by(user_id=user.id, can_defend=True).all()
    defenses_data = [{
        "defense_id": d.id,
        "city_id": d.city_id,
        "required_km": d.required_km,
        "defended_km": d.defended_km,
        "deadline": d.deadline.strftime('%Y-%m-%d %H:%M:%S')
    } for d in active_defenses]

    # Compile the ultimate master state payload required by Student 2
    return jsonify({
        "player_stats": {
            "id": user.id,
            "username": user.username,
            "coins": user.coins,
            "xp": user.xp
        },
        "world_map_cities": cities_data,
        "your_active_attacks": attacks_data,
        "your_active_defenses": defenses_data
    }), 200


# ==============================================================================
# STEP 9: LIVE NOTIFICATIONS ENGINE
# ==============================================================================
@game_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_game_notifications():
    user_id = get_jwt_identity()
    
    # Generate dynamic real-time alert text items for testing based on current state data
    under_attack = AttackLog.query.filter_by(status='ongoing').all()
    
    logs = []
    # If any player is running an active siege route, let the world know
    for attack in under_attack:
        city = City.query.get(attack.city_id)
        logs.append({
            "type": "warning",
            "message": f"🚨 ALERT: Tactical siege path detected advancing on {city.name}! Structural integrity dropping!"
        })
        
    if not logs:
        logs.append({
            "type": "info",
            "message": "🕊️ All regional sectors are quiet. No active warfare runs reported."
        })

    return jsonify({
        "notifications": logs
    }), 200