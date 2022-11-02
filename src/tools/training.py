import math

from rlbot.utils.game_state_util import CarState, Physics, Vector3, Rotator, BallState, GameState


def aerial_mid_field(index):
    car_state = CarState(
        boost_amount=100, physics=Physics(
            location=Vector3(0, -2000, 20),
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
    game_state = GameState(ball=ball_state, cars={index: car_state})
    return game_state
