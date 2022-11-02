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
    mid_p = Vec3(5120, 4096, 2044)
    mid_n = Vec3(-5120, -4096, 0)
    # mid = check_valid_location(location, mid_p, mid_n)

    # Check goals
    # goal_p = Vec3(893, 6000, 642)
    # goal_n = Vec3(-893, -6000, 0)
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

