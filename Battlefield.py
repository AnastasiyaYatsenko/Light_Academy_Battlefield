import random
import time


class Unit:
    """ Base class for Soldiers and Vehicles"""
    def __init__(self, health, cooldown):
        self.hp = health
        self.cd = cooldown
        self.last_attacked = 0
        self.exp = 0


class Soldier(Unit):
    def __init__(self):
        cd = random.randint(100, 2000)
        Unit.__init__(self, 100, cd)

    def atk_success(self):
        """ Calculates the success probability of an attack """
        return 0.5*(1 + self.hp/100) * random.randint(50 + self.exp, 100)/100

    def dmg_amount(self):
        """ Calculates the amount of damage depending on the time elapsed since the last attack """
        now = int(round(time.time() * 1000))
        if now - self.last_attacked >= self.cd:
            self.last_attacked = now
            return 0.05 + self.exp / 100
        else:
            return 0.05 + self.exp / 100
            #return 0

    def attack(self, enemy):
        """ Attack function, based on attack probability """
        atk_prob = self.atk_success()
        caused_dmg = self.dmg_amount()
        success = random.randint(0, 100)
        if success <= atk_prob*100:
            enemy.damage(caused_dmg)
            self.get_exp()

    def damage(self, caused_dmg):
        """ Damage function (lowers health) """
        self.hp -= caused_dmg
        if self.hp < 0:
            self.hp = 0

    def is_active(self):
        """ Returns true, if a soldier is alive """
        if self.hp > 0:
            return True
        else:
            return False

    def get_exp(self):
        """ Increment experience """
        if self.exp < 50:
            self.exp += 1

    def strength(self):
        """ Returns amount of health """
        return self.hp


class Vehicle(Unit):
    def __init__(self):
        cd = random.randint(1000, 2000)
        Unit.__init__(self, 100, cd)
        self.oper_amount = random.randint(1, 3)
        self.operators = []
        for i in range(self.oper_amount):
            soldier = Soldier()
            self.operators.append(soldier)

    def atk_success(self):
        """ Calculates the success probability of an attack """
        atk_prob = 1
        for s in self.operators:
            atk_prob *= s.atk_success()
        atk_prob = pow(atk_prob, float(1 / self.oper_amount))
        atk_prob = atk_prob * 0.5 * (1 + self.hp / 100)
        return atk_prob

    def dmg_amount(self):
        """ Calculates the amount of damage depending on the time elapsed since the last attack """
        sum_exp = 0
        now = int(round(time.time() * 1000))
        for s in self.operators:
            sum_exp += s.exp
        caused_dmg = 0.1 + sum_exp / 100
        if now - self.last_attacked >= self.cd:
            self.last_attacked = now
            return caused_dmg
        else:
            #return 0
            return caused_dmg

    def attack(self, enemy):
        """ Attack function, based on attack probability """
        atk_prob = self.atk_success()
        caused_dmg = self.dmg_amount()
        success = random.randint(0, 100)
        if success <= atk_prob*100:
            enemy.damage(caused_dmg)
            self.get_exp()

    def damage(self, caused_dmg):
        """ Damage function (lowers health) """
        self.hp -= caused_dmg*0.6
        dmg_oper = random.randint(0, self.oper_amount-1)
        self.operators[dmg_oper].damage(caused_dmg*0.2)
        if self.oper_amount == 1:
            self.operators[dmg_oper].damage(caused_dmg * 0.2)
        else:
            for i in range(self.oper_amount):
                if i != dmg_oper:
                    self.operators[i].damage(caused_dmg*(0.2/(self.oper_amount-1)))
        if not self.is_active():
            for s in self.operators:
                s.hp = 0
        active_opers = 0
        for s in self.operators:
            if s.is_active():
                active_opers += 1
        if active_opers == 0:
            self.hp = 0

    def is_active(self):
        """ Returns true, if a vehicle is active """
        if self.hp > 0:
            return True
        else:
            return False

    def get_exp(self):
        """ Increment experience """
        for s in self.operators:
            s.get_exp()

    def strength(self):
        """ Returns average amount of health """
        sum_hp = self.hp
        for o in self.operators:
            sum_hp += o.hp
        res_hp = sum_hp/(self.oper_amount+1)
        return res_hp


class Squad:
    """ A class for squads.
    Squads are consisted out of a number of units (soldiers or vehicles), that behave as a coherent group. """
    def __init__(self, unit_amount, strategy):
        self.unit_amount = unit_amount
        self.strategy = strategy
        self.units = []
        for i in range(self.unit_amount):
            choice = random.randint(0, 1)
            if choice == 0:
                soldier = Soldier()
                self.units.append(soldier)
            else:
                vehicle = Vehicle()
                self.units.append(vehicle)

    def atk_success(self):
        """ Calculates the success probability of an attack """
        atk_prob = 1
        for u in self.units:
            atk_prob *= u.atk_success()
        atk_prob = pow(atk_prob, float(1 / self.unit_amount))
        return atk_prob

    def dmg_amount(self):
        """ Damage function (lowers health) """
        sum_dmg = 0
        for u in self.units:
            sum_dmg += u.dmg_amount()
        return sum_dmg

    def attack(self, enemy):
        """ Attack function, based on attack probability of two squads"""
        atk_prob = self.atk_success()
        caused_dmg = self.dmg_amount()
        enemy_atk_prob = enemy.atk_success()
        if atk_prob > enemy_atk_prob:
            success = random.randint(0, 100)
            if success <= atk_prob*100:
                enemy.damage(caused_dmg)
                for s in self.units:
                    s.get_exp()

    def damage(self, caused_damage):
        """ Damage function (lowers health) """
        dmg = caused_damage / self.active_amount()
        for s in self.units:
            s.damage(dmg)

    def active_amount(self):
        """ Returns amount of active units """
        active_units = 0
        for u in self.units:
            if u.is_active():
                active_units += 1
        return active_units

    def is_active(self):
        """ Returns true, if the squad contains at least one active unit """
        active_units = self.active_amount()
        if active_units == 0:
            return False
        else:
            return True

    def strength(self):
        """ Returns total amount of health """
        sum_hp = 0
        for u in self.units:
            sum_hp += u.strength()
        return sum_hp


