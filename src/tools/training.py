import math
import random

from rlbot.utils.game_state_util import CarState, Physics, Vector3, Rotator, BallState, GameState, GameInfoState


def aerial_mid_field(index):
    y = random.randint(1, 5) * 1000
    car_state = CarState(
        boost_amount=100, physics=Physics(
            location=Vector3(0, -y, 20),
            rotation=Rotator(0, math.pi / 2, 0),
            velocity=Vector3(0, 0, 0),
            angular_velocity=Vector3(0, 0, 0)
        )
    )
    ball_state = BallState(
        Physics(
            location=Vector3(0, 0, 200),
            velocity=Vector3(0, 0, 1500),
            angular_velocity=Vector3(0, 0, 0)
        )
    )
    game_info = GameInfoState(
        game_speed=0.8
    )
    return GameState(
        ball=ball_state,
        cars={index: car_state},
        game_info=game_info
    )


def aerial_mid_field_frozen_ball(index):
    y = random.randint(1, 5) * 1000
    car_state = CarState(
        boost_amount=100, physics=Physics(
            location=Vector3(0, -y, 20),
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
    game_info = GameInfoState(
        game_speed=0.8
    )
    return GameState(
        ball=ball_state,
        cars={index: car_state},
        game_info=game_info
    )


def need_boost(index):
    return GameState(
        cars={index: CarState(
            boost_amount=100
        )}
    )
