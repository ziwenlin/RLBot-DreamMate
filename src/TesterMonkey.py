import math

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

from tools.helper import find_shot, PIDController, clip_to_field, get_target_goal, get_required_speed, predict_ball_fall
from util.boost_pad_tracker import BoostPadTracker
from util.drive import limit_to_safe_range
from util.orientation import Orientation, relative_location
from util.sequence import Sequence, ControlStep
from util.vec import Vec3


class TestMonkey(BaseAgent):

    def __init__(self, name, team, index):
        super().__init__(name, team, index)

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:

        # Gather some information about our car
        my_car = packet.game_cars[self.index]
        car_location = Vec3(my_car.physics.location)
        car_orientation = Orientation(my_car.physics.rotation)
        car_velocity = Vec3(my_car.physics.velocity)
        car_ground_speed = car_velocity.flat().length()

        # Gather some information about the ball
        ball_location = Vec3(packet.game_ball.physics.location)
        ball_relative = relative_location(car_location, car_orientation, ball_location)
        ball_angle = math.atan2(ball_relative.y, ball_relative.x)
        ball_angle *= 180 / math.pi

        # Draw some things to help understand what the bot is thinking
        # self.renderer.draw_line_3d(car_location, target_location, self.renderer.gray())
        # self.renderer.draw_rect_3d(target_location, 8, 8, True, self.renderer.orange(), centered=True)
        # self.renderer.draw_string_2d(10, 10, 2, 2, f'Target: {target_approach_speed:3.1f}', self.renderer.white())
        # self.renderer.draw_string_2d(10, 30, 2, 2, f'Ball: {target_approach_distance:3.1f}', self.renderer.white())
        # self.renderer.draw_string_2d(10, 50, 2, 2, f'Speed: {car_speed:3.1f}', self.renderer.white())

        # Controlling the car
        controls = SimpleControllerState()

        return controls
