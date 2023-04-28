import math

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.game_state_util import GameState, CarState, Physics, Vector3, Rotator
from rlbot.utils.structures.game_data_struct import GameTickPacket
from rlbot.utils.structures.quick_chats import QuickChats

import util.drive
from gui.application import AppThread
from tools.contollers import PIDController
from tools.timers import TimedActionController
from util.vec import Vec3


class SprintingCheetah(BaseAgent):
    def __init__(self, name, index, team):
        super().__init__(name, index, team)
        self.controls = SimpleControllerState()
        self.action_controller = TimedActionController()

        self.pid_speed = PIDController(0.01, 0.0, 0.01)
        self.previous_velocity = 0

    def initialize_agent(self):
        self.gui_thread = AppThread()
        self.gui_thread.start()

        self.timed_drive(0, 3, 2000, 1)
        self.timed_drive(10, 3, 1000, 0)

    def retire(self):
        self.gui_thread.stop()
        self.gui_thread.join()
        super().retire()

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        self.controls = SimpleControllerState()
        # Pre-game or in replay
        if packet.game_info.is_round_active is not True:
            self.renderer.draw_string_2d(
                10, 10, 10, 10,
                'Paused', self.renderer.red()
            )
            return self.controls
        # During kickoff but after the countdown
        if packet.game_info.is_kickoff_pause is True:
            self.renderer.draw_string_2d(
                10, 10, 10, 10,
                'Kickoff', self.renderer.red()
            )
            return self.controls
        self.action_controller.step(packet)

        # plot the turn angles with power slide
        # make something that layers timed controls

        self.plot_data(packet, 0, 20)

        return self.controls

    def timed_drive(self, start, hold, throttle, steer):
        def setup(_):
            self.renderer.draw_string_2d(
                10, 10, 10, 10,
                'Starting', self.renderer.cyan()
            )
            self.send_quick_chat(
                QuickChats.CHAT_EVERYONE,
                QuickChats.Information_InPosition
            )
            game_state = GameState(cars={
                0: CarState(Physics(
                    location=Vector3(500, -4000, 0),
                    rotation=Rotator(yaw=0.5 * math.pi, roll=0),
                    velocity=Vector3(0, 0, 0),
                ), 200)
            })
            self.set_game_state(game_state)

        def drive(packet: GameTickPacket):
            self.renderer.draw_string_2d(
                10, 10, 10, 10,
                'Running', self.renderer.cyan()
            )

            my_car = packet.game_cars[self.index]
            velocity = Vec3(my_car.physics.velocity)
            value = self.pid_speed.get_output(throttle, velocity.flat().length())

            self.controls.throttle = util.drive.limit_to_safe_range(value)
            self.controls.steer = steer
            self.controls.boost = value > 2
            self.gui_thread.send(f'pid_speed:{value}:{self.action_controller.current_time * 120}')

        self.action_controller.create(start, 0, setup)
        start += 10 / 120
        self.action_controller.create(start, hold, drive)

    def plot_data(self, packet, time_start, time_end):
        current_time = self.action_controller.current_time
        previous_time = self.action_controller.previous_time
        if time_start >= current_time or current_time >= time_end:
            return
        my_car = packet.game_cars[self.index]

        increment = 1 / 120
        delta_time = current_time - previous_time
        if delta_time < increment * 1.5:
            delta_time = increment
        else:
            delta_time = round(delta_time * 120) / 120
        velocity = Vec3(my_car.physics.velocity)

        speed = velocity.flat().length()
        acceleration = (speed - self.previous_velocity) / delta_time
        self.previous_velocity = speed

        current_tick = current_time * 120
        self.gui_thread.send(f'acceleration:{acceleration}:{current_tick}')
        self.gui_thread.send(f'velocity:{speed}:{current_tick}')
