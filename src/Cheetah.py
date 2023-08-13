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

        self.pid_speed = PIDController(0.042, 0.000018, -0.007)
        self.pid_boost = PIDController(0.052, 0.000006, 0.001)
        self.previous_velocity = 0

    def initialize_agent(self):
        self.gui_thread = AppThread()
        self.gui_thread.start()

        # self.timed_drive(0, 5, 500, 0)
        # self.timed_drive(10, 5, 1000, 0)
        # self.timed_drive(20, 5, 1200, 0)

        # self.timed_drive(0, 5, 1200, 0)
        # self.timed_drive(10, 5, 1300, 0)
        # self.timed_drive(20, 5, 1400, 0)

        # self.timed_drive(0, 5, 1500, 0)
        # self.timed_drive(10, 5, 1800, 0)
        # self.timed_drive(20, 5, 2100, 0)

        # self.timed_drive(0, 5, 1000, 1)
        # self.timed_drive(10, 5, 1000, 0.5)
        # self.timed_drive(20, 5, 1000, 0)

        self.timed_drive(0, 4, 2000, 1)
        self.timed_drive(10, 4, 1000, 1)
        self.timed_drive(20, 2.5, 2000, 0)
        self.timed_drive(30, 4, 1000, 0)

    def retire(self):
        self.gui_thread.stop()
        self.gui_thread.join()
        super().retire()

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        self.controls = SimpleControllerState()
        # Pre-game or in replay or at kickoff countdown
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

        # Teleports/wraps the agent car back to the opposite site of the field
        if packet.game_cars[self.index].physics.location.y > 2000:
            game_state = GameState(cars={
                0: CarState(Physics(
                    location=Vector3(1000, -2000, 0)
                ))
            })
            self.set_game_state(game_state)

        # Getting target directions
        target_position = Vec3(10, 100, 20)
        target_velocity = Vec3(-200, 100, 0)
        target_direction = target_velocity.normalized()

        # Rendering target and direction
        self.renderer.begin_rendering()
        self.renderer.draw_rect_3d(target_position, 10, 10, True, self.renderer.red(), True)
        self.renderer.draw_line_3d(target_position, target_position + target_direction * 250, self.renderer.red())
        self.renderer.end_rendering()

        # plot the turn angles with power slide
        # make something that layers timed controls

        self.plot_data(packet, 0, 40)

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
                    location=Vector3(1000, -2000, 0),
                    rotation=Rotator(yaw=0.5 * math.pi, roll=0),
                    velocity=Vector3(0, 0, 0),
                ), 200)
            })
            self.set_game_state(game_state)
            self.gui_thread.send(f'velocity:{0}:{self.action_controller.current_time * 120}')
            self.gui_thread.send(f'acceleration:{0}:{self.action_controller.current_time * 120}')
            self.gui_thread.send(f'pid_speed:{0}:{self.action_controller.current_time * 120}')
            self.gui_thread.send(f'pid_boost:{0}:{self.action_controller.current_time * 120}')

        def drive(packet: GameTickPacket):
            self.renderer.draw_string_2d(
                10, 10, 10, 10,
                'Running', self.renderer.cyan()
            )

            my_car = packet.game_cars[self.index]
            velocity = Vec3(my_car.physics.velocity)
            speed = self.pid_speed.get_output(throttle, velocity.flat().length())
            speed *= abs(steer) * 0.75 + 0.25
            # speed *= throttle / 2400
            if speed < 0.015:
                speed = 0.015
            boost = self.pid_boost.get_output(throttle, velocity.flat().length())

            self.controls.throttle = util.drive.limit_to_safe_range(speed)
            self.controls.steer = steer
            self.controls.boost = boost > 1
            self.gui_thread.send(f'pid_speed:{speed * 100}:{self.action_controller.current_time * 120}')
            self.gui_thread.send(f'pid_boost:{boost * 100}:{self.action_controller.current_time * 120}')

        def finish(_):
            self.renderer.draw_string_2d(
                10, 10, 10, 10,
                'Cleaning', self.renderer.cyan()
            )
            self.pid_speed.reset()
            self.pid_boost.reset()
            self.gui_thread.send(f'pid_speed:{0}:{self.action_controller.current_time * 120}')
            self.gui_thread.send(f'pid_boost:{0}:{self.action_controller.current_time * 120}')

        self.action_controller.create(start, 0, setup)
        start += 10 / 120
        self.action_controller.create(start, hold, drive)
        start += hold
        self.action_controller.create(start, 0, finish)

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
