import math
from typing import Dict, Union

from rlbot.agents.base_agent import SimpleControllerState

from util.ball_prediction_analysis import find_slice_at_time
from util.boost_pad_tracker import BoostPadTracker
from util.drive import limit_to_safe_range
from util.vec import Vec3


def find_shot(target_a, target_b, ball_location, car_location):
    try:
        car_to_ball = ball_location - car_location
        car_to_ball_direction = car_to_ball.normalized()
    except ZeroDivisionError:
        return ball_location

    ball_to_left_target_direction = (target_a - ball_location).normalized()
    ball_to_right_target_direction = (target_b - ball_location).normalized()
    direction_of_approach = clamp2D(car_to_ball_direction,
                                    ball_to_left_target_direction,
                                    ball_to_right_target_direction)

    offset_ball_location = ball_location - (direction_of_approach * 92.75)

    try:
        side_of_approach_direction = sign(
            (ball_location - car_location).dot(direction_of_approach.cross(Vec3(0, 0, 1))))
        car_to_ball_perpendicular = car_to_ball.cross(Vec3(0, 0, side_of_approach_direction)).normalized()
        adjustment = abs(car_to_ball.flat().ang_to(direction_of_approach.flat())) * 2560
        final_target = offset_ball_location + (car_to_ball_perpendicular * adjustment)
    except ZeroDivisionError:
        return offset_ball_location
    except ValueError:
        return offset_ball_location
    return final_target


def clamp2D(direction, start, end):
    """

    :param Vec3 direction:
    :param Vec3 start:
    :param Vec3 end:
    """
    is_right = direction.dot(end.cross(Vec3(0, 0, -1))) < 0
    is_left = direction.dot(start.cross(Vec3(0, 0, -1))) > 0

    if end.dot(start.cross(Vec3(0, 0, -1))) > 0:
        if is_left and is_right:
            return direction
    else:
        if is_left or is_right:
            return direction

    if start.dot(direction) < end.dot(direction):
        return end

    return start


def sign(value):
    if value < 0:
        return -1
    return 1


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


def clip_to_field(location: Vec3):
    # Check field
    mid_p = Vec3(4000, 5100, 2000)
    mid_n = Vec3(-4000, -5100, 0)
    # mid = check_valid_location(location, mid_p, mid_n)

    # Check goals
    # goal_p = Vec3(800, 6000, 642)
    # goal_n = Vec3(-800, -6000, 0)
    # goal = check_valid_location(location, goal_p, goal_n)

    # if sum(mid) > sum(goal):
    #     return clip_to_box(location, mid_p, mid_n)
    # elif sum(goal) > sum(mid):
    #     return clip_to_box(location, goal_p, mid_p)
    return clip_to_box(location, mid_p, mid_n)


def clip_to_box(location, box_p, box_n):
    """

    :param Vec3 location:
    :param Vec3 box_p:
    :param Vec3 box_n:
    """

    def clip_within_box(value, corner_a, corner_b):
        if value > corner_a:
            return corner_a
        elif value < corner_b:
            return corner_b
        return value

    x = clip_within_box(location.x, box_p.x, box_n.x)
    y = clip_within_box(location.y, box_p.y, box_n.y)
    z = clip_within_box(location.z, box_p.z, box_n.z)
    return Vec3(x, y, z)


def check_valid_location(location, box_p, box_n):
    """

    :param Vec3 location:
    :param Vec3 box_p:
    :param Vec3 box_n:
    """

    def check_within_box(check, corner_a, corner_b):
        """

        :param float check:
        :param float corner_a:
        :param float corner_b:
        """
        return corner_a > check > corner_b

    x = check_within_box(location.x, box_p.x, box_n.x)
    y = check_within_box(location.y, box_p.y, box_n.y)
    z = check_within_box(location.z, box_p.z, box_n.z)
    return x, y, z


