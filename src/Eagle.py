import math

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

import tools.training
from tools.helper import limit_controls, calculate_angle_error, \
    find_aerial_target_direction, find_aerial_direction, \
    find_aerial_target, get_target_goal, find_shot, find_aerial_ball
from tools.contollers import PIDController, JumpController, BoostController, SmoothTargetController, ControllerManager
from util.orientation import Orientation, relative_location
from util.vec import Vec3


class FlyingEagle(BaseAgent):

    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.jump = JumpController()
        self.boost = BoostController()

        self.training = tools.training.TrainingController(index)
        self.control_manager = ControllerManager()

        self.pid_steer = PIDController(0.1, 0.0000001, 0.2)
        self.pid_pitch = PIDController(0.3, 0.000001, 4.8)
        self.pid_roll = PIDController(0.005, 0.000001, 1.2)
        self.pid_yaw = PIDController(0.01, 0.000001, 0.6)

        self.smooth_target = SmoothTargetController(0.2, 0.000001, 0.4)
        self.control_manager.add_controller(self.smooth_target, 'smooth')
        self.control_manager.add_controller(self.pid_steer, 'steer')
        self.control_manager.add_controller(self.pid_pitch, 'pitch')
        self.control_manager.add_controller(self.pid_roll, 'roll')
        self.control_manager.add_controller(self.pid_yaw, 'yaw')
        self.control_manager.add_controller(self.boost, 'boost')
        self.control_manager.add_controller(self.jump, 'jump')

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
            if self.training.is_done():
                self.set_game_state(self.training.reset(''))
            self.control_manager.reset()
            return SimpleControllerState()

        # goal_a, goal_b = get_target_goal(self.team)
        # target_location = find_aerial_ball(car_location, car_velocity, self.get_ball_prediction_struct(), packet)
        # target_shot = find_shot(goal_a, goal_b, target_location, car_location)
        # target_direction = find_aerial_direction(target_shot, car_location, car_velocity)

        # goal_a, goal_b = get_target_goal(self.team)
        # target_location = find_aerial_target(ball_location, ball_velocity, car_location, car_velocity)
        # target_shot = find_shot(goal_a, goal_b, target_location, car_location)
        # target_direction = find_aerial_direction(target_shot, car_location, car_velocity)

        # goal_a, goal_b = get_target_goal(self.team)
        # target_shot = find_shot(goal_a, goal_b, ball_location, car_location)
        # target_location = find_aerial_target(target_shot, ball_velocity, car_location, car_velocity)
        # target_direction = find_aerial_direction(target_location, car_location, car_velocity)

        # goal_a, goal_b = get_target_goal(self.team)
        # target_location = target_shot = find_shot(goal_a, goal_b, ball_location, car_location)
        # target_direction = find_aerial_target_direction(target_location, ball_velocity, car_location, car_velocity)
        # target_direction = self.smooth_target.step(target_direction)

        target_location = target_shot = ball_location
        target_direction = find_aerial_target_direction(target_location, ball_velocity, car_location, car_velocity)
        target_direction = self.smooth_target.step(target_direction)

        target_z_angle = math.asin(target_direction.z / target_direction.length()) * 180 / math.pi
        target_xy_angle = math.atan2(target_direction.y, target_direction.x) * 180 / math.pi
        target_zy_angle = math.atan2(target_direction.y, target_direction.z) * 180 / math.pi

        target_relative_direction = relative_location(Vec3(), car_orientation, target_direction)
        target_relative_direction_length = target_relative_direction.length()

        target_relative_xy_angle = math.atan2(target_relative_direction.y, target_relative_direction.x) * 180 / math.pi
        target_relative_zy_angle = math.atan2(target_relative_direction.y, target_relative_direction.z) * 180 / math.pi
        target_relative_z_angle = math.asin(target_relative_direction.z / target_relative_direction_length) * 180 / math.pi

        car_pitch = car_orientation.pitch * 180 / math.pi
        car_roll = car_orientation.roll * 180 / math.pi
        car_yaw = car_orientation.yaw * 180 / math.pi

        # Draw some things to help understand what the bot is thinking
        self.renderer.draw_line_3d(car_location, car_location + target_direction, self.renderer.orange())
        self.renderer.draw_line_3d(car_location, car_location + car_velocity, self.renderer.cyan())
        self.renderer.draw_line_3d(ball_location, ball_location + ball_velocity, self.renderer.cyan())
        self.renderer.draw_line_3d(car_location, target_location, self.renderer.red())

        self.renderer.draw_rect_3d(car_location + target_direction, 8, 8, True, self.renderer.orange(), centered=True)
        self.renderer.draw_rect_3d(car_location + car_velocity, 8, 8, True, self.renderer.cyan(), centered=True)
        self.renderer.draw_rect_3d(ball_location + ball_velocity, 8, 8, True, self.renderer.cyan(), centered=True)
        self.renderer.draw_rect_3d(target_location, 16, 16, True, self.renderer.red(), centered=True)

        self.renderer.draw_rect_3d(target_shot, 16, 16, True, self.renderer.red(), centered=True)

        self.renderer.draw_string_2d(10, 00, 3, 5, f'1: {my_car.has_wheel_contact}', self.renderer.white())
        self.renderer.draw_string_2d(10, 30, 3, 5, f'2: {my_car.jumped}', self.renderer.white())
        self.renderer.draw_string_2d(10, 60, 3, 5, f'3: {my_car.double_jumped}', self.renderer.white())
        self.renderer.draw_string_2d(10, 90, 3, 5, f'3: {my_car.is_super_sonic}', self.renderer.white())

        # Controlling the car
        controls = SimpleControllerState()

        if abs(target_relative_z_angle) < 20 and abs(target_relative_xy_angle) < 20:
            self.boost.toggle(1)
        elif abs(target_relative_z_angle) < 40 and abs(target_relative_xy_angle) < 40:
            self.boost.toggle(5 / (abs(target_relative_z_angle) + abs(target_relative_xy_angle)))

        if my_car.has_wheel_contact is True:
            self.jump.reset()
            if abs(target_relative_xy_angle) < 15 and target_relative_z_angle > 60:
                self.jump.toggle(30)
            controls.steer = self.pid_steer.get_output(target_relative_xy_angle, 0)
            if target_relative_z_angle < 60:
                controls.throttle = 1
            else:
                controls.throttle = 0.1
            controls.handbrake = abs(target_relative_xy_angle) > 20


        if my_car.has_wheel_contact is False:
            controls.pitch = self.pid_pitch.get_output(target_relative_z_angle, 0)
            controls.roll = self.pid_roll.get_output(target_relative_zy_angle, 0)
            controls.yaw = self.pid_yaw.get_output(target_relative_xy_angle, 0)

        # if car_location.z < 50 and abs(car_roll) > 170:
        #     controls.roll = self.pid_roll.get_output(0, car_roll)
        #     controls.throttle = -1
        #     self.jump.toggle(1)

        # if my_car.has_wheel_contact is False and car_location.z < 500 and ball_direction_z_angle > 60:
        #     angle = calculate_angle_error(90, car_pitch)
        #     controls.pitch = self.pid_pitch.get_output(angle, 0)
        #     if abs(angle) < 45 and my_car.jumped is True and my_car.double_jumped is False:
        #         controls.pitch = controls.roll = controls.yaw = 0
        #         self.jump.toggle(5)
        #     self.boost.toggle(10 / abs(angle))
        #
        # if my_car.is_super_sonic is True:
        #     self.boost.toggle(0.8)

        self.control_manager.step()
        controls.jump = self.jump.step()
        controls.boost = self.boost.step()
        return limit_controls(controls)
