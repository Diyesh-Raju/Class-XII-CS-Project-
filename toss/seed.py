from app import create_app, db
from models.models import City

def seed_game_map():
    app = create_app()
    with app.app_context():
        print("⏳ Checking game world map coordinates...")
        
        # Check if cities already exist so we don't accidentally duplicate them
        if City.query.count() == 0:
            print("🗺️ Game map is empty. Deploying regional territories...")
            
            # Creating a list of starting locations for players to battle over
            starting_cities = [
                City(name="New York", hp=200, shield_health=0),
                City(name="Los Angeles", hp=200, shield_health=0),
                City(name="Chicago", hp=200, shield_health=0),
                City(name="London", hp=200, shield_health=0),
                City(name="Tokyo", hp=200, shield_health=0),
                City(name="Paris", hp=200, shield_health=0)
            ]
            
            db.session.add_all(starting_cities)
            db.session.commit()
            print("✅ Successfully deployed 6 tactical cities onto the Mileage Wars map!")
        else:
            print("ℹ️ Cities are already populated in the database. Skipping deployment.")

if __name__ == "__main__":
    seed_game_map()
        