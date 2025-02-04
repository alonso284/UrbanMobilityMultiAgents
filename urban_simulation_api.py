# -*- coding: utf-8 -*-
"""UrbanSimulation.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1YfGqZ41HiJZx13s1l8Qke2vbWJmXQMqS
"""

# !pip install agentpy

import agentpy as ap
import numpy as np
import random, json
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import seaborn as sns, IPython
from matplotlib import pyplot as plt, cm

'''
Grid cell types

gr grass
us street heading up
ds street heading down
rs street heading east
ls street heading left
ic intersection
cw crosswalk
sw sidewalk
pw able cross walk
ho house
de destination
dw driveway
ob obstacle
'''
gr = -100;
cw, ic, us, ls, ds, rs, sw, pw, ho, de, dw, ob = -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 # Values are clockwise
traffic_light_cooldown, traffic_light, car = 99, 100, 101

class CarAgent(ap.Agent):

    """
    Function to setup the car agents
    """
    def setup(self):
      self.env = self.model.env
      self.random = self.model.random
      self.agentType = "car"

      # Store a list of remaining movements to leave an intersection (queue)
      self.intersection_moves = []

      # 0: up, 1: left, 2: down, 3: right
      # This dictionary maps which directions are available to cars traveling in a certain direction
      self.directions = {
          rs: [3, 3, 3, 3, 3, 0, 2],
          us: [0, 0, 0, 0, 0, 1, 3],
          ds: [2, 2, 2, 2, 2, 1, 3],
          ls: [1, 1, 1, 1, 1, 0, 2]
      }

      self.direction = -1

    """
    Function to choose a new direction to go after the next intersection
    """
    def choose_direction(self):
      tile = self.env.get_tile(self.get_position())
      possibleDirections = self.directions[tile]
      self.direction = self.random.choice(possibleDirections)

    """
    Function to run at each step of the simulation
    """
    def execute(self):

      # Check if the car is allowed to move to the next position

      if len(self.intersection_moves) > 0:
        pos = self.get_position()
        move = self.intersection_moves[0]
        next_position = (pos[0] + move[0], pos[1] + move[1])
        # Check there's no car or pedestrian in the next tile, else, don't move and wait for the file to be free
        if not self.model.has_car(next_position) and not self.model.crosswalk_has_pedestrians(next_position):
          self.env.move_to(self, next_position)
          self.intersection_moves.pop(0)
          # If out of the intersection, choose a new random direction
          if len(self.intersection_moves) == 0:
            self.choose_direction()
      else:
        # Advance according to road direction if there is no obstacle (car or crosswalk)
        next_position = self.get_next_position()
        if next_position is not None and not self.model.has_car(next_position):
          if self.env.get_tile(next_position) != cw and self.env.get_tile(next_position) != pw:
            self.env.move_to(self, next_position)

    """
    Function to get the next position for the car depending on the road it's on
    """
    def get_next_position(self):
      position = self.get_position()

      if len(self.intersection_moves) > 0:
        move = self.intersection_moves.pop(0)
        return (position[0] + move[0], position[1] + move[1])

      # Get direction of street and calculate new position
      tile = self.env.get_tile(position)
      if tile == rs:
        return (position[0], position[1]+1)
      elif tile == ls:
        return (position[0], position[1]-1)
      elif tile == us:
        return (position[0]-1, position[1])
      elif tile == ds:
        return (position[0]+1, position[1])
      else:
        return None

    def enter_intersection(self):
      enter_direction_tile = self.env.get_tile(self.get_position())
      enter_direction = self.direction_from_tile(enter_direction_tile)
      forward = None
      right = None
      left = None

      # 0: up, 1: left, 2: down, 3: right
      if enter_direction == 0: # up
        forward = (-1, 0)
        right = (0, 1)
        left = (0, -1)
      elif enter_direction == 1: # left
        forward = (0, -1)
        right = (-1, 0)
        left = (1, 0)
      elif enter_direction == 2: # down
        forward = (1, 0)
        left = (0, 1)
        right = (0, -1)
      else: # right
        forward = (0, 1)
        right = (1, 0)
        left = (-1, 0)

      # Determine maneuver (forward, left, right) based on current direction and intended direction
      # FIXME: Consider U turn (?)
      intersection_path = None
      if enter_direction == self.direction:
        intersection_path = "forward"
      elif (enter_direction + 1)%4 == self.direction:
        intersection_path = "left"
      elif (enter_direction - 1)%4 == self.direction:
        intersection_path = "right"
      else:
        print("Something's wrong")

      if intersection_path == "forward":
        self.intersection_moves = [forward, forward, forward, forward, forward]
      elif intersection_path == "left":
        self.intersection_moves = [forward, forward, forward, left, left, left]
      elif intersection_path == "right":
        self.intersection_moves = [forward, forward, right, right]

    def direction_from_tile(self, tile):
      if tile == rs:
        return 3
      elif tile == ls:
        return 1
      elif tile == us:
        return 0
      elif tile == ds:
        return 2


    """
    Function to get the current position in the grid of the car
    """
    def get_position(self):
      return self.env.positions[self]

