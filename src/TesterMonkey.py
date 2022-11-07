import math

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

import tools.training
from tools.helper import PIDController, limit_controls, JumpController, find_aerial_direction, calculate_angle_error, \
    SmoothTargetController, BoostController
from util.orientation import Orientation, relative_location
from util.vec import Vec3


class TestMonkey(BaseAgent):

    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.jump = JumpController()
        self.boost = BoostController()

        self.training = tools.training.TrainingController(index)

        self.pid_steer = PIDController(0.1, 0.0000001, 0.2)
        self.pid_pitch = PIDController(0.5, 0.000001, 4.8)
        self.pid_roll = PIDController(0.05, 0.000001, 1.2)
        self.pid_yaw = PIDController(0.2, 0.000001, 4.8)

        self.smooth_target = SmoothTargetController(0.2, 0.000001, 0.4)

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        # Gather some information about our car
        my_car = packet.game_cars[self.index]
        car_location = Vec3(my_car.physics.location)
        car_orientation = Orientation(my_car.physics.rotation)
        car_velocity = Vec3(my_car.physics.velocity)
        car_velocity_xy_angle = math.atan2(car_velocity.y, car_velocity.x) * 180 / math.pi
        car_relative_velocity = relative_location(Vec3(), car_orientation, car_velocity)
        car_ground_speed = car_velocity.flat().length()

        # Gather some information about the ball
        ball_location = Vec3(packet.game_ball.physics.location)
        ball_velocity = Vec3(packet.game_ball.physics.velocity)
        ball_relative = ball_location - car_location
        ball_xy_angle = math.atan2(ball_relative.y, ball_relative.x) * 180 / math.pi
        ball_direction = relative_location(car_location, car_orientation, ball_location)
        ball_direction_xy_angle = math.atan2(ball_direction.y, ball_direction.x) * 180 / math.pi
        ball_direction_z_angle = math.asin(ball_direction.z / ball_direction.length()) * 180 / math.pi

        self.training.step(packet)
        if self.training.need_boost():
            self.set_game_state(self.training.add_boost())
        elif self.training.is_finished():
            self.set_game_state(self.training.reset())

        target_direction = find_aerial_direction(ball_location, car_location, car_velocity)
        target_direction = self.smooth_target.step(target_direction)

        target_relative_direction = relative_location(Vec3(), car_orientation, target_direction)
        target_z_angle = math.asin(target_direction.z / target_direction.length()) * 180 / math.pi
        target_xy_angle = math.atan2(target_direction.y, target_direction.x) * 180 / math.pi
        target_zy_angle = math.atan2(target_direction.y, target_direction.z) * 180 / math.pi

        target_relative_xy_angle = math.atan2(target_relative_direction.y, target_relative_direction.x) * 180 / math.pi
        target_relative_zy_angle = math.atan2(target_relative_direction.y, target_relative_direction.z) * 180 / math.pi
        target_relative_z_angle = math.asin(target_relative_direction.z / target_relative_direction.length()) * 180 / math.pi

        car_pitch = car_orientation.pitch * 180 / math.pi
        car_roll = car_orientation.roll * 180 / math.pi
        car_yaw = car_orientation.yaw * 180 / math.pi

        # Draw some things to help understand what the bot is thinking
        self.renderer.draw_line_3d(car_location, car_location + target_direction, self.renderer.orange())
        self.renderer.draw_line_3d(car_location, car_location + car_velocity, self.renderer.cyan())
        self.renderer.draw_line_3d(ball_location, ball_location + ball_velocity, self.renderer.red())
        self.renderer.draw_rect_3d(car_location + target_direction, 8, 8, True, self.renderer.orange(), centered=True)
        self.renderer.draw_rect_3d(car_location + car_velocity, 8, 8, True, self.renderer.cyan(), centered=True)
        self.renderer.draw_rect_3d(ball_location + ball_velocity, 8, 8, True, self.renderer.red(), centered=True)

        self.renderer.draw_string_2d(10, 00, 3, 5, f'1: {target_xy_angle:3.1f}', self.renderer.white())
        self.renderer.draw_string_2d(10, 30, 3, 5, f'2: {target_z_angle:3.1f}', self.renderer.white())
        self.renderer.draw_string_2d(10, 60, 3, 5, f'3: {car_yaw:3.1f}', self.renderer.white())
        self.renderer.draw_string_2d(10, 90, 3, 5, f'3: {car_roll:3.1f}', self.renderer.white())

        # Controlling the car
        controls = SimpleControllerState()

        if (abs(target_relative_z_angle) < 15 and abs(target_relative_xy_angle) < 15):
            self.boost.toggle(1)
        elif (abs(target_relative_z_angle) < 30 and abs(target_relative_xy_angle) < 30):
            self.boost.toggle(5 / (abs(target_relative_z_angle) + abs(target_relative_xy_angle)))

        if ball_location.z > 300:
            error_xy_angle = calculate_angle_error(ball_xy_angle, car_velocity_xy_angle)
            if abs(error_xy_angle) < 15 and my_car.has_wheel_contact:
                self.jump.toggle(30)
            controls.steer = self.pid_steer.get_output(ball_direction_xy_angle, 0)
            controls.throttle = 0.1
            controls.handbrake = True

        if my_car.has_wheel_contact is False:
            controls.pitch = self.pid_pitch.get_output(target_relative_z_angle, 0)
            controls.roll = self.pid_roll.get_output(target_relative_zy_angle, 0)
            controls.yaw = self.pid_yaw.get_output(target_relative_xy_angle, 0)

        if car_location.z < 50 and abs(car_roll) > 170:
            controls.throttle = -1
            controls.roll = 1

        controls.jump = self.jump.step()
        controls.boost = self.boost.step()
        return limit_controls(controls)
