import math

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

from tools.helper import PIDController, limit_controls, JumpController, find_aerial_direction, calculate_angle_error
from tools.training import need_boost, aerial_mid_field_frozen_ball
from util.orientation import Orientation, relative_location
from util.vec import Vec3


class TestMonkey(BaseAgent):

    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.jump = JumpController()

        self.pid_steer = PIDController(0.1, 0.0, 0.2)
        self.pid_pitch = PIDController(0.05, 0.000001, 1.2)
        self.pid_roll = PIDController(0.005, 0.000001, 1.2)
        self.pid_yaw = PIDController(0.02, 0.000001, 1.2)

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:

        # Gather some information about our car
        my_car = packet.game_cars[self.index]
        car_location = Vec3(my_car.physics.location)
        car_orientation = Orientation(my_car.physics.rotation)
        car_velocity = Vec3(my_car.physics.velocity)
        car_ground_speed = car_velocity.flat().length()

        # Gather some information about the ball
        ball_location = Vec3(packet.game_ball.physics.location)
        ball_velocity = Vec3(packet.game_ball.physics.velocity)
        ball_relative = relative_location(car_location, car_orientation, ball_location)
        ball_angle = math.atan2(ball_relative.y, ball_relative.x)
        ball_angle *= 180 / math.pi

        if ball_location.z < 100:
            game_state = aerial_mid_field_frozen_ball(self.index)
            self.set_game_state(game_state)
            return SimpleControllerState()
        elif my_car.boost < 5:
            game_state = need_boost(self.index)
            self.set_game_state(game_state)

        target_direction = find_aerial_direction(ball_location, car_location, car_velocity)
        target_relative_direction = relative_location(Vec3(), car_orientation, target_direction)
        target_z_angle = math.asin(target_direction.z / target_direction.length()) * 180 / math.pi
        target_xy_angle = math.atan2(target_direction.y, target_direction.x) * 180 / math.pi
        target_zy_angle = math.atan2(target_direction.y, target_direction.z) * 180 / math.pi

        car_pitch = car_orientation.pitch * 180 / math.pi
        car_roll = car_orientation.roll * 180 / math.pi
        car_yaw = car_orientation.yaw * 180 / math.pi

        # Draw some things to help understand what the bot is thinking
        # self.renderer.draw_line_3d(car_location, target_location, self.renderer.gray())
        # self.renderer.draw_rect_3d(target_location, 8, 8, True, self.renderer.orange(), centered=True)
        # self.renderer.draw_string_2d(10, 10, 2, 2, f'Target: {target_approach_speed:3.1f}', self.renderer.white())
        # self.renderer.draw_string_2d(10, 30, 2, 2, f'Ball: {target_approach_distance:3.1f}', self.renderer.white())
        # self.renderer.draw_string_2d(10, 50, 2, 2, f'Speed: {car_speed:3.1f}', self.renderer.white())

        # Controlling the car
        controls = SimpleControllerState()

        if ball_location.z > 300:
            self.car_single_jump(controls, my_car)
        controls.jump = self.jump.state

        if not my_car.has_wheel_contact:
            controls.pitch = self.pid_pitch.get_output(calculate_angle_error(target_z_angle, car_pitch), 0)
            controls.roll = self.pid_roll.get_output(calculate_angle_error(target_zy_angle, car_roll), 0)
            controls.yaw = self.pid_yaw.get_output(calculate_angle_error(target_xy_angle, car_yaw), 0)
            controls.boost = True

        return limit_controls(controls)

    def car_single_jump(self, controls, my_car):
        if my_car.has_wheel_contact is True:
            controls.jump = self.jump.toggle_hold(5)
