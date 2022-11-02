import math

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket, FieldInfoPacket, GoalInfo

from tools.helper import find_shot, PIDController, find_boost_in_path, clip_to_field, predict_ball_fall
from tools.performance import TickMonitor
from util.ball_prediction_analysis import find_slice_at_time
from util.boost_pad_tracker import BoostPadTracker
from util.drive import steer_toward_target, limit_to_safe_range
from util.orientation import relative_location, Orientation
from util.sequence import Sequence, ControlStep
from util.vec import Vec3


class MyBot(BaseAgent):

    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.active_sequence = Sequence([])
        self.boost_pad_tracker = BoostPadTracker()

        self.pid_speed = PIDController(100, 0.1, 5)
        self.pid_steer = PIDController(0.1, 0.0002, 0.2)
        self.pid_pitch = PIDController(1, 0, 0)
        self.pid_roll = PIDController(1, 0, 0)

        self.goal_info = None
        self.no_error_running = True

        self.need_boost = False
        self.is_flipping = False
        self.last_steering = 0

        self.time_flipped = 0
        self.time_jumped = 0
        self.time_steering = 0

        self.time = 0
        self.tick = TickMonitor()

    def initialize_agent(self):
        # Set up information about the boost pads now that the game is active and the info is available
        self.boost_pad_tracker.initialize_boosts(self.get_field_info())
        field_info: FieldInfoPacket = self.get_field_info()
        self.goal_info = [field_info.goals[x] for x in range(field_info.num_goals)]

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        """
        This function will be called by the framework many times per second. This is where you can
        see the motion of the ball, etc. and return controls to drive your car.
        """

        # Keep our boost pad info updated with which pads are currently active
        self.boost_pad_tracker.update_boost_status(packet)
        self.tick.step()

        # This is good to keep at the beginning of get_output. It will allow you to continue
        # any sequences that you may have started during a previous call to get_output.
        if self.active_sequence is not None and not self.active_sequence.done:
            controls = self.active_sequence.tick(packet)
            if controls is not None:
                self.no_error_running = True
                return controls

        # Gather some information about our car and the ball
        my_car = packet.game_cars[self.index]
        car_location = Vec3(my_car.physics.location)
        car_velocity = Vec3(my_car.physics.velocity)
        car_speed = car_velocity.length()
        car_orientation = Orientation(my_car.physics.rotation)
        ball_location = Vec3(packet.game_ball.physics.location)
        ball_relative = relative_location(car_location, car_orientation, ball_location)
        ball_angle = math.atan2(ball_relative.y, ball_relative.x)
        ball_angle *= 180 / math.pi
        ball_distance = car_location.dist(ball_location)

        # Prediction of the ball according to how quickly the car moves
        prediction_speed = (1100 - car_speed) // 220 / 10
        prediction_time = 0.2 * (ball_distance // 150)
        prediction_time += prediction_speed

        # We're far away from the ball, let's try to lead it a little
        ball_prediction_struct = self.get_ball_prediction_struct()  # This can predict bounces, etc
        ball_in_future = find_slice_at_time(
            ball_prediction_struct, packet.game_info.seconds_elapsed + prediction_time)

        # ball_in_future might be None if we don't have an adequate ball prediction right now, like during
        # replays, so check it to avoid errors.
        if ball_distance > 500 and ball_in_future is not None:
            ball_prediction = Vec3(ball_in_future.physics.location)
            self.renderer.draw_rect_3d(ball_prediction, 8, 8, True, self.renderer.red(), centered=True)

        if self.team == 0:
            target_goal_a = Vec3(800, 5213, 321)
            target_goal_b = Vec3(-800, 5213, 321)
        else:
            target_goal_a = Vec3(-800, -5213, 321)
            target_goal_b = Vec3(800, -5213, 321)

        # not_my_car = packet.game_cars[packet.num_cars]
        self.need_boost = my_car.boost < 12

        # By default, we will chase the ball, but target_location can be changed later
        target_location = find_shot(target_goal_a, target_goal_b, ball_location, car_location)

        if packet.game_info.is_kickoff_pause:
            return self.do_kickoff(ball_location, car_location, car_orientation, packet)

        # Look for boost while approaching the ball
        if ball_distance > 500 and my_car.boost < 66:
            closest_boost = find_boost_in_path(car_location, target_location, self.boost_pad_tracker)
            if closest_boost is not None:
                target_location = closest_boost

        # Need more boost
        if my_car.boost < 20 or self.need_boost:
            my_goal: GoalInfo = self.goal_info[self.team]
            goal_location = Vec3(my_goal.location)
            closest_boost = find_boost_in_path(car_location, goal_location, self.boost_pad_tracker)
            if closest_boost is not None:
                target_location = closest_boost

        ball_time = 1

        if ball_location.z > 200:
            # When the ball is in the air wait for it to come down.
            # We're far away from the ball, let's try to lead it a little
            ball_prediction_struct = self.get_ball_prediction_struct()
            ball_approach_time, ball_prediction = predict_ball_fall(
                ball_location, ball_prediction_struct, packet)
            target_location = find_shot(target_goal_a, target_goal_b, ball_prediction, car_location)
            ball_prediction = target_location
        else:
            ball_approach_time = 0.1
            ball_prediction = ball_location

        target_location = clip_to_field(target_location)

        # Draw some things to help understand what the bot is thinking
        self.renderer.draw_line_3d(car_location, target_location, self.renderer.white())
        self.renderer.draw_rect_3d(target_location, 8, 8, True, self.renderer.cyan(), centered=True)
        self.renderer.draw_rect_3d(ball_prediction, 8, 8, True, self.renderer.pink(), centered=True)

        line_coord_a = ball_location
        for i in range(50):
            ball_in_future = find_slice_at_time(
                ball_prediction_struct, packet.game_info.seconds_elapsed + 0.1 * i)
            if ball_in_future is None:
                break
            line_coord_b = Vec3(ball_in_future.physics.location)
            self.renderer.draw_line_3d(line_coord_a, line_coord_b, self.renderer.cyan())
            line_coord_a = line_coord_b

        # Controller state
        controls = SimpleControllerState()
        controls.steer = steer_toward_target(my_car, target_location)
        controls.yaw = controls.steer

        target_distance = target_location.length()
        needed_car_speed = target_distance / ball_time
        if needed_car_speed > 2200:
            needed_car_speed = 2200
        elif needed_car_speed < 100:
            needed_car_speed = 100

        controls.throttle = self.pid_speed.get_output(needed_car_speed, car_velocity.length())
        controls.throttle = limit_to_safe_range(controls.throttle)

        # Calculations after the target is determined
        target_relative = relative_location(car_location, car_orientation, target_location)
        target_angle = math.atan2(target_relative.y, target_relative.x)
        target_angle *= 180 / math.pi

        if my_car.has_wheel_contact is False:
            controls.pitch = -1 * math.tanh(car_orientation.pitch * 1.2)
            controls.roll = -1 * math.tanh(car_orientation.roll * 1.2)

        if ball_relative.z < 300 and \
                ball_relative.x < 333 and \
                car_speed > 500 and \
                -10 < ball_angle < 10 and my_car.has_wheel_contact:
            return self.do_front_flip(packet)

        if -20 < ball_angle < 20 and \
                ball_relative.z < 500 and \
                ball_relative.x > 2000 and my_car.has_wheel_contact:
            controls.boost = True
            # return self.do_front_flip(packet)

        if -100 < ball_relative.y < 100 and \
                ball_relative.z < 120 and \
                ball_relative.x > 100:
            controls.boost = True

        if target_relative.x < 100 and -50 > target_angle > 50:
            controls.steer *= -1
            controls.throttle = -1
            controls.handbrake = True
            controls.boost = False

        if car_speed > 2200:
            controls.boost = False

        if -120 > target_angle > 120 and target_relative.x < 0 and my_car.has_wheel_contact:
            return self.do_half_flip(packet)

        if controls.steer == self.last_steering:
            self.time_steering += 1
            if self.time_steering > self.tick.tps * 3 and my_car.has_wheel_contact:
                print(self.tick.tps, self.tick.last_time)
                return self.do_half_flip(packet)
        else:
            self.time_steering = 0
            self.last_steering = controls.steer

        return controls

    def do_kickoff(self, ball_location, car_location, car_orientation, packet):
        if car_location.dist(ball_location) < 500:
            return self.do_front_flip(packet)
        relative = relative_location(car_location, car_orientation, ball_location)
        angle = math.atan2(relative.y, relative.x) * 360
        controls = SimpleControllerState()
        controls.steer = self.pid_steer.get_output(angle, 0)
        controls.steer = limit_to_safe_range(controls.steer)
        controls.throttle = 1.0
        controls.boost = True
        return controls

    def do_half_flip(self, packet):
        # Do a front flip. We will be committed to this for a few seconds and the bot will ignore other
        # logic during that time because we are setting the active_sequence.
        self.active_sequence = Sequence([
            ControlStep(duration=0.2, controls=SimpleControllerState(throttle=-1, steer=-0.2)),
            ControlStep(duration=0.1, controls=SimpleControllerState(jump=True)),
            ControlStep(duration=0.1, controls=SimpleControllerState(jump=False, pitch=1)),
            ControlStep(duration=0.2, controls=SimpleControllerState(jump=True, pitch=1)),
            ControlStep(duration=0.2, controls=SimpleControllerState(pitch=-1)),
            ControlStep(duration=0.4, controls=SimpleControllerState(pitch=-1, roll=1, boost=True)),
            ControlStep(duration=0.4, controls=SimpleControllerState(roll=1, throttle=1, boost=True)),
        ])

        # Return the controls associated with the beginning of the sequence, so we can start right away.
        return self.active_sequence.tick(packet)

    def do_front_flip(self, packet):
        # Send some quick-chat just for fun
        # self.send_quick_chat(team_only=False, quick_chat=QuickChatSelection.Information_IGotIt)

        # Do a front flip. We will be committed to this for a few seconds and the bot will ignore other
        # logic during that time because we are setting the active_sequence.
        self.active_sequence = Sequence([
            ControlStep(duration=0.1, controls=SimpleControllerState(jump=True)),
            ControlStep(duration=0.1, controls=SimpleControllerState(jump=False, pitch=-1)),
            ControlStep(duration=0.2, controls=SimpleControllerState(jump=True, pitch=-1)),
            ControlStep(duration=0.8, controls=SimpleControllerState()),
        ])

        # Return the controls associated with the beginning of the sequence, so we can start right away.
        return self.active_sequence.tick(packet)

    def car_steer_control(self, controls, target_angle):
        controls.steer = self.pid_steer.get_output(target_angle, 0)
        if -1.2 > controls.steer > 1.2:
            controls.handbrake = True
        controls.steer = limit_to_safe_range(controls.steer)

    def car_throttle_control(self, controls, current_car_speed, needed_car_speed):
        controls.throttle = self.pid_speed.get_output(needed_car_speed, current_car_speed)
        controls.throttle = limit_to_safe_range(controls.throttle)

    def car_air_control(self, car_orientation, controls, my_car):
        # Stabilize car in the air
        if my_car.has_wheel_contact is False:
            controls.pitch = self.pid_pitch.get_output(0, car_orientation.pitch)
            controls.roll = self.pid_roll.get_output(0, car_orientation.roll)
            controls.pitch = limit_to_safe_range(controls.pitch)
            controls.roll = limit_to_safe_range(controls.roll)
