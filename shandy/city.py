class City():
    def __init__(self,name,hp=200,old_owner=None,new_owner=None,shield_health=0):
        self.hp=hp
        self.name=name
        self.old_owner=old_owner
        self.new_owner=new_owner
        self.shield_health=shield_health

    def take_damage(self,dmg,km,attacker,used=0,extra=0):
        self.hp -= dmg
        if self not in self.new_owner.cities_to_defend:
            self.new_owner.cities_to_defend.append(self)

        if self.hp<0:
            self.hp=0
        if self.hp==0:
            self.old_owner=self.new_owner
            self.new_owner=attacker
            attacker.owned_cities.append(self)
            self.old_owner.owned_cities.remove(self)
            self.hp=200
        print(f"{attacker.username} ran {km} km\n{used} km in damage dealt\n{extra} km used as overflow bonus\nDamage: {dmg}\nRemaining HP: {self.hp}\nowner={self.new_owner.username}\n\n")

    def heal_damage(self,heal_amt,km,defender,used=0,extra=0):
        self.hp+=heal_amt
        if self.hp>200:
            bonus=self.hp-200
            self.hp=200
            self.shield_health+=bonus
        if self.hp==200 or self.hp==0:
            self.hp=200
            self.old_owner=self.new_owner
            self.new_owner=defender
            self.old_owner.owned_cities.remove(self)
            self.new_owner.cities_to_defend.remove(self)
            self.new_owner.owned_cities.append(self)
        print(f"{defender.username} ran {km} km\n{used} km in health cured\n{extra} km added to shield health\nHealth added: {abs(heal_amt)}\nNew HP: {self.hp}\nOwner: {self.new_owner.username}\n\n")

    def to_dict(self):
        json_object={'Name': self.name,'HP':self.hp,'Shield Health':self.shield_health,'Current Owner': self.new_owner.username,'Previous Owner':self.old_owner.username if self.old_owner is not None else None}
        return json_object
