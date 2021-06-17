import random
import time
from abc import ABCMeta, abstractmethod
import yaml


class Unit(metaclass=ABCMeta):
    """ Base class for Soldiers and Vehicles

    Attributes
    ----------
    hp : int
        amount of health points
    cd : int
        number of ms required to recharge the unit for an attack
    last_attacked : int
        time of the last attack in milliseconds since epoch
    exp : int
        amount of experience

    """

    def __init__(self, health, cooldown):
        self.hp = health
        self.cd = cooldown
        self.last_attacked = 0
        self.exp = 0

    @abstractmethod
    def attack(self, enemy):
        """ Attack function, based on attack probability

        """
        pass

    @abstractmethod
    def damage(self, caused_dmg):
        """ Damage function (lowers health)

        """
        pass

    @abstractmethod
    def get_exp(self):
        """ Increment experience

        """
        pass

    @abstractmethod
    def atk_success(self):
        """ Calculates the success probability of an attack

        """
        pass

    @abstractmethod
    def dmg_amount(self):
        """ Calculates the amount of damage depending on the time
        elapsed since the last attack

        """
        pass

    @property
    @abstractmethod
    def is_active(self):
        """ Returns true, if a soldier is alive

        """
        pass

    @property
    @abstractmethod
    def strength(self):
        """ Returns amount of health

        """
        pass


class Soldier(Unit):
    """ A class used to represent a Soldier

    Attributes
    ----------
    hp : int
        amount of health points
    cd : int
        number of ms required to recharge the unit for an attack
    last_attacked : int
        time of the last attack in milliseconds since epoch
    exp : int
        amount of experience
    name : str
        type of unit (soldier)

    """

    def __init__(self):
        cd = random.randint(100, 2000)
        Unit.__init__(self, 100, cd)
        self.name = "soldier"

    def attack(self, enemy):
        """ Attack function, based on attack probability

        """
        atk_prob = self.atk_success()
        caused_dmg = self.dmg_amount()
        success = random.randint(0, 100)
        if success <= atk_prob * 100:
            enemy.damage(caused_dmg)
            self.get_exp()

    def damage(self, caused_dmg):
        """ Damage function (lowers health)

        """
        self.hp -= caused_dmg
        if self.hp < 0:
            self.hp = 0

    def get_exp(self):
        """ Increment experience

        """
        if self.exp < 50:
            self.exp += 1

    def atk_success(self):
        """ Calculates the success probability of
        an attack

        """
        random_part = random.randint(50 + self.exp, 100) / 100
        return 0.5 * (1 + self.hp / 100) * random_part

    def dmg_amount(self):
        """ Calculates the amount of damage depending on the time
        elapsed since the last attack

        """
        now = int(round(time.time() * 1000))
        if now - self.last_attacked >= self.cd:
            self.last_attacked = now
            return 0.05 + self.exp / 100
        else:
            return 0.05 + self.exp / 100

    def is_active(self):
        """ Returns true, if a soldier is alive """
        return self.hp > 0

    def strength(self):
        """ Returns amount of health """
        return self.hp


class Vehicle(Unit):
    """ A class used to represent a Vehicle

    Attributes
    ----------
    hp : int
        amount of health points
    cd : int
        number of ms required to recharge the unit for an attack
    last_attacked : int
        time of the last attack in milliseconds since epoch
    exp : int
        amount of experience
    name : str
        type of unit (vehicle)

     """

    def __init__(self):
        cd = random.randint(1000, 2000)
        Unit.__init__(self, 100, cd)
        self.oper_amount = random.randint(1, 3)
        self.operators = []
        for i in range(self.oper_amount):
            soldier = Soldier()
            self.operators.append(soldier)
        self.name = "vehicle"

    def active_opers(self):
        active_opers = 0
        for s in self.operators:
            if s.is_active():
                active_opers += 1
        return active_opers

    def attack(self, enemy):
        """ Attack function, based on attack probability

        """
        atk_prob = self.atk_success()
        caused_dmg = self.dmg_amount()
        success = random.randint(0, 100)
        if success <= atk_prob * 100:
            enemy.damage(caused_dmg)
            self.get_exp()

    def damage(self, caused_dmg):
        """ Damage function (lowers health)

        """
        self.hp -= caused_dmg * 0.6
        if self.hp < 0:
            self.hp = 0
        dmg_oper = random.randint(0, self.oper_amount - 1)
        self.operators[dmg_oper].damage(caused_dmg * 0.2)
        if self.oper_amount == 1:
            self.operators[dmg_oper].damage(caused_dmg * 0.2)
        else:
            oper_damage = caused_dmg * (0.2 / (self.oper_amount - 1))
            for i in range(self.oper_amount):
                if i != dmg_oper:
                    self.operators[i].damage(oper_damage)
        if not self.is_active():
            for s in self.operators:
                s.hp = 0
        if self.active_opers() == 0:
            self.hp = 0

    def get_exp(self):
        """ Increment experience

        """
        for s in self.operators:
            s.get_exp()

    def atk_success(self):
        """ Calculates the success probability of an attack

        """
        atk_prob = 1
        for s in self.operators:
            if s.is_active():
                atk_prob *= s.atk_success()
        atk_prob = pow(atk_prob, float(1 / self.active_opers()))
        atk_prob = atk_prob * 0.5 * (1 + self.hp / 100)
        return atk_prob

    def dmg_amount(self):
        """ Calculates the amount of damage depending on the time elapsed since the last attack

        """
        sum_exp = 0
        now = int(round(time.time() * 1000))
        for s in self.operators:
            if s.is_active():
                sum_exp += s.exp
        caused_dmg = 0.1 + sum_exp / 100
        if now - self.last_attacked >= self.cd:
            self.last_attacked = now
            return caused_dmg
        else:
            return caused_dmg

    def is_active(self):
        """ Returns true, if a vehicle is active

        """
        return self.hp > 0

    def strength(self):
        """ Returns average amount of health

        """
        sum_hp = self.hp
        for o in self.operators:
            sum_hp += o.hp
        res_hp = sum_hp / (self.oper_amount + 1)
        return res_hp


