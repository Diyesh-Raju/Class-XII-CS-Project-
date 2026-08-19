from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models.models import User, City, AttackLog, DefenseLog, GPSPoint
import datetime

fitness_bp = Blueprint('fitness', __name__)

# ==============================================================================
# 1. ATTACK ENGINE ENDPOINT
# ==============================================================================
@fitness_bp.route('/attack', methods=['POST'])
@jwt_required()
def initiate_attack():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    
    city_name = data.get('city_name')
    goal_distance = data.get('goal_distance') # km target chosen by player

    if not city_name or not goal_distance:
        return jsonify({"message": "Missing city_name or goal_distance parameters!"}), 400

    city = City.query.filter_by(name=city_name).first()
    if not city:
        return jsonify({"message": f"City '{city_name}' does not exist on the map!"}), 404

    # Validation mirroring game_manager.py: Can't launch an attack on a city you already own
    if city.new_owner_id == int(user_id):
        return jsonify({"message": "You already own this city! You can only defend it."}), 400

    # Instantiate the structural Attack record
    new_attack = AttackLog(
        goal_distance=float(goal_distance),
        committed=0.0,
        completed=False,
        bonus=0.0,
        status='ongoing',
        user_id=int(user_id),
        city_id=city.id
    )

    db.session.add(new_attack)
    db.session.commit()

    return jsonify({
        "message": f"Attack successfully declared on {city_name}!",
        "attack_id": new_attack.id,
        "target_goal": goal_distance
    }), 201


# ==============================================================================
# 2. DEFENSE ENGINE ENDPOINT (Matches rules established in defend.py)
# ==============================================================================
@fitness_bp.route('/defend', methods=['POST'])
@jwt_required()
def initiate_defense():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    
    city_name = data.get('city_name')
    if not city_name:
        return jsonify({"message": "Missing city_name parameter!"}), 400

    city = City.query.filter_by(name=city_name).first()
    if not city:
        return jsonify({"message": f"City '{city_name}' not found!"}), 404

    # Custom Teammate Logic translation from defend.py:
    # 1. If city HP is pristine (200), required defense distance depends on ownership status
    if city.hp == 200:
        required_km = 20.0 if city.new_owner_id != int(user_id) else 0.0
    else:
        # 2. If it has sustained damage, defense difficulty scale formula: (200 - hp) / 15
        required_km = (200.0 - city.hp) / 15.0

    # 3. Check if defense is legally permitted (defend.py rule: cannot defend if HP is maxed and shield is full)
    if city.hp == 200 and city.shield_health == 50:
        return jsonify({"message": "City structure and defensive energy shields are already fully maxed out!"}), 400

    new_defense = DefenseLog(
        required_km=required_km,
        defended_km=0.0,
        can_defend=True,
        user_id=int(user_id),
        city_id=city.id
    )

    db.session.add(new_defense)
    db.session.commit()

    return jsonify({
        "message": f"Defensive garrison mobilized for {city_name}!",
        "defense_id": new_defense.id,
        "required_km": round(required_km, 2),
        "deadline": new_defense.deadline.strftime('%Y-%m-%d %H:%M:%S')
    }), 201


