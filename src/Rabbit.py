from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket


class TutorialRabbit(BaseAgent):
    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:


        self.renderer.begin_rendering()
        self.renderer.draw_string_3d((0, 0, 0), 2, 2, "Hello RLBot!", self.renderer.black())
        self.renderer.end_rendering()

        return SimpleControllerState()