class TrafficLightAgent(ap.Agent):
    """
    Setup traffic light agent variables
    """
    def setup(self):
        # Actions are linked to a movement in the grid.
        self.actions = {'up': (-1,0), 'down': (1, 0), 'left': (0, -1), 'right': (0, 1)}
        # Positions nedded to move according to starting location in intersection (top left corner)
        self.differencial = {'up': (1,1), 'down': (0, 0), 'left': (0, 1), 'right': (1, 0)}
        # Traffic light rotation order (currently clockwise)
        self.next_positions = {'up':'left', 'left':'down', 'down':'right', 'right':'up'}

        self.env = self.model.env
        self.p = self.model.p

        self.random = self.model.random
        self.agentType = "light"

        # Positions of cars and crosswalks based on starting position (top left corner)
        self.exit_directions = []
        self.cross_walks = {}
        self.top_left_pos = None

        # Traffic light variables
        self.counter = self.p.traffic_light_step_duration # Time the light has spent in green or yellow (passing or cooldown mode)
        self.intersection_position = self.random.choice(['up', 'down', 'left', 'right']) # which direction of the street the traffic light is letting go through FIXME: traffic light may not start in the upper left cell
        self.cooldown = False # Whether the traffic light is on cooldown


    """
    Function to calculate the exits and crosswalks of each side of the intersection
    """
    def find_exits(self):
        # Starting location (top left corner of intersection)
        self.top_left_pos = self.env.positions[self]
        # Move to actual starting position
        self.env.move_by(self, self.differencial[self.intersection_position])

        # Locations of cars that need to pass according to intersection position
        left_exit = (self.top_left_pos[0], self.top_left_pos[1]-2)
        right_exit = (self.top_left_pos[0]+1, self.top_left_pos[1]+3)
        down_exit = (self.top_left_pos[0]+3, self.top_left_pos[1])
        up_exit = (self.top_left_pos[0]-2, self.top_left_pos[1]+1)

        self.exit_directions = [up_exit, left_exit, down_exit, right_exit]

        # Location of crosswalks that need to pass according to intersection position
        left_cross_walk = [(self.top_left_pos[0], self.top_left_pos[1]-1), (self.top_left_pos[0]+1, self.top_left_pos[1]-1)]
        right_exit = [(self.top_left_pos[0], self.top_left_pos[1]+2), (self.top_left_pos[0]+1, self.top_left_pos[1]+2)]
        down_exit = [(self.top_left_pos[0]+2, self.top_left_pos[1]), (self.top_left_pos[0]+2, self.top_left_pos[1]+1)]
        up_exit = [(self.top_left_pos[0]-1, self.top_left_pos[1]), (self.top_left_pos[0]-1, self.top_left_pos[1]+1)]

        self.cross_walks = {'down': left_cross_walk, 'left': up_exit, 'up': right_exit, 'right': down_exit}

        # Enable the corresponding crosswalk
        self.allow_cross_walk(self.intersection_position)


    """
    Function for each step of the simulation
    """
    def execute(self):
        # Traffic light time counter (Green mode)
        if self.counter <= 0 and not self.cooldown:
          self.counter = self.p.traffic_light_step_cooldown
          self.cooldown = True

        # Traffic light time counter (Yellow mode)
        if self.counter <= 0 and self.cooldown:
          self.start_next_cycle()
          self.cooldown = False

        # If light is in green (pass mode)
        if not self.cooldown:
          # Check if a car has a green light and is ready to move
          next_car_position = self.next_car_position()
          if self.is_car_in_position(next_car_position):
            # Get agent in 'position next_car_position'
            carAgent = list(self.env.grid[next_car_position][0])[0]
            carAgent.enter_intersection()

        self.counter -= 1

        self.record('status', not self.cooldown)

    """
    Get the position of the car it should be letting through
    """
    def next_car_position(self):
        next_car_orientation = self.actions[self.intersection_position]
        dx, dy = -2 * next_car_orientation[0], -2 * next_car_orientation[1]

        x, y = self.get_position()
        return x + dx, y + dy

    """
    Get position of agent in environment
    """
    def is_car_in_position(self, pos):
        N, M = self.model.p.street.shape
        if pos in self.env.positions.values():
          return True

    """
    Get position of agent in environment
    """
    def get_position(self):
        return self.env.positions[self]

    """
    Move agent to next position and reset counter
    """
    def start_next_cycle(self):
        # Close down the intersection
        self.disallow_cross_walk(self.intersection_position)

        # Order (Clockwise)
        self.intersection_position = self.next_positions[self.intersection_position]

        # Random (Choose randomly which lane to allow next)
        # self.intersection_position = self.random.choice(['up', 'down', 'left', 'right'])

        # Calculate new position
        new_pos = (self.top_left_pos[0] + self.differencial[self.intersection_position][0],
                   self.top_left_pos[1] + self.differencial[self.intersection_position][1])

        # Move traffic light to new lane and allow new crosswalk
        self.env.move_to(self, new_pos)
        self.allow_cross_walk(self.intersection_position)

        # Restart counter
        self.counter = self.p.traffic_light_step_duration

    """
    Get opposite direction
    """
    def get_opposite_direction(self, dir):
      if dir == "down": return "up"
      elif dir == "up": return "down"
      elif dir == "left": return "right"
      elif dir == "right": return "left"

    """
    Allow both paralel crosswalks to allowed lane
    """
    def allow_cross_walk(self, dir):
      for tile in self.cross_walks[dir]:
        self.env.change_tile(tile, pw)
      for tile in self.cross_walks[self.get_opposite_direction(dir)]:
        self.env.change_tile(tile, pw)

    """
    Disallow both paralel crosswalks to allowed lane
    """
    def disallow_cross_walk(self, dir):
      for tile in self.cross_walks[dir]:
        self.env.change_tile(tile, cw)
      for tile in self.cross_walks[self.get_opposite_direction(dir)]:
        self.env.change_tile(tile, cw)