class Squad:
    """ A class for squads.
    Squads are consisted out of a number of units (soldiers
    or vehicles), that behave as a coherent group.

    Attributes
    ----------
    unit_amount : int
        amount of units
    strategy : str
        squad strategy
    units : int
        list of units

    """

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
        """ Calculates the success probability of an attack

        """
        atk_prob = 0
        if self.active_amount() > 0:
            atk_prob = 1
            for u in self.units:
                if u.is_active():
                    atk_prob *= u.atk_success()
            atk_prob = pow(atk_prob, float(1 / self.active_amount()))
        return atk_prob

    def dmg_amount(self):
        """ Damage function (lowers health)

        """
        sum_dmg = 0
        for u in self.units:
            sum_dmg += u.dmg_amount()
        return sum_dmg

    def attack(self, enemy):
        """ Attack function, based on attack probability of two squads

        """
        atk_prob = self.atk_success()
        caused_dmg = self.dmg_amount()
        enemy_atk_prob = enemy.atk_success()
        if atk_prob > enemy_atk_prob:
            success = random.randint(0, 100)
            if success <= atk_prob * 100:
                enemy.damage(caused_dmg)
                for s in self.units:
                    s.get_exp()

    def damage(self, caused_damage):
        """ Damage function (lowers health)

        """
        if self.is_active():
            dmg = caused_damage / self.active_amount()
            for s in self.units:
                s.damage(dmg)

    def active_amount(self):
        """ Returns amount of active units

        """
        active_units = 0
        for u in self.units:
            if u.is_active():
                active_units += 1
        return active_units

    def is_active(self):
        """ Returns true, if the squad contains at least
        one active unit
        """
        active_units = self.active_amount()
        return active_units > 0

    def strength(self):
        """ Returns total amount of health

        """
        sum_hp = 0
        for u in self.units:
            sum_hp += u.strength()
        return sum_hp


def choose_army_strongest(user_armies, curr_army):
    """ Strategy 'strongest' (armies)

    """
    max_strength = 0
    i = 0
    chosen_enemy = user_armies[0]
    if curr_army == 0 and len(user_armies) > 1:
        chosen_enemy = user_armies[1]
    for a in user_armies:
        if (i != curr_army) and (a.strength() >= max_strength):
            max_strength = a.strength()
            chosen_enemy = a
        i += 1
    return chosen_enemy


def choose_army_weakest(user_armies, curr_army):
    """ Strategy 'weakest' (armies)

    """
    chosen_enemy = user_armies[0]
    min_strength = user_armies[0].strength()
    if curr_army == 0 and len(user_armies) > 1:
        min_strength = user_armies[1].strength()
        chosen_enemy = user_armies[1]
    i = 0
    for a in user_armies:
        if (i != curr_army) and (a.strength() <= min_strength):
            min_strength = a.strength()
            chosen_enemy = a
        i += 1
    return chosen_enemy


def choose_army_random(user_armies, curr_army):
    """ Strategy 'random' (armies)

    """
    chosen = random.randint(0, len(user_armies) - 2)
    if chosen == curr_army:
        chosen = len(user_armies) - 1
    chosen_enemy = user_armies[chosen]
    return chosen_enemy


def attack_squad_strongest(squad, enemy):
    """ Strategy 'strongest' (squads)

    """
    chosen_enemy = enemy.squads[0]
    max_strength = enemy.squads[0].strength()
    for s in enemy.squads:
        if s.strength() >= max_strength:
            max_strength = s.strength()
            chosen_enemy = s
    squad.attack(chosen_enemy)