# ==============================================================================
# 3. GPS WORKOUT SUBMISSION ENGINE (Translates running data into damage/healing)
# ==============================================================================
@fitness_bp.route('/add-run', methods=['POST'])
@jwt_required()
def add_fitness_run():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    data = request.get_json() or {}

    distance = data.get('distance') # The total kilometers completed on this workout run
    attack_id = data.get('attack_id')
    defense_id = data.get('defense_id')
    gps_coordinates = data.get('gps_points', []) # Optional telemetry trace list from Student 3

    if not distance:
        return jsonify({"message": "Missing distance value!"}), 400

    dist = float(distance)

    # --------------------------------------------------------------------------
    # CASE A: TARGETING AN ONGOING ATTACK LOG (Combines attack.py + city.py mechanics)
    # --------------------------------------------------------------------------
    if attack_id:
        attack = AttackLog.query.filter_by(id=attack_id, user_id=int(user_id), completed=False).first()
        if not attack:
            return jsonify({"message": "Active attack session not found or already completed!"}), 404

        city = City.query.get(attack.city_id)
        
        # Calculate progression thresholds
        total = dist + attack.committed
        rem = attack.goal_distance - attack.committed

        if total >= attack.goal_distance:
            # Overachievement: Attack finishes completely! 
            overflow = total - attack.goal_distance
            attack.committed = attack.goal_distance
            attack.completed = True
            attack.bonus += overflow
            attack.status = 'completed'

            # Damage metric calculation matching your project specifications
            damage_to_deal = rem * 10
            
            # Execute your teammate's core city database modification mechanics
            city.hp -= damage_to_deal
            if city.hp <= 0:
                city.hp = 200 # City collapses and resets structural HP
                city.old_owner_id = city.new_owner_id
                city.new_owner_id = user.id # Capture sequence! The attacker claims ownership

            user.xp += 50 # Reward progression experience metrics
            user.coins += 20
        else:
            # Standard incremental approach progress update
            attack.committed = total
            damage_to_deal = dist * 10
            city.hp -= damage_to_deal
            if city.hp <= 0:
                city.hp = 200
                city.old_owner_id = city.new_owner_id
                city.new_owner_id = user.id
            user.xp += 10

        # Save GPS point coordinates arrays into your system mapping table if provided
        for idx, pt in enumerate(gps_coordinates):
            point = GPSPoint(latitude=pt['lat'], longitude=pt['lng'], sequence=idx, attack_id=attack.id)
            db.session.add(point)

        db.session.commit()
        return jsonify({"status": "success", "city_hp": city.hp, "attack_status": attack.status, "user_coins": user.coins})

    # --------------------------------------------------------------------------
    # CASE B: TARGETING AN ACTIVE DEFENSE INSTANCE (Matches defend.py mechanics)
    # --------------------------------------------------------------------------
    elif defense_id:
        defense = DefenseLog.query.filter_by(id=defense_id, user_id=int(user_id), can_defend=True).first()
        if not defense:
            return jsonify({"message": "Active defense contract not found or expired!"}), 404

        # Validate teammate's 72-hour hard limit deadline restriction
        if datetime.datetime.utcnow() > defense.deadline:
            defense.can_defend = False
            db.session.commit()
            return jsonify({"message": "Defensive time limit window of 72 hours has run out!"}), 400

        city = City.query.get(defense.city_id)
        total = dist + defense.defended_km
        rem = defense.required_km - defense.defended_km

        if total >= defense.required_km:
            # Complete defense achieved!
            overflow = total - defense.required_km
            defense.defended_km = defense.required_km
            
            # Execute teammate's variable recovery modifier conditions
            heal_amount = rem * (10 if city.new_owner_id == user.id else -10)
            city.hp += heal_amount
            
            # Shield amplification handling
            if city.hp > 200:
                bonus_shield = city.hp - 200
                city.hp = 200
                city.shield_health += bonus_shield
                if city.shield_health > 50: 
                    city.shield_health = 50 # Bound to structural limit ceiling

            if city.hp == 200 and city.shield_health == 50:
                defense.can_defend = False

            user.xp += 40
            user.coins += 15
        else:
            # Incremental partial patch recovery
            defense.defended_km = total
            heal_amount = dist * (10 if city.new_owner_id == user.id else -10)
            city.hp += heal_amount
            if city.hp > 200:
                bonus_shield = city.hp - 200
                city.hp = 200
                city.shield_health += bonus_shield
                if city.shield_health > 50: city.shield_health = 50
            user.xp += 10

        for idx, pt in enumerate(gps_coordinates):
            point = GPSPoint(latitude=pt['lat'], longitude=pt['lng'], sequence=idx, defense_id=defense.id)
            db.session.add(point)

        db.session.commit()
        return jsonify({"status": "success", "city_hp": city.hp, "shield_health": city.shield_health, "defended_km": defense.defended_km})

    return jsonify({"message": "You must supply either an attack_id or defense_id to link your run details!"}), 400