class Army:
    """ A class for armies.
        Armies are consisted out of a number of squads, that behave as a coherent group. """
    def __init__(self, squad_amount, strategy, unit_amount):
        self.squad_amount = squad_amount
        self.strategy = strategy
        self.squads = []
        for i in range(self.squad_amount):
            squad = Squad(unit_amount, strategy)
            self.squads.append(squad)
        self.amount_units = squad_amount*unit_amount

    def choose_army_strongest(self, armies, curr_army):
        """ Strategy 'strongest' (armies) """
        max_strength = 0
        i = 0
        chosen_enemy = armies[0]
        if curr_army == 0 and len(armies) > 1:
            chosen_enemy = armies[1]
        for a in armies:
            if (i != curr_army) and (a.strength() >= max_strength):
                max_strength = a.strength()
                chosen_enemy = a
            i += 1
        return chosen_enemy

    def choose_army_weakest(self, armies, curr_army):
        """ Strategy 'weakest' (armies) """
        chosen_enemy = armies[0]
        min_strength = armies[0].strength()
        if curr_army == 0 and len(armies) > 1:
            min_strength = armies[1].strength()
            chosen_enemy = armies[1]
        i = 0
        for a in armies:
            if (i != curr_army) and (a.strength() <= min_strength):
                min_strength = a.strength()
                chosen_enemy = a
            i += 1
        return chosen_enemy

    def choose_army_random(self, armies, curr_army):
        """ Strategy 'random' (armies) """
        chosen = random.randint(0, len(armies) - 2)
        if chosen == curr_army:
            chosen = len(armies) - 1
        chosen_enemy = armies[chosen]
        return chosen_enemy

    def choose_squad_strongest(self, squad,  enemy):
        """ Strategy 'strongest' (squads) """
        chosen_enemy = enemy.squads[0]
        max_strength = enemy.squads[0].strength()
        for s in enemy.squads:
            if s.strength() >= max_strength:
                max_strength = s.strength()
                chosen_enemy = s
        squad.attack(chosen_enemy)

    def choose_squad_weakest(self, squad,  enemy):
        """ Strategy 'weakest' (squads) """
        chosen_enemy = enemy.squads[0]
        min_strength = enemy.squads[0].strength()
        for s in enemy.squads:
            if (s.strength() <= min_strength) and (s.strength() > 0):
                min_strength = s.strength()
                chosen_enemy = s
        squad.attack(chosen_enemy)

    def choose_squad_random(self, squad,  enemy):
        """ Strategy 'random' (squads) """
        chosen_enemy = random.randint(0, enemy.squad_amount-1)
        squad.attack(enemy.squads[chosen_enemy])

    def attack(self, armies, curr_army):
        """ Attack function, based on strategy """
        if armies[curr_army].strategy == "strongest":
            enemy = self.choose_army_strongest(armies, curr_army)
            for s in self.squads:
                self.choose_squad_strongest(s, enemy)
        elif armies[curr_army].strategy == "weakest":
            enemy = self.choose_army_weakest(armies, curr_army)
            for s in self.squads:
                self.choose_squad_weakest(s, enemy)
        else:
            enemy = self.choose_army_random(armies, curr_army)
            for s in self.squads:
                self.choose_squad_random(s, enemy)

    def strength(self):
        """ Returns total health """
        sum_hp = 0
        for s in self.squads:
            sum_hp += s.strength()
        return sum_hp

    def active_amount(self):
        """ Returns amount of active squads and calculate amount of active units """
        active_squads = 0
        self.amount_units = 0
        for s in self.squads:
            if s.is_active():
                active_squads += 1
                self.amount_units += s.active_amount()
        return active_squads

    def is_active(self):
        """ Returns true, if the army contains at least one active squad """
        active_squads = self.active_amount()
        if active_squads == 0:
            return False
        else:
            return True


# Initializing armies
armies_amount = int(input("The number of armies (2 <= n): "))
strategy = input("The choice of attack strategy per army (random|weakest|strongest): ")
squad_amount = int(input("The number of squads per army (2 <= n): "))
units_amount = int(input("The number of units per squad (5 <= n <= 10): "))
armies = []
for i in range(armies_amount):
    army = Army(squad_amount, strategy, units_amount)
    armies.append(army)
active_armies = armies_amount

# Main cycle of battle
j = 0
while active_armies >= 2:
    i = 0
    for army in armies:
        army.attack(armies, i)
        i += 1
    if j % 1000 == 0:
        i = 1
        for army in armies:
            amount = army.active_amount()
            print("Army №" + str(i) + ": " + str(amount) + " squads left")
            i += 1
        print("---------")
    active_armies = 0
    for army in armies:
        if army.is_active():
            active_armies += 1
    j += 1

# Determining the winner
winner = -1
i = 0
for army in armies:
    if army.is_active():
        winner = i
    i += 1
if winner > -1:
    print("Army №" + str(i) + " is a winner!")
else:
    print("There is no winner")