def attack_squad_weakest(squad, enemy):
    """ Strategy 'weakest' (squads)

    """
    chosen_enemy = enemy.squads[0]
    min_strength = enemy.squads[0].strength()
    for s in enemy.squads:
        if (s.strength() <= min_strength) and (s.strength() > 0):
            min_strength = s.strength()
            chosen_enemy = s
    squad.attack(chosen_enemy)


def attack_squad_random(squad, enemy):
    """ Strategy 'random' (squads)

    """
    chosen_enemy = random.randint(0, enemy.squad_amount - 1)
    squad.attack(enemy.squads[chosen_enemy])


ARMY_STRATEGY = {"strongest": choose_army_strongest,
                 "weakest": choose_army_weakest,
                 "random": choose_army_random}
SQUAD_STRATEGY = {"strongest": attack_squad_strongest,
                  "weakest": attack_squad_weakest,
                  "random": attack_squad_random}


class Army:

    """ A class for armies.
    Armies are consisted out of a number of squads, that behave
    as a coherent group.

    Attributes
    ----------
    squad_amount : int
        amount of squads
    strategy : str
        army strategy
    squads : int
        list of squads
    amount_units : int
        amount of active units

    """

    def __init__(self, sq_amount, strategy_str, unit_amount):
        self.squad_amount = sq_amount
        self.strategy = strategy_str
        self.squads = []
        for i in range(self.squad_amount):
            squad = Squad(unit_amount, strategy_str)
            self.squads.append(squad)
        self.amount_units = sq_amount * unit_amount

    def attack(self, user_armies, curr_army):
        """ Attack function, based on strategy

        """
        enemy = ARMY_STRATEGY[user_armies[curr_army].strategy](user_armies, curr_army)
        for s in self.squads:
            SQUAD_STRATEGY[user_armies[curr_army].strategy](s, enemy)

    def strength(self):
        """ Returns total health

        """
        sum_hp = 0
        for s in self.squads:
            sum_hp += s.strength()
        return sum_hp

    def active_amount(self):
        """ Returns amount of active squads and calculate amount of active units

        """
        active_squads = 0
        self.amount_units = 0
        for s in self.squads:
            if s.is_active():
                active_squads += 1
                self.amount_units += s.active_amount()
        return active_squads

    def is_active(self):
        """ Returns true, if the army contains at least one active squad

        """
        active_squads = self.active_amount()
        return active_squads > 0


def main():
    # Initializing armies
    config_file = open("battle_config.yml")
    config = yaml.load(config_file, Loader=yaml.FullLoader)

    seed_num = config["seed"]
    armies_amount = config["armies_amount"]
    strategy = config["strategy"]
    squad_amount = config["squad_amount"]
    units_amount = config["units_amount"]

    random.seed(seed_num)
    armies = []
    for i in range(armies_amount):
        army = Army(squad_amount, strategy, units_amount)
        armies.append(army)
    active_armies = armies_amount

    # Main cycle of battle
    j = 0
    game = {}
    while active_armies >= 2:
        i = 0
        for army in armies:
            army.attack(armies, i)
            i += 1
        if j % 50 == 0:
            i = 1
            armies_dict = {}
            for army in armies:
                amount = army.active_amount()
                print("Army N" + str(i) + ": " + str(amount) + " squads left")
                l = 1
                squads_dict = {}
                for s in army.squads:
                    curr_squad = {}
                    soldiers = []
                    vehicles = []
                    print("Squad N" + str(l))
                    print("Soldiers: ", end="")
                    for u in s.units:
                        if u.name == "soldier":
                            print(str(u.hp) + " ", end="")
                            soldiers.append(u.hp)
                    print(";")
                    print("Vehicles: ", end="")
                    for u in s.units:
                        if u.name == "vehicle":
                            print(str(u.hp) + " ", end="")
                            vehicles.append(u.hp)
                    print(";")
                    curr_squad["Soldiers"] = soldiers
                    curr_squad["Vehicles"] = vehicles
                    squads_dict["Squad N" + str(l)] = curr_squad
                    l += 1
                armies_dict["Army N" + str(i)] = squads_dict
                if i < armies_amount:
                    print("---------")
                i += 1
            print("==================")
            game["Round N" + str(j)] = armies_dict
        active_armies = 0
        for army in armies:
            if army.is_active():
                active_armies += 1
        j += 1

    with open(r'log.yml', 'w') as file:
        yaml.dump(game, file)

    # Determining the winner
    winner = -1
    i = 1
    for army in armies:
        if army.is_active():
            winner = i
        i += 1
    if winner > -1:
        print("Army №" + str(winner) + " is a winner!")
    else:
        print("There is no winner")


if __name__ == "__main__":
    main()
