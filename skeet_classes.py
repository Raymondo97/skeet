"""This file contains the necessary classes for the skeet.py game to function."""

import arcade
import time
import math
import random
from abc import ABC
from abc import abstractmethod

# These are Global constants to use throughout the game
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 500

RIFLE_WIDTH = 100
RIFLE_HEIGHT = 20
RIFLE_COLOR = arcade.color.DARK_RED

BULLET_RADIUS = 3
BULLET_COLOR = arcade.color.BLACK_OLIVE
BULLET_SPEED = 10

TARGET_RADIUS = 20
TARGET_COLOR = arcade.color.CARROT_ORANGE
TARGET_STRONG_LIVES = 3
TARGET_SAFE_COLOR = arcade.color.AIR_FORCE_BLUE
TARGET_SAFE_RADIUS = 15

# Global constants for explosions
EXPLOSION_RADIUS = 30
EXPLOSION_PART1_COLOR = arcade.color.RED
EXPLOSION_PART2_COLOR = arcade.color.YELLOW
EXPLOSION_WAIT_TIME = .25

class Point():
    """A class to keep track of coordinates."""
    def __init__(self):
        """Initializes the x and y coordinates."""
        self.x = 0
        self.y = 0
        
    
class Velocity():
    """A class to keep track of the velocity for objects."""
    def __init__(self):
        """Initializes the change in x and y for velocity."""
        self.dx = 0
        self.dy = 0
        

class Flying_Objects(ABC):
    """An abstract class that contains data for flying objects."""
    def __init__(self):
        """Initalizes center, velocity, and life of object."""
        self.center = Point()
        self.velocity = Velocity()
        self.alive = True
        
    def advance(self):
        """Handles the advancing of an object."""
        self.center.x += self.velocity.dx
        self.center.y += self.velocity.dy
        
    def is_off_screen(self, screen_width, screen_height):
        """Returns true if object exits screen parameters."""
        off_screen = False
        # If statement checks if objects goes off any side of screen
        if self.center.x > screen_width or 0 > self.center.y or \
           self.center.y > screen_height:
            off_screen = True
        return off_screen
    
    @abstractmethod
    def draw(self):
        """Abstract method for child objects to be drawn."""
        pass
    
    
class Bullet(Flying_Objects):
    """A child class of Flying_Objects for a bullet."""
    def __init__(self):
        """Initalizes Flying_Objects attributes, specifying bullet constants."""
        super().__init__()
        self.radius = BULLET_RADIUS
        
    def draw(self):
        """Draws a filled circle using the current attributes."""
        arcade.draw_circle_filled(self.center.x, self.center.y, self.radius,
                                  BULLET_COLOR)
        
    def fire(self, angle):
        """Changes velocity of bullet to match direction of angle given."""
        self.velocity.dx = math.cos(math.radians(angle)) * BULLET_SPEED
        self.velocity.dy = math.sin(math.radians(angle)) * BULLET_SPEED
        
    
class Target(Flying_Objects):
    """A child class of Flying_Objects for a target."""
    def __init__(self):
        """Initializes Flying Objects attributes, specifying target constants."""
        super().__init__()
        self.radius = TARGET_RADIUS
        self.center.y = random.uniform(SCREEN_HEIGHT / 2, SCREEN_HEIGHT)
        # I felt that some of the targets were moving too fast, so I slowed it down.
        self.velocity.dx = random.uniform(1, 3)
        self.velocity.dy = random.uniform(-2, 3)
    
    def hit(self):
        """A method to kill target. Returns points scored for hit."""
        self.alive = False
        return 1
    
    # A class method for creating explosions from the Explosion class
    def explode(self):
        """Creates an explosion object to appear when target is hit."""
        explosion = Explosion(self.center.x, self.center.y)
        return explosion
            
    def draw(self):
        """Draws a filled circle using the current attributes."""
        arcade.draw_circle_filled(self.center.x, self.center.y, self.radius,
                                  TARGET_COLOR)
        
        
