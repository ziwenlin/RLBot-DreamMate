import threading

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

from gui.application import AppThread
from tools.timers import TimedActionController
from util.vec import Vec3


class BunnyHop(BaseAgent):
    def __init__(self, name, index, team):
        super().__init__(name, index, team)
        self.controls = SimpleControllerState()
        self.action_controller = TimedActionController()

        self.current_time = 0
        self.previous_time = 0

        self.jump_position = Vec3()
        self.jump_velocity = Vec3()

        self.previous_acceleration = 0
        self.previous_velocity = 0

    def initialize_agent(self):
        self.gui_thread = AppThread()
        self.gui_thread.start()

        self.timed_jump(0, 0.0)
        self.timed_jump(2, 0.1)
        self.timed_jump(4, 0.2)
        self.timed_jump(7, 0.5)

    def retire(self):
        self.gui_thread.stop()
        self.gui_thread.join()
        super().retire()

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        self.controls = SimpleControllerState()
        self.action_controller.step(packet)

        self.previous_time = self.action_controller.previous_time
        self.current_time = self.action_controller.current_time

        self.plot_data(packet, 0, 10)
        return self.controls

    def plot_data(self, packet, time_start, time_end):
        if time_start >= self.current_time or self.current_time >= time_end:
            return
        my_car = packet.game_cars[0]

        position = Vec3(my_car.physics.location)
        velocity = Vec3(my_car.physics.velocity)

        height = position.z - self.jump_position.z
        speed = velocity.z - self.jump_velocity.z
        acceleration = (speed - self.previous_velocity) / (self.current_time - self.previous_time)
        self.previous_velocity = speed
        self.previous_acceleration = acceleration

        current_tick = self.current_time * 120
        self.gui_thread.send(f'acceleration:{acceleration / 100}:{current_tick}')
        self.gui_thread.send(f'velocity:{speed}:{current_tick}')
        self.gui_thread.send(f'position:{height}:{current_tick}')

    def timed_jump(self, time_trigger, jump_hold):
        increment = 1 / 120
        if jump_hold < 3 * increment:
            jump_hold = 2 * increment
        if jump_hold > 0.2:
            jump_hold = 0.2
        time_offset = 10 * increment

        def start(packet):
            my_car = packet.game_cars[0]
            self.jump_position = Vec3(my_car.physics.location)
            self.jump_velocity = Vec3(my_car.physics.velocity)
            target = lambda: self.predict_jump(self.current_time + time_offset, jump_hold)
            threading.Thread(target=target).start()

        def jump(_):
            self.controls.jump = True

        self.action_controller.create(time_trigger, 0, start)
        time_trigger += time_offset
        self.action_controller.create(time_trigger, jump_hold, jump)

    def predict_jump(self, start_time, hold_time):
        start_tick = start_time * 120 + 1
        hold_ticks = hold_time * 120 + 1
        if hold_ticks > 0.2 * 120:
            hold_ticks = 0.2 * 120
        increment = 1 / 120

        jump_force = 291.667
        jump_hold = jump_force * 5
        gravity = -650
        sticky = gravity * 0.5

        wheel_force = -gravity
        wheel_height = 13

        position = 0
        velocity = 0
        acceleration = 0
        self.gui_thread.send(f'prediction velocity:{velocity}:{start_tick}')
        self.gui_thread.send(f'prediction position:{position}:{start_tick}')
        self.gui_thread.send(f'prediction acceleration:{acceleration}:{start_tick}')

        for t in range(200 + int(hold_ticks * 2)):
            # Variables that needed immediate updates
            velocity_previous = velocity

            # Control variables
            if t == 0:  # or t is double jump
                velocity += jump_force  # - gravity * increment
            if t < 3 or t < hold_ticks:
                velocity += jump_hold * increment
            if t < 7:
                velocity += sticky * increment

            if position <= wheel_height and t > 7:
                # First wheel touches the ground
                wheel_suspension = wheel_force * self.wheel_behaviour(position, velocity)
                velocity += wheel_suspension * increment

            if position < -1 and t > 7 and velocity < 0:
                # All wheels touches the ground
                car_suspension = -velocity / increment / 2
                velocity += car_suspension * increment

            # Physics of simulation
            velocity += gravity * increment
            position += velocity * increment
            acceleration = (velocity - velocity_previous) / increment

            # Safety clipping values
            if position < -100:
                position = -100
            if acceleration < 10 * -100:
                acceleration = 10 * -100
            if velocity < -400:
                velocity = -400

            tick = start_tick + t + 1
            self.gui_thread.send(f'prediction acceleration:{acceleration / 100}:{tick}')
            self.gui_thread.send(f'prediction velocity:{velocity}:{tick}')
            self.gui_thread.send(f'prediction position:{position}:{tick}')

    def wheel_behaviour(self, position, velocity):
        wheel_velocity = 1 - velocity * 0.08
        wheel_position = position * 2.5 - 1
        wheel_multiplier = wheel_velocity - wheel_position
        if wheel_multiplier < 0:
            wheel_multiplier = 0
        return wheel_multiplier
