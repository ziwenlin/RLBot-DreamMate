from typing import Dict, Union

from util.vec import Vec3


class PIDController:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.i_value = 0
        self.d_value = 0

    def get_output(self, target, value):
        error = target - value
        p = self.kp * error
        i = self.ki * (error + self.i_value)
        d = self.kd * (error - self.d_value)
        self.d_value = error
        self.i_value += error
        return p + i + d

    def reset(self):
        self.d_value = 0
        self.i_value = 0


class JumpController:
    def __init__(self):
        self.hold_time = 1
        self.state = False
        self.timer = 0

    def toggle(self, hold_time=1):
        self.hold_time = hold_time
        self.state = True

    def step(self):
        if self.state is False:
            return False
        if self.timer < self.hold_time:
            self.timer += 1
        else:
            self.timer = 0
            self.state = False
        return True

    def reset(self):
        self.state = False
        self.timer = 0


class BoostController:
    def __init__(self):
        self.hold_time = 1
        self.release_time = 1
        self.state = False
        self.timer = 0

    def toggle(self, sureness=1):
        if sureness > 1:
            sureness = 1
        if sureness < 0:
            return
        self.hold_time = 5 * sureness
        self.release_time = 5 * (1 - sureness)
        self.state = True

    def reset(self):
        self.state = False
        self.timer = 0

    def step(self):
        if self.state is False:
            return False
        self.timer += 1
        if self.timer > self.hold_time + self.release_time:
            self.timer = 0
            self.state = False
        elif self.timer > self.hold_time:
            return False
        return True


class SmoothTargetController:
    def __init__(self, kp, ki, kd):
        self.pid_x = PIDController(kp, ki, kd)
        self.pid_y = PIDController(kp, ki, kd)
        self.pid_z = PIDController(kp, ki, kd)
        self.target = Vec3()

    def step(self, target: Vec3):
        self.target.x += self.pid_x.get_output(target.x, self.target.x)
        self.target.y += self.pid_y.get_output(target.y, self.target.y)
        self.target.z += self.pid_z.get_output(target.z, self.target.z)
        return self.target

    def reset(self):
        self.target = Vec3()
        self.pid_x.reset()
        self.pid_y.reset()
        self.pid_z.reset()


class ControllerManager:
    def __init__(self):
        self.controllers: Dict[str, Union[
            PIDController, SmoothTargetController, JumpController, BoostController
        ]] = {}
        self.previous = {}

    def add_controller(self, controller, name):
        self.controllers[name] = controller
        self.previous[name] = 0

    def step(self):
        for name in self.controllers:
            controller = self.controllers[name]
            previous = self.previous[name]
            if controller is PIDController:
                if controller.i_value == previous:
                    controller.reset()
                previous = controller.i_value
            elif controller is SmoothTargetController:
                if controller.target == previous:
                    controller.reset()
                previous = controller.target
            self.previous[name] = previous

    def reset(self):
        for name in self.controllers:
            controller = self.controllers[name]
            if controller is PIDController or controller is SmoothTargetController:
                controller.reset()
            elif controller is BoostController or controller is JumpController:
                controller.reset()
