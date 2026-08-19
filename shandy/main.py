import time
from game_manager import GameManager

chosen_game=int(input("""===MILEAGE WARS===
                          
1. New Game
2. Load Game

-->Your Choice: """))

g=GameManager()

while True:
    if chosen_game==1:
        choice=int(input("""\n\n====MILEAGE WARS====\n\n1. Show Cities
2. Attack City
3. Defend City
4. Add Run
5. Add Player
6. Add City
7. Save Game
8. Load Game
9. Exit\n\n-->Your Choice: """))
        
        if choice==1:
            for i in g.cities:
                print(i.name)
            time.sleep(1)

        elif choice==2:
            u=input("Enter valid username: ")
            c=input("Enter valid city name: ")
            gd=int(input("Enter goal distance: "))
            
            if u in [i.username for i in g.players] and c in [i.name for i in g.cities]:
                g.create_attack(u,c,gd)
                time.sleep(1)
            else:
                print("User and city doesn't exist")
                time.sleep(1)

        elif choice==3:
            u=input("Enter valid username: ")
            c=input("Enter valid city name: ")            
            if u in [i.username for i in g.players] and c in [i.name for i in g.cities]:
                g.create_defense(u,c)
                time.sleep(1)
            else:
                print("User and city doesn't exist")    
                time.sleep(1)      
        
        elif choice==4:
            u=input("Enter username: ")
            p=None
            for i in g.players:
                if i.username==u:
                    p=i
                    break
            if p.active_attacks==[]:
                if p.active_defenses==[]:
                    print("No active attacks or defences, create one to be able to add a run")
                    time.sleep(1)
                else:
                    defences=''
                    for i in p.active_defenses:
                        defences+=i.city.name
                    d=int(input(f"Choose your defence: \n{defences}: "))
                    selected=p.active_defenses[(d-1)]
                    selected.defend_run(int(input("Enter distance: ")))
                    time.sleep(1)

            else:
                if p.active_defenses==[]:
                    attacks=''
                    for i in p.active_attacks:
                        attacks+=i.city.name
                    a=int(input(f"Choose your attack: \n{attacks}: "))
                    selected=p.active_attacks[(a-1)]
                    selected.add_run(int(input("Enter distance: ")))
                    time.sleep(1)
                else:
                    attacks=''
                    for i in p.active_attacks:
                        attacks+=i.city.name
                    defences=''
                    for i in p.active_defenses:
                        defences+=i.city.name
                    ad=int(input("Attack(1) or Defense(2): "))
                    if ad==1:
                        a=int(input(f"Choose your attack: \n{attacks}"))
                        selected=p.active_attacks[(a-1)]
                        selected.add_run(int(input("Enter distance")))
                        time.sleep(1)
                    elif ad==2:
                        d=int(input(f"Choose your defence: \n{defences}"))
                        selected=p.active_defenses[(d-1)]
                        selected.defend_run(int(input("Enter distance: ")))
                        time.sleep(1)

        elif choice==5:
            g.add_player(input("Enter username: "),input("Enter City name: "))
            time.sleep(1)
        
        elif choice==6:
            g.create_city(input("Enter City name: "))
            time.sleep(1)

        elif choice==7:
            g.make_final_json()
            time.sleep(1)
        elif choice==8:
            g.load_json()
            time.sleep(1)
        elif choice==9:
            time.sleep(1)
            break

    elif chosen_game==2:

        g.load_json()

        while True:

            choice=int(input("""\n\n====MILEAGE WARS====\n
    1. Show Cities
    2. Attack City
    3. Defend City
    4. Add Run
    5. Add Player
    6. Add City
    7. Save Game
    8. Reload Save
    9. Exit

    -->Your Choice: """))

            if choice==1:

                for i in g.cities:
                    print(f"{i.name} | Owner: {i.new_owner.username} | HP: {i.hp}")

                time.sleep(1)

            elif choice==2:

                u=input("Enter valid username: ")
                c=input("Enter valid city name: ")
                gd=int(input("Enter goal distance: "))

                if u in [i.username for i in g.players] and c in [i.name for i in g.cities]:

                    g.create_attack(u,c,gd)

                else:
                    print("User or city doesn't exist")

                time.sleep(1)

            elif choice==3:

                u=input("Enter valid username: ")
                c=input("Enter valid city name: ")

                if u in [i.username for i in g.players] and c in [i.name for i in g.cities]:

                    g.create_defense(u,c)

                else:
                    print("User or city doesn't exist")

                time.sleep(1)

            elif choice==4:

                u=input("Enter username: ")

                p=None

                for i in g.players:
                    if i.username==u:
                        p=i
                        break

                if p is None:

                    print("Player not found")
                    time.sleep(1)
                    continue

                if p.active_attacks==[] and p.active_defenses==[]:

                    print("No active attacks or defenses")
                    time.sleep(1)

                elif p.active_attacks!=[]:

                    print("\nATTACKS:")

                    for idx,i in enumerate(p.active_attacks):
                        print(f"{idx+1}. {i.city.name}")

                    a=int(input("Choose attack: "))

                    selected=p.active_attacks[a-1]

                    dist=int(input("Enter distance: "))

                    selected.add_run(dist)

                    time.sleep(1)

                elif p.active_defenses!=[]:

                    print("\nDEFENSES:")

                    for idx,i in enumerate(p.active_defenses):
                        print(f"{idx+1}. {i.city.name}")

                    d=int(input("Choose defense: "))

                    selected=p.active_defenses[d-1]

                    dist=int(input("Enter distance: "))

                    selected.defend_run(dist)

                    time.sleep(1)

            elif choice==5:

                uname=input("Enter username: ")
                city=input("Enter city name: ")

                g.add_player(uname,city)

                time.sleep(1)

            elif choice==6:

                city=input("Enter city name: ")

                g.create_city(city)

                time.sleep(1)

            elif choice==7:

                g.make_final_json()

                print("Game saved!")

                time.sleep(1)

            elif choice==8:

                g.load_json()

                print("Save reloaded!")

                time.sleep(1)

            elif choice==9:

                print("Exiting game...")

                time.sleep(1)
                exit()       