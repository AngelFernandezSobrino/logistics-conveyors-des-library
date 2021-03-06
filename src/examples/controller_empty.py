from simulator import BehaviourController
from simulator.objects import Tray


def input_tray(args):
    args['simulation_data']['0'].input(Tray(23, 2))


class BehaviourControllerEmpty(BehaviourController):
    def __init__(self, system_description: dict):
        super().__init__(system_description)

        self.external = {
            0: input_tray
        }