def get_target_goal(team):
    if team == 0:
        target_goal_a = Vec3(800, 5213, 321)
        target_goal_b = Vec3(-800, 5213, 321)
    else:
        target_goal_a = Vec3(-800, -5213, 321)
        target_goal_b = Vec3(800, -5213, 321)
    return target_goal_a, target_goal_b


def get_required_speed(time_remaining, distance_remaining):
    target_approach_speed = distance_remaining / time_remaining
    if 400 < target_approach_speed < 800:
        target_approach_speed = 200
    if target_approach_speed > 2200:
        target_approach_speed = 2200
    return target_approach_speed


def find_boost_in_path(car, target, boost_map):
    """

    :param BoostPadTracker boost_map:
    :param Vec3 target:
    :param Vec3 car:
    """

    distance_car_to_target = car.dist(target)
    closest_boost = None
    for pad in boost_map.boost_pads:
        distance_to_target = pad.location.dist(target)
        distance_to_car = pad.location.dist(car)
        if not pad.is_active:
            # Skip non-active boost pads
            continue
        if pad.is_full_boost:
            # Give a bit more priority to full boost
            distance_to_target -= 300
        if distance_to_target + distance_to_car > distance_car_to_target * 1.2:
            # Skip if the boost is not on track of the path
            continue
        if closest_boost is None:
            # If no boost has been selected, so temporarily select it
            closest_boost = (pad, distance_to_car, distance_to_target)
            continue
        is_closer_to_car = distance_to_car < closest_boost[1]
        is_closer_to_target = distance_to_target < closest_boost[2]
        if (is_closer_to_target or is_closer_to_car) is False:
            # This boost is not closer to the target nor the car, so pass
            continue
        elif (is_closer_to_target and is_closer_to_car) is False:
            # This boost is closer to something, so we need to calculate
            # Give more priority to boost closer to the car
            sum_current = distance_to_car + distance_to_target * 1.5
            sum_previous = closest_boost[1] + closest_boost[2] * 1.5
            if sum_previous < sum_current:
                # Boost is not closer to the car
                continue
        closest_boost = (pad, distance_to_car, distance_to_target)

    if closest_boost is None:
        return None
    return closest_boost[0].location


def predict_ball_fall(ball_prediction, ball_prediction_struct, packet):
    game_time = packet.game_info.seconds_elapsed
    ball_approach_time = 0.1
    for i in range(50):
        ball_in_future = find_slice_at_time(
            ball_prediction_struct, game_time + 0.1 * i)
        if ball_in_future is None:
            # There is nothing to predict
            break
        # Convert the location to Vec3
        new_ball_prediction = Vec3(ball_in_future.physics.location)
        if new_ball_prediction.z < ball_prediction.z:
            # The new prediction needs to be lower than the previous prediction
            ball_prediction = new_ball_prediction
        elif ball_prediction.z < 200:
            ball_approach_time = 0.1 * i
            ball_prediction_distance = ball_prediction.length()
            approach_speed = ball_prediction_distance / ball_approach_time
            if approach_speed > 800:
                continue
            ball_prediction = new_ball_prediction
            break
    return ball_approach_time, ball_prediction


def limit_controls(controls: SimpleControllerState):
    controls.pitch = limit_to_safe_range(controls.pitch)
    controls.yaw = limit_to_safe_range(controls.yaw)
    controls.roll = limit_to_safe_range(controls.roll)
    controls.steer = limit_to_safe_range(controls.steer)
    controls.throttle = limit_to_safe_range(controls.throttle)
    return controls


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


