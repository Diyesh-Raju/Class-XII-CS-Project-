import datetime

class Attack():

    def __init__(self,attacker,city,committed,completed=0,bonus=0,status='active',deadline=None):
        self.attacker=attacker
        self.deadline=datetime.datetime.now()+datetime.timedelta(hours=48)
        self.status=status
        self.city=city
        self.committed=committed
        self.completed=completed
        self.bonus=bonus
    
    def damage(self):
        print(f"Attacker: {self.attacker}\nCity:{self.city.name}\nCommitted KM: {self.committed}\nCompleted KM: {self.completed}")
    

    def add_run(self,dist):
        total=dist+self.completed
        rem=self.committed-self.completed
        if self.status=='active':
            curtime=datetime.datetime.now()
            if curtime<self.deadline:
                if total>=self.committed:
                    overflow=total-self.committed
                    self.completed=self.committed
                    dmg=rem*15
                    self.city.take_damage(dmg,dist,self.attacker,rem,overflow)
                    self.bonus+=overflow
                    self.status='success'

                else:
                    self.completed=total
                    dmg=dist*15
                    self.city.take_damage(dmg,dist,self.attacker,dist)
            else:
                self.status='fail'
                print('Attack failed\nDeadline reached')
        else:
            print(f'attack is already a {self.status}')
        
        self.attacker.add_coins(dist*10)
        self.attacker.add_xp(dist*5)