class PedestrianAgent(ap.Agent):

    def setup(self):
      self.env = self.model.env
      # Blackboard forsharing update Q function with other agents
      self.blackboard = self.model.blackboard
      self.actions = self.blackboard.actions
      self.random = self.model.random

      # Avoid putting pedestrians over each other
      self.display_offset = (self.random.uniform(-0.2, 0.2), self.random.uniform(-0.2, 0.2))

      # Choose a random building to go to (destination)
      self.destination = self.random.choice(self.model.destinations)

      self.agentType = "pedestrian"

      # Pedestrian variables
      self.inside_intersection = False
      self.reward = 0
      self.training = False

    """
    Q-Learning.
    Q update dict is shared with other agents for optimized training
    """
    def train(self, episodes):
      start = self.get_position()

      self.training = True
      for k in range(self.p.train_episodes):
          state = (start, self.destination)                                 # Initial state
          while state[0] != self.destination:                               # Iterate until agent reaches the goal
              action = self.execute()                                       # Choose & execute action
              new_state = self.get_state()
              reward = self.env.get_reward(new_state[0], self.destination)  # Get action reward
              self.blackboard.update_Q(state, action, reward, new_state)    # Update Q-values
              state = new_state
          self.env.move_to(self, start)
          self.reward = 0
      self.training = False

    """
    Choose action based on learning
    """
    def execute(self):
      # If in destination, dont move
      if self.get_position() == self.destination:
        return


      action = self.choose_action(self.get_state())
      action_move = self.actions[action]

      pos = self.get_position()
      new_position = (pos[0] + action_move[0], pos[1] + action_move[1])

      # Move to new position if possible and collect reward
      if self.training or self.can_move_into(new_position):
        self.env.move_to(self, new_position)
        self.reward += self.env.get_reward(self.get_position(), self.destination)

      # Checl if agent is on a crosswalk
      if self.env.get_tile(new_position) == pw:
        self.inside_intersection = True
      elif self.env.get_tile(new_position) == sw:
        self.inside_intersection = False

      return action

    """
    Choose action that is optimum or random based on models epsilon
    """
    def choose_action(self, state):
      if random.uniform(0, 1) < self.blackboard.epsilon:
        return random.choice(list(self.actions.keys()))
      else:
        return max(self.blackboard.Q[state], key=self.blackboard.Q[state].get)

    """
    Get agents position
    """
    def get_position(self):
      return self.env.positions[self]

    """
    Check if agent can move into new position without getting run over
    """
    def can_move_into(self, pos):
      return self.env.get_tile(pos) != cw or self.inside_intersection and not self.model.has_car(pos)

    """
    Get next position and if allowed, if not, stay in place
    """
    def get_next_position(self):
      pos = self.get_position()
      if pos == self.destination:
        return pos
      action = self.choose_action(self.get_state())
      action_move = self.actions[action]
      new_position = (pos[0] + action_move[0], pos[1] + action_move[1])

      if self.can_move_into(new_position):
        return new_position
      else:
        return pos

    """
    State of agent is based of position and its destination
    """
    def get_state(self):
      return (self.get_position(), self.destination)