def find_aerial_target_direction(target: Vec3, target_velocity: Vec3, car_location: Vec3, car_velocity: Vec3):
    relative_target = BetterVec3(target - car_location)

    car_speed = car_velocity.length() + 1
    trajectory_time = abs(relative_target.xyz_length / car_speed)

    increment_z_angle = 10
    increment_xy_angle = 10
    increment_boost = 1
    last_z_angle_error = 1000
    last_xy_angle_error = 1000
    last_boost_error = 1000

    gravity = Vec3(0, 0, 650)
    boost_direction = BetterVec3(relative_target.normalized())

    if relative_target.xyz_length < car_speed / 2:
        return car_velocity

    for i in range(15):
        future_target_position = BetterVec3(relative_target + target_velocity * trajectory_time
                                            + 0.5 * -gravity * trajectory_time ** 2)
        needed_car_velocity = future_target_position / trajectory_time
        needed_car_acceleration = (needed_car_velocity - car_velocity) / trajectory_time
        boost_force = needed_car_acceleration + gravity

        boost_error = 991.667 - boost_force.length()
        if abs(boost_error) > abs(last_boost_error):
            increment_boost *= -0.5
        trajectory_time += increment_boost
        last_boost_error = boost_error

    for i in range(15):
        acceleration = boost_direction * 991.6667 - gravity
        try:
            acceleration_sss = (boost_direction - car_velocity.normalized()) * 991.6667 - gravity
        except ZeroDivisionError:
            acceleration_sss = acceleration

        trajectory_time_before_sss = (2200 - car_speed) / acceleration.length()
        trajectory_time_after_sss = 0
        if trajectory_time_before_sss < 0:
            trajectory_time_before_sss = 0
        if trajectory_time < trajectory_time_before_sss:
            trajectory_time_after_sss = trajectory_time - trajectory_time_before_sss
        else:
            trajectory_time_before_sss = trajectory_time

        future_car_velocity = BetterVec3(car_velocity + acceleration * trajectory_time_before_sss
                                         + acceleration_sss * trajectory_time_after_sss
                                         )
        future_car_position = BetterVec3(car_velocity * trajectory_time_before_sss
                                         + 0.5 * acceleration * trajectory_time_before_sss ** 2
                                         + future_car_velocity * trajectory_time_after_sss
                                         + 0.5 * acceleration_sss * trajectory_time_after_sss ** 2
                                         )
        future_target_position = BetterVec3(relative_target + target_velocity * trajectory_time
                                            + 0.5 * -gravity * trajectory_time ** 2)

        ratio_before_sss = (trajectory_time_before_sss / trajectory_time)
        ratio_after_sss = (trajectory_time_after_sss / trajectory_time)
        trajectory_speed = (0.5 * (future_car_velocity.xyz_length + car_speed) * ratio_before_sss
                            + future_car_velocity.xyz_length * ratio_after_sss)
        trajectory_time = future_target_position.xyz_length / trajectory_speed

        z_angle_error = 0
        z_angle_error += calculate_angle_error(future_target_position.z_angle, future_car_position.z_angle)
        z_angle_error += calculate_angle_error(future_target_position.z_angle, future_car_velocity.z_angle)
        if abs(z_angle_error) > abs(last_z_angle_error):
            increment_z_angle *= -0.5
        boost_direction.z_angle += increment_z_angle
        last_z_angle_error = z_angle_error

        xy_angle_error = 0
        xy_angle_error += calculate_angle_error(future_target_position.xy_angle, future_car_position.xy_angle)
        xy_angle_error += calculate_angle_error(future_target_position.xy_angle, future_car_velocity.xy_angle)
        if abs(xy_angle_error) > abs(last_xy_angle_error):
            increment_xy_angle *= -0.5
        boost_direction.xy_angle += increment_xy_angle
        last_xy_angle_error = xy_angle_error

        boost_direction.z = math.sin(boost_direction.z_angle * math.pi / 180)
        boost_direction.xy_length = math.cos(boost_direction.z_angle * math.pi / 180)
        boost_direction.x = math.cos(boost_direction.xy_angle * math.pi / 180) * boost_direction.xy_length
        boost_direction.y = math.sin(boost_direction.xy_angle * math.pi / 180) * boost_direction.xy_length

    return boost_direction * (relative_target.xyz_length * 0.2)


