from typing import Callable

from rlbot.utils.structures.game_data_struct import GameTickPacket


class TimedAction:
    def __init__(self, start_time, hold_time, func: Callable[[GameTickPacket], None]):
        self.__run = func
        self.start_time = start_time
        self.end_time = start_time + hold_time
        self.is_active = False

    def run(self, packet, current_time):
        if self.start_time > current_time:
            return False
        if self.is_active is not True:
            self.end_time += current_time - self.start_time
            self.is_active = True
        elif current_time >= self.end_time:
            return True
        self.__run(packet)
        return False


class TimedActionController:
    def __init__(self, current_time):
        self.start_time = current_time
        self.current_time = current_time
        self.previous_time = current_time
        self.tick = -120
        self.actions: list[TimedAction] = []
        self.current_action = TimedAction(0, 0, lambda: None)

    def step(self, packet: GameTickPacket):
        time_elapsed = packet.game_info.seconds_elapsed
        self.process_time(time_elapsed)
        self.process_action(packet)

    def create(self, start, hold, function):
        action = TimedAction(start, hold, function)
        self.actions.append(action)

    def process_action(self, packet):
        action = self.current_action
        state = action.run(packet, self.current_time)
        if state is not True:
            return  # Action did not end yet
        if not len(self.actions) > 0:
            return  # No more available actions
        # Get the next action queued
        self.current_action = self.actions.pop(0)
        self.process_action(packet)

    def process_time(self, time_elapsed):
        if self.tick < 0:
            self.current_time = increment = -1 / 120
            self.start_time = time_elapsed - increment
        if self.tick == 0:
            self.start_time = time_elapsed
        self.previous_time = self.current_time
        self.current_time = time_elapsed - self.start_time
        self.tick += 1
