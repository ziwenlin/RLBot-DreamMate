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
        side_of_approach_direction =  sign(
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