def find_aerial_ball(car_location: Vec3, car_velocity: Vec3, ball_prediction_struct, packet):
    game_time = packet.game_info.seconds_elapsed
    ball_slice = find_slice_at_time(ball_prediction_struct, game_time)
    if ball_slice is None:
        return car_location + car_velocity * 0.5

    target_location = Vec3(ball_slice.physics.location)
    relative_target = target_location - car_location

    car_speed = car_velocity.length() + 1
    trajectory_time = abs(relative_target.length() / car_speed) if car_speed > 200 else 1

    increment_boost = 0.1
    last_boost_error = 1000

    gravity = Vec3(0, 0, 650)

    for i in range(30):
        ball_in_future = find_slice_at_time(ball_prediction_struct, game_time + trajectory_time)
        if ball_in_future is None: break
        future_ball_position = Vec3(ball_in_future.physics.location)
        future_relative_position = future_ball_position - car_location
        needed_car_velocity = future_relative_position / trajectory_time
        needed_car_acceleration = (needed_car_velocity - car_velocity) / trajectory_time
        needed_boost_force = needed_car_acceleration + gravity
        boost_force = needed_boost_force.length()

        if boost_force < 991.667:
            break
        boost_error = 991.667 - boost_force
        if abs(boost_error) > abs(last_boost_error):
            increment_boost *= -0.5
        trajectory_time += increment_boost
        last_boost_error = boost_error

    new_target = find_slice_at_time(ball_prediction_struct, game_time + trajectory_time - 0.05)
    if new_target is None:
        return car_location + car_velocity * 0.5
    return Vec3(new_target.physics.location)


def find_aerial_target(target: Vec3, target_velocity: Vec3, car_location: Vec3, car_velocity: Vec3):
    relative_target = (target - car_location)

    car_speed = car_velocity.length() + 1
    trajectory_time = abs(relative_target.length() / car_speed) if car_speed > 200 else 1

    increment_boost = 0.1
    last_boost_error = 1000

    gravity = Vec3(0, 0, 650)

    if trajectory_time < 0.5:
        return target + target_velocity * trajectory_time + 0.5 * -gravity * trajectory_time ** 2

    for i in range(15):
        future_target_position = (target + target_velocity * trajectory_time
                                  + 0.5 * -gravity * trajectory_time ** 2)
        future_relative_position = future_target_position - car_location
        needed_car_velocity = future_relative_position / trajectory_time
        needed_car_acceleration = (needed_car_velocity - car_velocity) / trajectory_time
        needed_boost_force = needed_car_acceleration + gravity
        boost_force = needed_boost_force.length()

        if boost_force < 991:
            break

        boost_error = 991.667 - boost_force
        if abs(boost_error) > abs(last_boost_error):
            increment_boost *= -0.5
        trajectory_time += increment_boost
        last_boost_error = boost_error

    return target + target_velocity * trajectory_time + 0.5 * -gravity * trajectory_time ** 2


