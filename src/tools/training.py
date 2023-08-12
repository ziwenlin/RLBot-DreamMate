from rlbot.utils.game_state_util import CarState, GameState
from rlbot.utils.structures.game_data_struct import GameTickPacket

from tools.performance import TickMonitor
from training.exercises import aerial_mid_field, aerial_side_field, aerial_straight_up, aerial_mid_field_frozen_ball


class TrainingController:
    def __init__(self, car_index):
        self.car_index = car_index
        self.variation = 0
        self.packet = GameTickPacket

        self.tick_speed = TickMonitor()
        self.tick_count = 0
        self.tick_delay = 0
        self.running = False

        self.last_hit = 0
        self.last_hit_tick = 0

        self.boost_buffer = 50

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

        my_car = packet.game_cars[self.car_index]
        if my_car.boost == 0 and self.boost_buffer == 0:
            self.running = False
        if packet.game_ball.physics.location.z < 100:
            self.running = False

        last_hit = packet.game_ball.latest_touch.time_seconds
        if last_hit != self.last_hit:
            self.last_hit_tick = self.tick_count + 1 * tps_ratio
            self.last_hit = last_hit
        if self.tick_count > self.last_hit_tick > 0:
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

    def reset(self, training='', variation=-1):
        self.last_hit_tick = 0
        self.boost_buffer = 50
        self.tick_count = 0
        self.tick_delay = 0
        self.running = True

        if variation < 0:
            self.variation += 1
            if self.variation > 5:
                self.variation = 0
            variation = self.variation

        if training == 'mid field frozen ball':
            return aerial_mid_field_frozen_ball(self.car_index, variation)
        elif training == 'mid field':
            return aerial_mid_field(self.car_index, variation)
        elif training == 'side field':
            return aerial_side_field(self.car_index, variation)
        elif training == 'straight up':
            return aerial_straight_up(self.car_index)
        return aerial_mid_field(self.car_index, variation)

    def is_done(self):
        self.tick_delay += 1
        return self.tick_delay > 10

    def is_finished(self):
        return self.running is False


def need_boost(index, amount=100):
    return GameState(
        cars={index: CarState(
            boost_amount=amount
        )}
    )
