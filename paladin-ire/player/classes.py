# -*- coding: utf-8 -*-

import attributes
from attributes import ATTRIBUTES, ATTRIBUTE_DESCRIPTIONS

class PlayerClass(object):

    def __init__(self):
        self.class_skills = []
        self.base_attr = []

        # Use these flags to determine whether a player
        # will start with access to spells (mage types)
        # and sneak (rogue types)
        self.spell_book_enable = False
        self.sneak_enable = False
        self.resists = {}

class Warrior(PlayerClass):

    """ Warriors can use\nthe Bash, Block,\nand Kick skills """

    description = """
  Warriors are the typical melee class, equipped
  with Bash, Block, and Kick from the start.

  The Bash ability is especially useful and will
  temporarily stun enemies.  Blocking will prevent
  some damage to the Warrior.

  Kicking provides extra damage when primary
  attacks are recharging.

  Warriors may also throw weapons in their inventory
  towards enemies.  This will sometimes cause the
  item to break.
  """

    preferred_attr = [ 'strength', 'attack' ]

    def __init__(self):
        super(Warrior,self).__init__()
        self.class_skills = [ 'bash', 'block', 'kick' ]
        self.resists['death'] = 10

class Mage(PlayerClass):

    """ Mages skills include\nAlteration, Destruction,\nand Conjuration """

    description = """
  Mages come equipped with the ability to use magic
  from the start of the game.  Mages are range combat
  specialists and do best dealing damage from a
  distance.

  Alteration spells can be used to pick locks, find
  secrets, and make the player invisible.

  Destruction spells deal damage from afar, while
  Conjuration spells provide the Mage with a
  damage shield or other helpful items.
  """

    preferred_attr = [ 'focus','wisdom' ]

    def __init__(self):
        super(Mage,self).__init__()
        self.class_skills = [ 'alteration', 'destruction', 'conjuration' ]
        self.spell_book_enable = True
        self.resists['fire'] = 5
        self.resists['frost'] = 5

class Rogue(PlayerClass):

    """ Rogues have the\nBackstab, Sneak,\nand Dodge skills """

    description = """
  Rogues do best approaching their enemies from
  behind using their Backstab skill.  This will
  deal extra damage if the player is undetected.

  Rogues can sneak from the start of the game,
  and may also use the Dodge skill.

  Rogues will sometimes find poisons which can be
  applied to weapons to cause extra damage or
  inflict status effects on enemies.
  """

    preferred_attr = [ 'defense','focus' ]

    def __init__(self):
        super(Rogue,self).__init__()
        self.class_skills = [ 'backstab', 'sneak', 'dodge' ]
        self.sneak_enable = True
        self.resists['detection'] = 10

CLASSES = [ Warrior, Mage, Rogue ]