def find_aerial_direction(target: Vec3, car_location: Vec3, car_velocity: Vec3):
    relative_target = BetterVec3(target - car_location)

    car_speed = car_velocity.length() + 1
    trajectory_time = abs(relative_target.xyz_length / car_speed)

    increment_z_angle = 10
    increment_xy_angle = 10
    last_z_angle_error = 1000
    last_xy_angle_error = 1000

    if relative_target.xyz_length < car_speed / 2:
        return car_velocity

    gravity = Vec3(0, 0, 650)
    boost_direction = BetterVec3(relative_target.normalized())

    for i in range(30):
        acceleration = boost_direction * 991.666 - gravity
        future_car_velocity = BetterVec3(car_velocity + acceleration * trajectory_time)
        # future_car_position = BetterVec3(relative_target - car_velocity * trajectory_time
        #                                  - 0.5 * acceleration * trajectory_time ** 2)

        trajectory_speed = 0.5 * (future_car_velocity.xyz_length + car_speed)
        trajectory_time = abs(relative_target.xyz_length / trajectory_speed)

        z_angle_error = 0
        # z_angle_error += calculate_angle_error(relative_target.z_angle, future_car_position.z_angle)
        z_angle_error += calculate_angle_error(relative_target.z_angle, future_car_velocity.z_angle)
        if abs(z_angle_error) > abs(last_z_angle_error):
            increment_z_angle *= -0.5
        boost_direction.z_angle += increment_z_angle
        last_z_angle_error = z_angle_error

        xy_angle_error = 0
        # xy_angle_error += calculate_angle_error(relative_target.xy_angle, future_car_position.xy_angle)
        xy_angle_error += calculate_angle_error(relative_target.xy_angle, future_car_velocity.xy_angle)
        if abs(xy_angle_error) > abs(last_xy_angle_error):
            increment_xy_angle *= -0.5
        boost_direction.xy_angle += increment_xy_angle
        last_xy_angle_error = xy_angle_error

        boost_direction.z = math.sin(boost_direction.z_angle * math.pi / 180)
        boost_direction.xy_length = math.cos(boost_direction.z_angle * math.pi / 180)
        boost_direction.x = math.cos(boost_direction.xy_angle * math.pi / 180) * boost_direction.xy_length
        boost_direction.y = math.sin(boost_direction.xy_angle * math.pi / 180) * boost_direction.xy_length

    return boost_direction * (relative_target.xyz_length * 0.1)


def calculate_vector(vector: Vec3):
    xy_angle = math.atan2(vector.y, vector.x)
    try:
        xy_length = vector.y / math.sin(xy_angle)
    except ZeroDivisionError:
        xy_length = vector.x / math.cos(xy_angle)
    z_angle = math.atan2(vector.z, xy_length)
    try:
        length = vector.z / math.sin(z_angle)
    except ZeroDivisionError:
        length = xy_length / math.cos(z_angle)
    xy_angle *= 180 / math.pi
    z_angle *= 180 / math.pi
    return xy_angle, z_angle, xy_length, length


class BetterVec3(Vec3):
    def __init__(self, vector):
        super().__init__(vector)
        self.xy_angle, self.z_angle, self.xy_length, self.xyz_length \
            = calculate_vector(vector)


def calculate_angle_error(target: float, current: float):
    angle_error = target - current
    if angle_error < -180:
        angle_error += 360
    elif angle_error > 180:
        angle_error -= 360
    return angle_error


def rotate_z_vector(vector: Vec3, degrees: float):
    xy_angle = math.atan2(vector.y, vector.x)
    xy_length = vector.y / math.sin(xy_angle)
    z_angle = math.atan2(vector.z, xy_length)
    length = vector.z / math.sin(z_angle)

    z_angle += degrees * math.pi / 180
    xy_length = math.cos(z_angle) * length
    z = math.sin(z_angle) * length
    x = math.cos(xy_angle) * xy_length
    y = math.sin(xy_angle) * xy_length
    return Vec3(x, y, z)


def rotate_xy_vector(vector: Vec3, degrees):
    angle = math.atan2(vector.y, vector.x)
    xy_length = vector.y / math.sin(angle)
    angle += degrees * math.pi / 180
    x = math.cos(angle) * xy_length
    y = math.sin(angle) * xy_length
    return Vec3(x, y, vector.z)


def divide_vector(a: Vec3, b: Vec3):
    try:
        x = a.x / b.x
        y = a.y / b.y
        z = a.z / b.z
    except ZeroDivisionError:
        x = a.x / (b.x + 1)
        y = a.y / (b.y + 1)
        z = a.z / (b.z + 1)
    return Vec3(x, y, z)


def multiply_vector(a: Vec3, b: Vec3):
    x = a.x * b.x
    y = a.y * b.y
    z = a.z * b.z
    return Vec3(x, y, z)
