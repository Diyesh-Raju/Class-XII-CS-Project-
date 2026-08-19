from app import db
from datetime import datetime, timedelta

# ==============================================================================
# 1. PLAYER INFRASTRUCTURE (Matches player.py)
# ==============================================================================
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False) # For encrypted passwords
    coins = db.Column(db.Integer, default=0)                  # p.coins
    xp = db.Column(db.Integer, default=0)                     # p.xp
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ==============================================================================
# 2. MAP & TERRITORY INFRASTRUCTURE (Matches city.py)
# ==============================================================================
class City(db.Model):
    __tablename__ = 'cities'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    hp = db.Column(db.Integer, default=200)                   # self.hp (max 200)
    shield_health = db.Column(db.Integer, default=0)          # self.shield_health
    
    # Dual ownership trackers matching your teammate's layout
    old_owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    new_owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Relationship accessors to link them seamlessly back to the User table
    old_owner = db.relationship('User', foreign_keys=[old_owner_id])
    new_owner = db.relationship('User', foreign_keys=[new_owner_id])

# ==============================================================================
# 3. COMBAT WARFARE SUBSYSTEM (Matches game_manager.py & main.py inputs)
# ==============================================================================
class AttackLog(db.Model):
    __tablename__ = 'attack_logs'
    id = db.Column(db.Integer, primary_key=True)
    goal_distance = db.Column(db.Float, nullable=False)       # The attack's scale target
    committed = db.Column(db.Float, default=0.0)              # total km run so far
    completed = db.Column(db.Boolean, default=False)          # true/false flag
    bonus = db.Column(db.Float, default=0.0)                  # overflow bonus miles
    status = db.Column(db.String(30), default='ongoing')      # state tracking tag
    started_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=False)
    
    attacker = db.relationship('User', backref='active_attacks')
    city = db.relationship('City')

# ==============================================================================
# 4. ACTIVE DEFENSE INFRASTRUCTURE (Matches defend.py)
# ==============================================================================
class DefenseLog(db.Model):
    __tablename__ = 'defense_logs'
    id = db.Column(db.Integer, primary_key=True)
    required_km = db.Column(db.Float, default=0.0)            # dynamically assigned rule
    defended_km = db.Column(db.Float, default=0.0)            # progress tracker meter
    can_defend = db.Column(db.Boolean, default=True)          # self.can_defend
    deadline = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(hours=72)) # 72 hr clock
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=False)
    
    defender = db.relationship('User', backref='active_defenses')
    city = db.relationship('City')

# ==============================================================================
# 5. FITNESS GPS PATH SECTIONS (Support for Student 3)
# ==============================================================================
class GPSPoint(db.Model):
    __tablename__ = 'gps_points'
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    sequence = db.Column(db.Integer, nullable=False)          # Ordering the path dots
    
    # Optional flags connecting coordinates to specific actions
    attack_id = db.Column(db.Integer, db.ForeignKey('attack_logs.id'), nullable=True)
    defense_id = db.Column(db.Integer, db.ForeignKey('defense_logs.id'), nullable=True)