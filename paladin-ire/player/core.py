# -*- coding: utf-8 -*-
import random

NAME_LIST=['Flargin','Dingo','Mypaltr','Pallyride','Pallindrome','Jeff','Chaz',
           'Molly','Martin','Grena','Palson','Rempo','Trixy','Mouse','Pal']

class RandomRoll(object):

    DISADV = -1
    ZERO = 0
    ADV = 1
    CRIT = 2

    def __init__(self,player,ubound,lbound=1):
        self.player = player
        self.ub = ubound    # Random roll range upper-bound
        self.lb = lbound    # Random roll range lower-bound

    def _calc_adv(self,skill):
        # Calculates skill checks
        if skill is not None:
            chk_mod = getattr(self.player,skill)
            return (chk_mod / self.skill_max_val()) + 1.
        return 1.

    def skill_max_val(self):
        return float((self.player.level * 10) + 7)

    @property
    def possibles(self):
        return range(self.min_val,self.max_val)

    def calc_bound(self,bound,mult=1.):
        assert isinstance(mult, float)
        return int(bound * mult)

    def execute(self):
        return random.choice(self.possibles)

    def attr_roll(self,attr):
        return self._calc_adv(attr)

    def roll(self,check):
        self.max_val = self.calc_bound(self.ub, self.attr_roll(check))
        self.min_val = self.calc_bound(self.lb, self.attr_roll('luck'))
        return self.execute()

    def resist_roll(self,resist):
        adv = self._calc_adv(resist)
        max_val = self.skill_max_val()
        result = self.roll(resist)
        return abs((result/max_val) - adv)

    def atk_roll(self,goal):
        # goal = roll attr or save for target/enemy
        result = self.roll('attack')
        if (result/float(goal)) > 1.25:
            return self.CRIT
        elif result >= goal:
            return self.ADV
        elif result == 0:
            return self.ZERO
        elif result < goal:
            return self.DISADV

class Entity(object):

    """ General attributes/properties/methods for PC/NPC Entities """

    attributes = ["health","attack","defense","focus","strength","wisdom","luck"], 1
    resists = ["fire","frost","death","detection"], 0
    status_effects = ["blind","paralyzed","invincible","fast"], 0

    attr_desc = {
                 'health':'Contributes to\nplayer hit points',
                 'attack':'Affects damage\ndealt by the\nplayer',
                 'defense':'Contributes to\ndamage mitigation\nand dodging',
                 'focus':'Affects ranged\ndamage, spell\ncasting, and\nhit likelihood',
                 'strength':'Contributes to\ndamage and\ncarry capacity',
                 'wisdom':'Determines spell\ndamage and\nmana',
                 'luck':'Increases critical\nhit potential\nand save roll\nbaselines'
                }

    def __init__(self):
        self.alive = True
        self.__attr_init()
        self.level = 1

    def __attr_init(self):
        attrs = self.attributes, self.resists, self.status_effects
        for group in attrs:
            items, default = group
            for item in items:
                setattr(self, item, default)

    def pre_turn(self):
        """ Pre-Turn hook, status effects decremented """
        effects, _ = self.status_effects
        for eff in effects:
            val = getattr(self, eff)
            if val > 0:
                val -= 1
                setattr(self, eff, val)

    @property
    def alive(self):
        if self.health > 0: return True
        return False

    @alive.setter
    def alive(self,revive):
        # Allows reviving/killing a player by setting
        # the alive property to True/False
        if revive: self.health = 1
        else: self.health = 0
