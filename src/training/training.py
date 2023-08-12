"""
How to setup class TrainingController?

Initialize TrainingController:
# self.training = TrainingController(self)

Inside the runner function:
# self.training.step(packet)
# self.training.step_boost_refill()
# if self.training.is_finished():
#     # Code resetting other controllers
#     return SimpleControllerState()
"""
from rlbot.agents.base_agent import BaseAgent
from rlbot.utils.game_state_util import GameState, CarState
from rlbot.utils.structures.game_data_struct import GameTickPacket

from training.exercises import aerial_mid_field

RESET_TICK_DELAY = 10
START_TICK_DELAY = 10


class TrainingBase:
    def __init__(self, agent: BaseAgent):
        self.agent = agent
        self.packet: GameTickPacket = None
        self.running = False

        self.variation = 0
        self.boost_buffer = 50

        # Not sure, to be done
        self.reset_time = 1200
        self.reset_delay = 300

        # Will be not used like this
        self.last_hit_tick = 0
        self.tick_count = 0

    def step(self, packet: GameTickPacket):
        self.packet = packet
        pass

    def reset(self, variation=-1):
        self.last_hit_tick = 0
        self.boost_buffer = 50
        self.tick_count = 0
        self.running = True

        if variation < 0:
            self.variation += 1
            if self.variation > 5:
                self.variation = 0
            variation = self.variation

        state = aerial_mid_field(self.agent.index, variation)
        self.agent.set_game_state(state)

    def check_boost(self):
        boost_buffer_not_empty = self.boost_buffer > 0
        if boost_buffer_not_empty is False:
            return False
        agent_car = self.packet.game_cars[self.agent.index]
        agent_need_boost = agent_car.boost < 80
        if agent_need_boost is True:
            return True
        return False

    def add_boost(self):
        agent_car = self.packet.game_cars[self.agent.index]
        boost_given = self.refill_boost(20)
        boost_amount = boost_given + agent_car.boost
        self.agent.set_game_state(GameState(
            cars={self.agent.index: CarState(
                boost_amount=boost_amount
            )}
        ))

    def refill_boost(self, amount=20):
        if self.boost_buffer > amount:
            boost_given = amount
        else:
            boost_given = self.boost_buffer
        self.boost_buffer -= boost_given
        return boost_given


class TrainingController:
    def __init__(self, agent: BaseAgent):
        self.tick_count = 0
        self.tick_speed = 1

        self.start_tick_count = 0
        self.reset_tick_count = 0

        self.running = False
        self.exercise = TrainingBase(agent)

    def step(self, packet: GameTickPacket):
        if self.is_ready() is False:
            self.start()
            return
        self.exercise.step(packet)
        if self.is_finished() is True:
            self.reset()
            return
        self.tick_count += 1

    def start(self):
        self.start_tick_count += 1
        if self.start_tick_count < START_TICK_DELAY:
            return
        self.start_tick_count = 0
        self.tick_count = 0
        self.running = True

    def reset(self):
        self.reset_tick_count += 1
        if self.reset_tick_count < RESET_TICK_DELAY:
            return
        self.reset_tick_count = 0
        self.running = False
        self.exercise.reset()
        self.tick_speed = self.exercise.packet.game_info.game_speed

    def is_finished(self):
        # Tells the agent that the exercise is completed
        return self.exercise.running is False

    def is_ready(self):
        # Tells the agent when the exercise is starting
        return self.running is True

    def is_paused(self):
        # Tells the agent when the training is paused
        return self.is_finished() or not self.is_ready()

    def step_boost_refill(self):
        if self.exercise.check_boost() is True:
            self.exercise.add_boost()