rewardMap = {
  us: -100,
  ds: -100,
  ls: -100,
  rs: -100,
  ob: -100,
  ic: -100,
  ho: -100,
  de: -100,
  gr: -40,
  sw: -1,
  dw: -1,
  cw: -1,
  pw: -1
}

class StreetGrid(ap.Grid):
    """
    Setup the street tiles
    """
    def setup(self):
      # Initialize the environment
      self.environment = np.copy(self.p.street)

    """
    Get value of tile
    (agents have different destinations, return reward only if arrived to its desination)
    """
    def get_reward(self, pos, destination):
      if pos == destination:
        return 1000

      return rewardMap[self.get_tile(pos)]

    """
    Get the value of a specified position
    """
    def get_tile(self, pos):
      if 0 <= pos[0] < self.shape[0] and 0 <= pos[1] < self.shape[1]:
        return self.environment[pos]
      else:
        return None

    """
    Change the value of a tile on the grid
    """
    def change_tile(self, pos, val):
      if 0 <= pos[0] < self.shape[0] and 0 <= pos[1] < self.shape[1]:
        self.environment[pos] = val

class Blackboard():

  """
  Black board is used to optimize learning between agents
  All agents with the same destination share the same Q Table
  (This is done by making the state depend on the position, destination and action)
  """
  def __init__(self, model):
    self.actions = {"up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1)}

    self.alpha = model.p.alpha
    self.gamma = model.p.gamma
    self.epsilon = model.p.epsilon

    self.Q = {}
    for i in range(model.env.shape[0]):
      for j in range(model.env.shape[1]):
        for destination in model.destinations:
          self.Q[((i, j), destination)] = {action: 0 for action in self.actions}

  """
  Update queue value
  """
  def update_Q(self, state, action, reward, new_state):
        max_Q_new_state = max(self.Q[new_state].values())
        self.Q[state][action] = self.Q[state][action] + self.alpha * (reward + self.gamma * max_Q_new_state - self.Q[state][action])

class StreetModel(ap.Model):
    def setup(self):
        self.random.seed = self.p.seed
        self.env = StreetGrid(self, shape=self.p.street.shape, torus=True)
        self.destinations = self.find_tiles(de)
        # Blackboard for training
        self.blackboard = Blackboard(self)

        roads = self.find_tiles(us) + self.find_tiles(ds) + self.find_tiles(ls) + self.find_tiles(rs)
        car_positions = []
        # Spawn card on the road (according to density)
        for road in roads:
          if self.random.uniform(0, 1) < self.p.car_density:
            car_positions.append(road)

        # Spawn traffic light and cars
        self.traffic_light_agents = ap.AgentList(self, len(self.p.traffic_light_agents), TrafficLightAgent)
        self.car_agents = ap.AgentList(self, len(car_positions), CarAgent)

        # Spawn a pedestrian in each house
        houses = self.find_tiles(ho)
        self.pedestrian_agents = ap.AgentList(self, len(houses), PedestrianAgent)

        # Add all three types of agents
        self.env.add_agents(self.traffic_light_agents, positions=self.p.traffic_light_agents)
        self.env.add_agents(self.car_agents, positions=car_positions)
        self.env.add_agents(self.pedestrian_agents, positions=houses)

        # Train the model (without cars of traffic lights spawned to make the training space static)
        print("Training...")
        self.pedestrian_agents.train(self.p.train_episodes)
        self.blackboard.epsilon = 0
        print("Finished training...")

        self.car_agents.choose_direction()
        self.traffic_light_agents.find_exits()

        # Moving agents positions
        self.car_positions = []
        self.pedestrian_positions = []

    """
    Check if there is a car in position
    """
    def has_car(self, pos):
      pos = (pos[0] % self.env.shape[0], pos[1] % self.env.shape[1])

      blocked = False
      agents = list(self.env.grid[pos][0])
      for agent in agents:
        if agent.agentType == "car":
          blocked = True
          break

      return pos in self.car_positions or blocked

    """
    Check if tile is crosswalk (abled or enabled)
    """
    def is_crosswalk(self, pos):
      return self.env.get_tile(pos) == pw or self.env.get_tile(pos) == cw

    """
    Check that there isn't any pedestrian moving into the crosswalk
    """
    def crosswalk_has_pedestrians(self, pos):
      crosswalk = []
      # As crosswalk occupate two tiles, check if agent is on a cross walk and which way is the other crosswalk tile
      if self.is_crosswalk(pos):
        crosswalk.append(pos)
        if self.is_crosswalk((pos[0]+1, pos[1])):
          crosswalk.append((pos[0]+1, pos[1]))
        elif self.is_crosswalk((pos[0]-1, pos[1])):
          crosswalk.append((pos[0]-1, pos[1]))
        elif self.is_crosswalk((pos[0], pos[1]+1)):
          crosswalk.append((pos[0], pos[1]+1))
        elif self.is_crosswalk((pos[0], pos[1]-1)):
          crosswalk.append((pos[0], pos[1]-1))

      # Check both crosswalk tiles (if any) for pedestrians
      blocked = False
      for crosswalk_tile in crosswalk:
        agents = list(self.env.grid[crosswalk_tile][0])
        for agent in agents:
          if agent.agentType == "pedestrian":
            blocked = True
          break
        if blocked: break
      return blocked

    """
    Get all positions of a specific type of tile
    """
    def find_tiles(self, tile):
      tiles = []
      for i in range(self.env.shape[0]):
        for j in range(self.env.shape[1]):
          if self.env.get_tile((i, j)) == tile:
            tiles.append((i, j))
      return tiles

    """
    Simulation step
    """
    def step(self):
      # Store the current car positions so that execution order doesnt affect the car movements
      self.car_positions = []
      for car in self.car_agents:
        self.car_positions.append(car.get_position())

      # Store the current pedestrian positions as well as their next position as they have preference in movement
      self.pedestrian_positions = []
      for pedestrian in self.pedestrian_agents:
        self.pedestrian_positions.append(pedestrian.get_position())
        self.pedestrian_positions.append(pedestrian.get_next_position())

      # Execute agent actions
      self.traffic_light_agents.execute()
      self.car_agents.execute()
      self.pedestrian_agents.execute()

      self.env.record_positions()

    """
    Update agent values
    """
    def update(self):
      # Check if all pedestrians have reached their destination
      pedestrian_remaining = False
      for pedestrian in self.pedestrian_agents:
        if pedestrian.get_position() != pedestrian.destination:
          pedestrian_remaining = True
          break

      # Stop if all pedestrians arrived to their destinations
      if not pedestrian_remaining:
        self.stop()
        print("All pedestrians made it to their destination")

    # Report found route and Q-values
    def end(self):
        self.report('Q table', self.blackboard.Q)

# Environment representation with a grid
street =  np.array([
    # Big city
    [gr, gr, gr, gr, sw, ds, us, sw, gr, gr, gr, gr, sw, ds, us, sw, gr, gr, ho, dw, sw, ds, us, sw, gr, gr, de, dw, sw, ds, us, sw, gr, gr, gr, gr],
    [gr, gr, gr, gr, ob, ds, us, sw, gr, gr, de, dw, sw, ds, us, sw, dw, ho, gr, gr, sw, ds, us, sw, gr, gr, ho, gr, sw, ds, us, sw, dw, ho, gr, gr],
    [ho, gr, ho, gr, sw, ds, us, sw, dw, de, gr, gr, sw, ds, us, sw, gr, gr, ho, gr, ob, ds, us, sw, dw, ho, dw, gr, sw, ds, us, sw, gr, gr, ho, gr],
    [dw, gr, dw, gr, sw, ds, us, sw, gr, gr, gr, gr, sw, ds, us, sw, gr, gr, dw, gr, sw, ds, us, sw, gr, gr, dw, gr, sw, ds, us, sw, gr, gr, dw, gr],
    [sw, sw, sw, sw, sw, cw, cw, sw, ob, sw, sw, sw, sw, cw, cw, sw, sw, sw, sw, sw, sw, cw, cw, sw, ob, sw, ob, sw, sw, cw, cw, sw, ob, sw, sw, sw],
    [ls, ls, ls, ls, cw, ic, ic, cw, ls, ls, ls, ls, cw, ic, ic, cw, ls, ls, ls, ls, cw, ic, ic, cw, ls, ls, ls, ls, cw, ic, ic, cw, ls, ls, ls, ls],
    [rs, rs, rs, rs, cw, ic, ic, cw, rs, rs, rs, rs, cw, ic, ic, cw, rs, rs, rs, rs, cw, ic, ic, cw, rs, rs, rs, rs, cw, ic, ic, cw, rs, rs, rs, rs],
    [sw, sw, sw, sw, sw, cw, cw, sw, sw, sw, sw, sw, sw, cw, cw, sw, sw, sw, sw, sw, sw, cw, cw, sw, sw, sw, sw, sw, sw, cw, cw, sw, sw, sw, sw, sw],
    [gr, dw, gr, gr, sw, ds, us, sw, gr, gr, gr, gr, sw, ds, us, sw, gr, gr, ho, dw, sw, ds, us, sw, gr, gr, gr, gr, sw, ds, us, sw, gr, dw, gr, gr],
    [gr, ho, gr, gr, sw, ds, us, sw, gr, gr, ho, dw, sw, ds, us, ob, dw, de, gr, gr, sw, ds, us, sw, dw, ho, ho, dw, ob, ds, us, sw, gr, de, gr, gr],
    [gr, gr, de, dw, sw, ds, us, sw, dw, ho, gr, gr, ob, ds, us, sw, gr, gr, gr, gr, sw, ds, us, sw, gr, gr, gr, gr, sw, ds, us, sw, ob, gr, gr, gr],
    [gr, gr, gr, gr, sw, ds, us, sw, gr, gr, ho, dw, sw, ds, us, sw, gr, gr, gr, gr, ob, ds, us, sw, dw, ho, ho, dw, sw, ds, us, sw, dw, ho, gr, gr]
    # Small city
    # [gr, gr, gr, gr, sw, ds, us, sw, gr, gr, gr, gr],
    # [gr, gr, gr, gr, sw, ds, us, sw, gr, gr, gr, gr],
    # [gr, gr, gr, gr, sw, ds, us, sw, gr, gr, gr, gr],
    # [gr, gr, gr, gr, sw, ds, us, sw, gr, gr, gr, gr],
    # [sw, sw, sw, sw, sw, cw, cw, sw, sw, sw, sw, sw],
    # [ls, ls, ls, ls, cw, ic, ic, cw, ls, ls, ls, ls],
    # [rs, rs, rs, rs, cw, ic, ic, cw, rs, rs, rs, rs],
    # [sw, sw, sw, sw, sw, cw, cw, sw, sw, sw, sw, sw],
    # [gr, gr, gr, gr, sw, ds, us, sw, gr, gr, gr, gr],
    # [gr, gr, gr, gr, sw, ds, us, sw, gr, gr, gr, gr],
    # [gr, gr, gr, gr, sw, ds, us, sw, gr, gr, gr, gr],
    # [gr, gr, gr, gr, sw, ds, us, sw, gr, gr, gr, gr]
])

parameters = {
    'street': street,
    # Big city
    'traffic_light_agents': [(5, 5), (5, 13), (5, 21), (5, 29)],  # It is assumed the agent spawns in an 'ic' (intersection) location
    # Small city
    # 'traffic_light_agents': [(5, 5)],
    'traffic_light_step_duration': 12,  # FIXME Change to 'per agent' variable
    'traffic_light_step_cooldown': 4,  # FIXME Change to 'per agent' variable
    'car_density': 0.3,
    'steps': 128,
    'seed': 2,
    'alpha': 0.9,
    'gamma': 0.9,
    'epsilon': 0.3,
    'train_episodes': 200
}

model = StreetModel(parameters)

def animation_plot(model, ax):
    N, M = model.p.street.shape
    grid = np.copy(model.p.street)

    # Iterate over all traffic light agents
    for traffic_light_agent in model.traffic_light_agents:
        traffic_light_state = model.env.positions[traffic_light_agent]
        # Make it a street tile
        grid[traffic_light_state] = us

        # Paint paralel crosswalks to traffic light
        for tile in traffic_light_agent.cross_walks[traffic_light_agent.intersection_position]:
          grid[tile] = pw
        for tile in traffic_light_agent.cross_walks[traffic_light_agent.get_opposite_direction(traffic_light_agent.intersection_position)]:
          grid[tile] = pw

    # FIXME Calculate inside previous loop based on traffic light initial position and differentials
    red_lights = []
    for i in range(N):
      for j in range(M):
        if grid[(i, j)] == ic:
          red_lights.append((i, j))
          grid[(i, j)] = us

    for car_agent in model.car_agents:
      car_state = model.env.positions[car_agent]
      grid[car_state] = car

    directionArrows = ["⬆︎", "⬅︎", "⬇︎", "➡︎"]
    color_dict = {gr:'#2c7d29', cw: '#cccccc', ho: "#b34b29", ob: "#806332", de: "#435ee6", dw: "#81848a", ic: '#ff0000', us: '#777777', ls: '#777777', ds:'#777777', rs:'#777777', car: "#1e152a", traffic_light:'#00ff00', traffic_light_cooldown: '#ffff00', sw: '#a1a7b5', pw: '#999999'}
    directionDict = {us: 0, ls: 1, ds: 2, rs: 3}

    ap.gridplot(grid, ax=ax, color_dict=color_dict, convert=True)

    # Paint arrows
    for i in range(N):
      for j in range(M):
        tile = model.env.get_tile((i, j))
        if tile in directionDict and (i,j) not in model.env.positions.values():
          ax.text(j, i, directionArrows[directionDict[tile]], color = "#b0b0b0")

    # Draw traffic lights as dots (Green or yellow)
    for traffic_light_agent in model.traffic_light_agents:
      state = model.env.positions[traffic_light_agent]
      if traffic_light_agent.cooldown:
        ax.text(state[1]-0.25, state[0]+0.25, "•", color="#ffff00", size=20)
      else:
        ax.text(state[1]-0.25, state[0]+0.25, "•", color="#00ff00", size=20)

    # Draw traffic lights as dots (Red)
    for red_light in red_lights:
      ax.text(red_light[1]-0.25, red_light[0]+0.25, "•", color="#ff0000", size=20)

    # Draw pedestrians with their offsets
    for pedestrian in model.pedestrian_agents:
      pos = pedestrian.get_position()
      ax.text(pos[1]-0.2+pedestrian.display_offset[1], pos[0]+0.2+pedestrian.display_offset[0], "•", color="white", size=15)

fig = plt.figure(figsize=(14,7))
ax = fig.add_subplot(111)
animation = ap.animate(model, fig, ax, animation_plot)
IPython.display.HTML(animation.to_jshtml())

stats = model.run()

print(stats.arrange_variables())

"""# API

## /start_simulation [POST]

## /simulation_stats [GET]

Method to get simulation meta stadisditcs

```js
{
    'traffic_light_step_duration': int,
    'traffic_light_step_cooldown': int,
    'car_density': double,
    'steps': int,
    'alpha': double,
    'gamma': double,
    'epsilon': double,
    'train_episodes': 200,
    'car_id_list': [int],
    'pedestrian_id_list': [int],
    'traffic_light_id_list': [int],
}
```

## /mobile_agent_state/{step_number} [GET]

Method to get the location of mobile agents in a specific step

```js
{
  int (agent id): {
    'x': int,
    'y': int
  },
  ...
}
```

## /static_agent_state/{step_number} [GET]

```js
{
  int (agent id): {
    'x': int,
    'y': int,
    'status': bool (True = Green, False = Yellow)
  },
  ...
}
```


"""

from flask import Flask, request, jsonify
import pandas as pd

df = stats.arrange_variables()
app = Flask(__name__)

@app.route('/start_simulation', methods=['POST'])
def start_simulation():
    # FIXME
    return jsonify({'message': 'Simulation started'}), 200

@app.route('/simulation_stats', methods=['GET'])
def get_simulation_stats():
    agent_ids = df.groupby('obj_type')['obj_id'].unique().apply(list).to_dict()
    return jsonify({**parameters, **agent_ids})

@app.route('/mobile_agent_state/<int:step_number>', methods=['GET'])
def get_mobile_agent_state(step_number):
    filtered_df = df[(df['t'] == step_number) & df['obj_type'].isin(['PedestrianAgent', 'CarAgent'])]
    result = [{'id': row['obj_id'], 'x': row['p0'], 'y': row['p1'], 'type':row['obj_type']} for _, row in filtered_df.iterrows()]
    print(result)
    return jsonify(result) if result else jsonify({'error': 'No data for the given step'})


@app.route('/static_agent_state/<int:step_number>', methods=['GET'])
def get_static_agent_state(step_number):
    filtered_df = df[(df['t'] == step_number) & (df['obj_type'] == 'TrafficLightAgent')]
    result = [{'id': row['obj_id'], 'x': row['p0'], 'y': row['p1'], 'status': row['status']} for _, row in filtered_df.iterrows()]
    return jsonify(result) if result else jsonify({'error': 'No data for the given step'})

if __name__ == '__main__':
    app.run(debug=True)

