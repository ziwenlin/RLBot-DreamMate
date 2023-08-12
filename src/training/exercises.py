import math
import random

from rlbot.utils.game_state_util import CarState, Physics, Vector3, Rotator, BallState, GameState


def aerial_mid_field(index, variation=0):
    y_car = (1 + variation) * -500
    x_car = random.randint(-3, 3) * 100
    car_state = CarState(
        boost_amount=100, physics=Physics(
            location=Vector3(x_car, y_car, 20),
            rotation=Rotator(0, math.pi / 2, 0),
            velocity=Vector3(0, 0, 0),
            angular_velocity=Vector3(0, 0, 0)
        )
    )
    ball_state = BallState(
        Physics(
            location=Vector3(0, 0, 200),
            velocity=Vector3(0, 600, 1500),
            angular_velocity=Vector3(0, 0, 0)
        )
    )
    return GameState(
        ball=ball_state,
        cars={index: car_state},
    )


def aerial_side_field(index, variation=0):
    x_ball = (1 + variation) * -100
    x_car = random.randint(-3, 3) * 100
    car_state = CarState(
        boost_amount=100, physics=Physics(
            location=Vector3(x_car, -3000, 20),
            rotation=Rotator(0, math.pi / 2, 0),
            velocity=Vector3(0, 0, 0),
            angular_velocity=Vector3(0, 0, 0)
        )
    )
    ball_state = BallState(
        Physics(
            location=Vector3(3 * x_ball, 0, 200),
            velocity=Vector3(-x_ball, 300, 1500),
            angular_velocity=Vector3(0, 0, 0)
        )
    )
    return GameState(
        ball=ball_state,
        cars={index: car_state},
    )


def aerial_straight_up(index, variation=0):
    y_car = (1 + variation) * -300
    x_car = random.randint(-3, 3) * 50
    car_state = CarState(
        boost_amount=100, physics=Physics(
            location=Vector3(x_car, y_car, 20),
            rotation=Rotator(0, math.pi / 2, 0),
            velocity=Vector3(0, 0, 0),
            angular_velocity=Vector3(0, 0, 0)
        )
    )
    ball_state = BallState(
        Physics(
            location=Vector3(0, 0, 1500),
            velocity=Vector3(0, 0, 0),
            angular_velocity=Vector3(0, 0, 0)
        )
    )
    return GameState(
        ball=ball_state,
        cars={index: car_state},
    )


def aerial_mid_field_frozen_ball(index, variation=0):
    y_car = (1 + variation) * -1000
    x_car = random.randint(-3, 3) * 500
    car_state = CarState(
        boost_amount=100, physics=Physics(
            location=Vector3(x_car, y_car, 20),
            rotation=Rotator(0, math.pi / 2, 0),
            velocity=Vector3(0, 0, 0),
            angular_velocity=Vector3(0, 0, 0)
        )
    )
    ball_state = BallState(
        Physics(
            location=Vector3(0, 0, 1500),
            velocity=Vector3(0, 0, 0),
            angular_velocity=Vector3(0, 0, 0)
        )
    )
    return GameState(
        ball=ball_state,
        cars={index: car_state},
    )
