import datetime

class Defend():
    def __init__(self, defender, city, required_km=0, defended_km=0, deadline=None,can_defend=None):
        self.defender=defender
        self.city=city
        if city.hp==200:
            if city.new_owner!=defender:
                self.required_km=20
            else:
                self.required_km=0
        else:
            self.required_km=(200-city.hp)/15

        if city.hp!=200 or city.shield_health!=50:
            self.can_defend=True
        else:
            self.can_defend=False
        self.defended_km=defended_km
        self.deadline=datetime.datetime.now()+datetime.timedelta(hours=72)

    def defend_run(self,dist):
        total=dist+self.defended_km
        rem=self.required_km-self.defended_km
        if self.can_defend:
            curtime=datetime.datetime.now()
            if curtime<self.deadline:
                if total>self.required_km:
                    overflow=total-self.required_km
                    self.defended_km=self.required_km
                    if self.city.hp==200:
                        heal=rem*(-10) #reclaim damage to occupied city
                    elif self.city.hp!=200 and self.city.new_owner!=self.defender:
                        heal=rem*(-10)
                    else:
                        heal=rem*10
                    self.city.heal_damage(heal,dist,self.defender,rem,overflow)
                    if self.city.hp==200 and self.city.shield_health==50:
                        self.can_defend=False

                else:
                    self.defended_km=total
                    if self.city.hp==200:
                        heal=dist*(-10) #recclaim damage to occupied city
                    else:
                        heal=dist*10
                    self.city.heal_damage(heal,dist,self.defender,dist)
            else:
                self.can_defend=False
                print(f"Deadline passed, cant defend anymore. City lost to {self.city.new_owner.username}")
        else:
            print("Cant defend city anymore")