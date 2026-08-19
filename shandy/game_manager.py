import datetime
import random
import json
import time
from player import Player
from attack import Attack
from defend import Defend
from city import City


class GameManager():

    def __init__(self,players=None,bots=None,cities=None,attacks=None,defenses=None,player_json=None,city_json=None,final_json=None):

        self.bots=[]
        self.player_json=[]
        self.city_json=[]
        self.final_json={}
        self.players=[]
        self.cities=[]
        self.attacks=[]
        self.defenses=[]

    def add_player(self, uname, city):
        
        player = Player(username=uname)
        found_city = None
        for i in self.cities:
            if i.name == city:
                found_city = i
                break

        if found_city is None:
            found_city = City(city)
            self.cities.append(found_city)

        player.owned_cities.append(found_city)
        found_city.new_owner = player
        self.players.append(player)
        c = [i.name for i in player.owned_cities]
        print(f"Player added with username {player.username} and owner of {c}")

    def create_attack(self,uname,city,goal_dist):
        atk=None
        player=None
        target=None
        for i in self.players:
            if i.username==uname:
                player=i
                break
        
        for i in self.cities:
            if i.name==city:
                if i in player.owned_cities:
                    print("You own this city, cant attack it")
                else:
                    target=i
                    atk=Attack(player,target,goal_dist)
                    print(f"Attack created by {player.username} on {target.name} with a goal of {goal_dist} km")
                    player.active_attacks.append(atk)
                    break
        
        if atk is not None:
            self.attacks.append(atk)
        return atk

    def create_city(self,name):
        new_bot=Player(f"Bot {random.randint(1,999)}")
        old_bot=Player(f"Bot {random.randint(1000,2000)}")
        x=City(name=name)
        x.new_owner=new_bot
        self.cities.append(x)
        new_bot.owned_cities.append(x)
        self.bots.append(new_bot)
        self.bots.append(old_bot)
    
    def create_defense(self,uname,city):
        
        defense=None
        player=None
        defending_city=None
        
        for i in self.players:
            if i.username==uname:
                player=i
                break
        print(player.cities_to_defend)
        for i in self.cities:
            if i.name==city:
                if i not in player.cities_to_defend:
                    print("This city cant be defended by you right now.")
                else:
                    defending_city=i
                    defense=Defend(player,defending_city)
                    player.active_defenses.append(defense)
                    print(f"Defence created by {player.username} for {defending_city.name} with a goal of {defense.required_km} km to defend")

        if defense is not None:
            self.defenses.append(defense)
        return defense
    
    def player_to_json(self,uname):
        p=None
        for i in self.players + self.bots:
            if i.username==uname:
                p=i
                break
        self.player_json.append(p.to_dict())
        #print(self.player_json,end='\n\n')

    def city_to_json(self,name):
        c=None
        for i in self.cities:
            if i.name==name:
                c=i
                break
        self.city_json.append(c.to_dict())
        #print(self.city_json,end='\n\n')

    def make_final_json(self):
        self.player_json=[]
        self.city_json=[]
        for i in (self.players+self.bots):
            self.player_to_json(i.username)
        for i in self.cities:
            self.city_to_json(i.name)
        self.final_json={"players":self.player_json,'cities':self.city_json}
        with open("savegame.json","w") as f:
            json.dump(self.final_json,f,indent=2)
        print("json file created!")
    
    def load_json(self):
        self.players = []
        self.cities = []
        self.attacks=[]
        self.defenses=[]
        with open("savegame.json","r") as f:
            data=json.load(f)
        
        #load players
        player_data=data["players"]
        for i in player_data:
            p=Player(username=i["Username"],coins=i["Coins"],xp=i["XP"],owned_cities=[])
            self.players.append(p)
        
        #load cities
        city_data=data["cities"]
        for i in city_data:
            c=City(name=i["Name"],hp=i["HP"],old_owner=None,new_owner=None,shield_health=i["Shield Health"])
            self.cities.append(c)

        #connect city-player

        for i in player_data:
            p=None
            for k in self.players:
                if k.username==i["Username"]:
                    p=k
                    break
            c=i["Cities Owned"]
            cty=None
            for j in self.cities:
                for k in c:
                    if j.name==k:
                        p.owned_cities.append(j)
        
        for i in city_data:
            c=None
            for k in self.cities:
                if k.name==i["Name"]:
                    c=k
                    break
            old=i["Previous Owner"]
            new=i["Current Owner"]
            for j in self.players:
                if j.username == old:
                    c.old_owner=j
                elif j.username==new:
                    c.new_owner=j
        
        for i in player_data:

            p=None

            for j in self.players:
                if j.username==i["Username"]:
                    p=j
                    break

            defend_list=i["Cities To Defend"]

            for city_name in defend_list:

                for city in self.cities:

                    if city.name==city_name:
                        p.cities_to_defend.append(city)
                
        for i in player_data:

            p=None

            for j in self.players:
                if j.username==i["Username"]:
                    p=j
                    break

            atk_data=i["Active Attacks"]

            for atk in atk_data:

                target_city=None

                for city in self.cities:
                    if city.name==atk["city"]:
                        target_city=city
                        break

                a=Attack(
                    attacker=p,
                    city=target_city,
                    committed=atk["committed"],
                    completed=atk["completed"],
                    bonus=atk["bonus"],
                    status=atk["status"]
                )

                p.active_attacks.append(a)

                self.attacks.append(a)
        
        for i in player_data:

            p=None

            for j in self.players:
                if j.username==i["Username"]:
                    p=j
                    break

            defense_data=i["Active Defenses"]

            for d in defense_data:

                target_city=None

                for city in self.cities:
                    if city.name==d["city"]:
                        target_city=city
                        break

                defense=Defend(
                    defender=p,
                    city=target_city,
                    defended_km=d["defended_km"],
                    can_defend=d["can_defend"]
                )

                defense.required_km=d["required_km"]

                p.active_defenses.append(defense)

                self.defenses.append(defense)
