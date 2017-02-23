# -*- coding: utf-8 -*-

class Entity(object):

    """ General attributes/properties/methods for PC/NPC Entities """

    attributes = ["health","attack","defense","focus","strength","wisdom"], 1
    resists = ["fire","frost","death","detection"], 0
    status_effects = ["blind","paralyzed","invincible","fast"], 0

    attr_desc = {
                 'health':'Determines starting\nhit points',
                 'attack':'Affects damage\ndealt by the\nplayer',
                 'defense':'Contributes to\ndamage mitigation\nand dodging',
                 'focus':'Affects ranged\ndamage, spell\ncasting, and\nhit likelihood',
                 'strength':'Contributes to\ndamage and\ncarry capacity',
                 'wisdom':'Determines spell\ndamage and\nmana'
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

