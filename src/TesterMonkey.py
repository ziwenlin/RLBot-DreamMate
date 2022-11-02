import math

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

from tools.helper import find_shot, PIDController, clip_to_field, get_target_goal, get_required_speed
from util.ball_prediction_analysis import find_slice_at_time
from util.boost_pad_tracker import BoostPadTracker
from util.drive import limit_to_safe_range
from util.orientation import Orientation, relative_location
from util.sequence import Sequence, ControlStep
from util.vec import Vec3


class MyBot(BaseAgent):

    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.active_sequence = Sequence([])
        self.boost_pad_tracker = BoostPadTracker()

        self.pid_speed = PIDController(10, 0.1, 5)
        self.pid_steer = PIDController(0.05, 0.0002, 0.1)
        self.pid_pitch = PIDController(1, 0.01, 0.5)
        self.pid_roll = PIDController(1, 0.01, 0.5)

    def initialize_agent(self):
        # Set up information about the boost pads now that the game is active and the info is available
        self.boost_pad_tracker.initialize_boosts(self.get_field_info())

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        """
        This function will be called by the framework many times per second. This is where you can
        see the motion of the ball, etc. and return controls to drive your car.
        """

        # Keep our boost pad info updated with which pads are currently active
        self.boost_pad_tracker.update_boost_status(packet)

        # This is good to keep at the beginning of get_output. It will allow you to continue
        # any sequences that you may have started during a previous call to get_output.
        if self.active_sequence is not None and not self.active_sequence.done:
            controls = self.active_sequence.tick(packet)
            if controls is not None:
                return controls

        # Gather some information about our car
        my_car = packet.game_cars[self.index]
        car_location = Vec3(my_car.physics.location)
        car_orientation = Orientation(my_car.physics.rotation)
        car_velocity = Vec3(my_car.physics.velocity)
        car_speed = car_velocity.flat().length()

        # Gather some information about the ball
        ball_location = Vec3(packet.game_ball.physics.location)
        ball_relative = relative_location(car_location, car_orientation, ball_location)
        ball_angle = math.atan2(ball_relative.y, ball_relative.x)
        ball_angle *= 360 / math.pi

        # Gather some information about the goals
        target_goal_a, target_goal_b = get_target_goal(self.team)

        # By default, we will chase the ball, but target_location can be changed later
        target_location = find_shot(target_goal_a, target_goal_b, ball_location, car_location)

        ball_prediction_struct = self.get_ball_prediction_struct()  # This can predict bounces, etc

        if packet.game_info.is_kickoff_pause:
            return self.do_kickoff(ball_location, car_location, car_orientation, packet)

        ball_approach_time = 0.1
        ball_prediction = ball_location
        if ball_location.z > 200:
            # When the ball is in the air wait for it to come down.
            # We're far away from the ball, let's try to lead it a little
            for i in range(50):
                ball_in_future = find_slice_at_time(
                    ball_prediction_struct, packet.game_info.seconds_elapsed + 0.1 * i)
                if ball_in_future is None:
                    break
                new_ball_prediction = Vec3(ball_in_future.physics.location)
                if new_ball_prediction.z < ball_prediction.z:
                    ball_prediction = new_ball_prediction
                elif ball_prediction.z < 200:
                    ball_approach_time = 0.1 * i
                    ball_prediction_distance = ball_prediction.length()
                    approach_speed = ball_prediction_distance / ball_approach_time
                    if approach_speed > 1400:
                        continue
                    break
            target_location = find_shot(target_goal_a, target_goal_b, ball_prediction, car_location)
            ball_prediction = target_location

        target_location = clip_to_field(target_location)
        target_relative = relative_location(car_location, car_orientation, target_location)
        target_angle = math.atan2(target_relative.y, target_relative.x)
        target_angle *= 360 / math.pi

        target_distance = target_location.length()
        target_approach_distance = target_distance + 0.2 * abs(target_relative.x) - 0.8 * abs(target_relative.y)
        target_approach_speed = get_required_speed(ball_approach_time, target_approach_distance)

        # Draw some things to help understand what the bot is thinking
        self.renderer.draw_line_3d(car_location, target_location, self.renderer.gray())
        self.renderer.draw_string_3d(car_location, 1, 1, f'Speed: {car_velocity.length():.1f}', self.renderer.white())
        self.renderer.draw_rect_3d(target_location, 8, 8, True, self.renderer.orange(), centered=True)
        self.renderer.draw_rect_3d(ball_prediction, 8, 8, True, self.renderer.pink(), centered=True)

        controls = SimpleControllerState()
        self.car_air_control(car_orientation, controls, my_car)
        self.car_steer_control(controls, target_angle)
        self.car_throttle_control(controls, car_speed, target_approach_speed)

        return controls

    def car_steer_control(self, controls, target_angle):
        controls.steer = self.pid_steer.get_output(target_angle, 0)
        if -1.0 > controls.steer > 1.0 or -30 > target_angle > 30:
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
