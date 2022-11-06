import math

from rlbot.agents.base_agent import SimpleControllerState

from util.ball_prediction_analysis import find_slice_at_time
from util.boost_pad_tracker import BoostPadTracker
from util.drive import limit_to_safe_range
from util.vec import Vec3


def find_shot(target_a, target_b, ball_location, car_location):
    try:
        car_to_ball = ball_location - car_location
        car_to_ball_direction = car_to_ball.normalized()
    except:
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
    except:
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
        self.state = False
        self.timer = 0

    def toggle(self):
        self.state = not self.state
        return self.state

    def toggle_hold(self, delay=1):
        if self.timer < delay:
            self.timer += 1
        else:
            self.timer = 0
            self.state = not self.state
        return self.state


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


def find_aerial_direction(target: Vec3, car_location: Vec3, car_velocity: Vec3):
    relative_target = target - car_location
    relative_xy_angle, relative_z_angle, relative_xy_distance, relative_distance = calculate_vector(relative_target)

    trajectory_speed = car_velocity.length() + 1
    trajectory_time = abs(relative_distance / trajectory_speed) * 0.5

    increment_z_angle = 10
    increment_xy_angle = 10
    last_z_angle_error = 1000
    last_xy_angle_error = 1000

    gravity = Vec3(0, 0, -650)
    boost_direction = relative_target.normalized()
    boost_xy_angle, boost_z_angle, boost_xy_length, boost_distance = calculate_vector(boost_direction)

    for i in range(12):
        acceleration_vector: Vec3 = boost_direction * 991.666
        acceleration_vector += gravity

        velocity_vector = car_velocity + acceleration_vector * trajectory_time
        velocity_xy_angle, velocity_z_angle, velocity_xy_distance, velocity_speed = calculate_vector(velocity_vector)

        # position_vector = relative_target - car_velocity * trajectory_time \
        #                   - 0.5 * acceleration_vector * trajectory_time ** 2
        position_vector = relative_target - velocity_vector * trajectory_time
        position_xy_angle, position_z_angle, position_xy_distance, position_distance = calculate_vector(position_vector)

        trajectory_time = abs(relative_distance / velocity_speed) * 0.5

        z_angle_error = calculate_angle_error(relative_z_angle, velocity_z_angle)
        if abs(z_angle_error) > abs(last_z_angle_error):
            increment_z_angle *= -0.5
        boost_z_angle += increment_z_angle
        last_z_angle_error = z_angle_error

        xy_angle_error = calculate_angle_error(relative_xy_angle, velocity_xy_angle)
        if abs(xy_angle_error) > abs(last_xy_angle_error):
            increment_xy_angle *= -0.5
        boost_xy_angle += increment_xy_angle
        last_xy_angle_error = xy_angle_error

        boost_direction.z = math.sin(boost_z_angle * math.pi / 180)
        boost_xy_length = math.cos(boost_z_angle * math.pi / 180)
        boost_direction.x = math.cos(boost_xy_angle * math.pi / 180) * boost_xy_length
        boost_direction.y = math.sin(boost_xy_angle * math.pi / 180) * boost_xy_length

    return boost_direction * (relative_distance * 0.1)


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
