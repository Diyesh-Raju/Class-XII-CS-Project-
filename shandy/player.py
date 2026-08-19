class Player():

    def __init__(self,username,coins=0,xp=0,owned_cities=None,cities_to_defend=None,active_attacks=None,active_defenses=None):
        self.username=username
        self.coins=coins
        self.xp=xp
        if owned_cities is None:
            self.owned_cities = []
        else:
            self.owned_cities = owned_cities
        if cities_to_defend is None:
            self.cities_to_defend=[]
        else:
            self.cities_to_defend=cities_to_defend
        if active_attacks is None:
            self.active_attacks=[]
        else:
            self.active_attacks=active_attacks
        if active_defenses is None:
            self.active_defenses=[]
        else:
            self.active_defenses=active_defenses

    def add_coins(self,amt):
        self.coins+=amt
    
    def add_xp(self,amt):
        self.xp+=amt
    
    def add_city(self,city):
        self.owned_cities.append(city)
        for i in self.owned_cities:
            i.new_owner=self
    
    def to_dict(self):

        cities_owned=[i.name for i in self.owned_cities]

        cities_to_defend=[i.name for i in self.cities_to_defend]

        active_attacks=[]

        for i in self.active_attacks:
            active_attacks.append({
                "city": i.city.name,
                "committed": i.committed,
                "completed": i.completed,
                "bonus": i.bonus,
                "status": i.status
            })

        active_defenses=[]

        for i in self.active_defenses:
            active_defenses.append({
                "city": i.city.name,
                "required_km": i.required_km,
                "defended_km": i.defended_km,
                "can_defend": i.can_defend
            })

        json_obj={
            'Username':self.username,
            'Coins':self.coins,
            'XP':self.xp,
            'Cities Owned':cities_owned,
            'Cities To Defend':cities_to_defend,
            'Active Attacks':active_attacks,
            'Active Defenses':active_defenses
        }

        return json_obj