class Strong_Target(Target):
    """A child class for a strong target; has multiple hits."""
    def __init__(self):
        """Initializes different velocity and life count."""
        super().__init__()
        # I felt that some of the targets were moving too fast, so I slowed it down.
        self.velocity.dx = random.uniform(1, 2)
        self.velocity.dy = random.uniform(-2, 2)
        self.lives = TARGET_STRONG_LIVES
        
    def draw(self):
        """Draws an empty circle with hits left inside of circle."""
        arcade.draw_circle_outline(self.center.x, self.center.y, self.radius, TARGET_COLOR)
        text_x = self.center.x - (self.radius / 2)
        text_y = self.center.y - (self.radius / 2)
        arcade.draw_text(repr(self.lives), text_x, text_y, TARGET_COLOR, font_size=20)
    
    def hit(self):
        """Decrements life. Returns 5 if killed, otherwise returns 1."""
        self.lives -= 1
        if self.lives == 0:
            self.alive = False
            return 5
        else:
            return 1
        
    
class Safe_Target(Target):
    """A child class for a safe target; should not be hit."""
    def __init__(self):
        """Calls super of target init function, replacing the radius with Safe Target length."""
        super().__init__()
        self.radius = TARGET_SAFE_RADIUS
    
    def draw(self):
        """Draws a square thats a different color from other targets."""
        arcade.draw_rectangle_filled(self.center.x, self.center.y, self.radius, self.radius,
                                     TARGET_SAFE_COLOR)
        
    def hit(self):
        """Returns -10 as instead of 1."""
        super().hit()
        return -10
    
    
# This class is part of my "above and beyond" efforts
class Explosion:
    """A class for an explosion that appears when a target is destroyed."""
    def __init__(self, x, y):
        """Initializes explosion's center as a point class. X and Y will be
        the last known location of the target being destroyed.
        Also initializes radius, and partial radius for determining explosion size.
        Lastly, initalizes time to help determine when to remove."""
        self.center = Point()
        self.center.x = x
        self.center.y = y
        self.radius = EXPLOSION_RADIUS
        # Partial radius is responsible for creating inner point of explosion star
        self.partial_radius = self.radius / 3
        # Start time keeps track of when the explosion was created,
        # so that it can be removed after global explosion time
        self.start_time = time.time()
    
    def draw(self):
        """A draw method for drawing the explosion.
        Creates two lists for two 4-point stars, that create the explosion star.
        """
        # Following point list is reponsible for drawing points of the red part of the explosion star
        point_list1 = [(self.center.x - self.radius, self.center.y),
                      (self.center.x - self.partial_radius, self.center.y + self.partial_radius),
                      (self.center.x, self.center.y + self.radius),
                      (self.center.x + self.partial_radius, self.center.y + self.partial_radius),
                      (self.center.x + self.radius, self.center.y),
                      (self.center.x + self.partial_radius, self.center.y - self.partial_radius),
                      (self.center.x, self.center.y - self.radius),
                      (self.center.x - self.partial_radius, self.center.y - self.partial_radius)]
        # Following point list is reponsible for drawing points of the yellow part of the explosion star
        point_list2 = [(self.center.x - self.partial_radius, self.center.y),
                      (self.center.x - self.radius, self.center.y + self.radius),
                      (self.center.x, self.center.y + self.partial_radius),
                      (self.center.x + self.radius, self.center.y + self.radius),
                      (self.center.x + self.partial_radius, self.center.y),
                      (self.center.x + self.radius, self.center.y - self.radius),
                      (self.center.x, self.center.y - self.partial_radius),
                      (self.center.x - self.radius, self.center.y - self.radius)]
        arcade.draw_polygon_filled(point_list1, EXPLOSION_PART1_COLOR)
        arcade.draw_polygon_filled(point_list2, EXPLOSION_PART2_COLOR)