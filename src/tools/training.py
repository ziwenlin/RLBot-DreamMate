import math
import random

from rlbot.utils.game_state_util import CarState, Physics, Vector3, Rotator, BallState, GameState, GameInfoState
from rlbot.utils.structures.game_data_struct import GameTickPacket

from tools.performance import TickMonitor


class TrainingController:
    def __init__(self, car_index):
        self.car_index = car_index
        self.variation = 0

        self.tick_count = 0
        self.tick_delay = 0
        self.running = True

        self.boost_buffer = 50
        self.packet = GameTickPacket
        self.last_hit = 0
        self.last_hit_tick = 0
        self.tick_speed = TickMonitor()

    def step(self, packet: GameTickPacket):
        self.packet = packet
        self.tick_count += 1
        tps = self.tick_speed.step()
        game_speed = packet.game_info.game_speed
        if game_speed == 0:
            game_speed = 1
        tps_ratio = tps / game_speed
        if self.tick_count > 10 * tps_ratio:
            self.running = False
        if packet.game_ball.physics.location.z < 100:
            self.running = False
        my_car = packet.game_cars[self.car_index]
        if my_car.boost == 0 and self.boost_buffer == 0:
            self.running = False
        last_hit = packet.game_ball.latest_touch.time_seconds
        if last_hit != self.last_hit:
            self.last_hit_tick = self.tick_count + 1 * tps_ratio
            self.last_hit = last_hit
        if self.tick_count > self.last_hit_tick and self.last_hit_tick > 0:
            self.running = False

    def need_boost(self):
        my_car = self.packet.game_cars[self.car_index]
        if my_car.boost < 10 and self.boost_buffer > 0:
            return True
        return False

    def add_boost(self):
        my_car = self.packet.game_cars[self.car_index]
        boost_given = 50 if self.boost_buffer > 50 else self.boost_buffer
        self.boost_buffer -= boost_given
        new_boost_amount = boost_given + my_car.boost
        return need_boost(self.car_index, new_boost_amount)

    def reset(self, variation=5):
        self.boost_buffer = 50
        self.last_hit_tick = 0
        self.tick_count = 0
        self.tick_delay = 0
        self.running = True
        self.variation += 1
        if self.variation > variation:
            self.variation = 0
        # return aerial_mid_field_frozen_ball(self.car_index)
        return aerial_mid_field(self.car_index, self.variation)
        # return aerial_straight_up(self.car_index)

    def is_done(self):
        self.tick_delay += 1
        return self.tick_delay > 10

    def is_finished(self):
        return self.running is False


def aerial_mid_field(index, variation=0):
    y = (1 + variation) * -1000
    x = random.randint(-3, 3) * 100
    car_state = CarState(
        boost_amount=100, physics=Physics(
            location=Vector3(x, y, 20),
            rotation=Rotator(0, math.pi / 2, 0),
            velocity=Vector3(0, 0, 0),
            angular_velocity=Vector3(0, 0, 0)
        )
    )
    ball_state = BallState(
        Physics(
            location=Vector3(0, 0, 200),
            velocity=Vector3(0, 600, 1500),
            angular_velocity=Vector3(0, 0, 0)
        )
    )
    game_info = GameInfoState(
        # game_speed=0.8
    )
    return GameState(
        ball=ball_state,
        cars={index: car_state},
        game_info=game_info
    )

def aerial_straight_up(index):
    y = random.randint(3, 16) * -100
    x = random.randint(-3, 3) * 50
    car_state = CarState(
        boost_amount=100, physics=Physics(
            location=Vector3(x, y, 20),
            rotation=Rotator(0, math.pi / 2, 0),
            velocity=Vector3(0, 0, 0),
            angular_velocity=Vector3(0, 0, 0)
        )
    )
    ball_state = BallState(
        Physics(
            location=Vector3(0, 0, 1500),
            velocity=Vector3(0, 0, 0),
            angular_velocity=Vector3(0, 0, 0)
        )
    )
    game_info = GameInfoState(
        # game_speed=0.8
    )
    return GameState(
        ball=ball_state,
        cars={index: car_state},
        game_info=game_info
    )


def aerial_mid_field_frozen_ball(index):
    y = random.randint(1, 4) * -1000
    x = random.randint(-3, 3) * 1000
    car_state = CarState(
        boost_amount=100, physics=Physics(
            location=Vector3(x, y, 20),
            rotation=Rotator(0, math.pi / 2, 0),
            velocity=Vector3(0, 0, 0),
            angular_velocity=Vector3(0, 0, 0)
        )
    )
    ball_state = BallState(
        Physics(
            location=Vector3(0, 0, 1500),
            velocity=Vector3(0, 0, 0),
            angular_velocity=Vector3(0, 0, 0)
        )
    )
    game_info = GameInfoState(
        # game_speed=0.8
    )
    return GameState(
        ball=ball_state,
        cars={index: car_state},
        game_info=game_info
    )


def need_boost(index, amount=100):
    return GameState(
        cars={index: CarState(
            boost_amount=amount
        )}
    )
