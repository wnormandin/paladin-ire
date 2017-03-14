# -*- coding: utf-8 -*-

ATTRIBUTE_DESCRIPTIONS = {
    'health': "Determines a player's hit points, along with level",
    'attack': "Contributes to physical attack damage",
    'defense': "Resistance to physical damage",
    'focus': "Resistance to magical damage",
    'strength': "Contributes to physical attack damage and carry capacity",
    'wisdom': "Determines spell strength",
    'luck': 'Affects critical rate and damage'
    }


class Attribute(object):

    def __init__(self):
        pass


class Health(Attribute):
    name = 'health'


class Attack(Attribute):
    name = 'attack'


class Defense(Attribute):
    name = 'defense'


class Focus(Attribute):
    name = 'focus'


class Strength(Attribute):
    name = 'strength'


class Wisdom(Attribute):
    name = 'wisdom'

ATTRIBUTES = [Health, Attack, Defense, Focus, Strength, Wisdom]
