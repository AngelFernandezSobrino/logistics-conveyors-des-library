from __future__ import annotations

from typing import TypedDict, TYPE_CHECKING


from simulator.helpers.timed_events_manager import TimedEventsManager
from .tray import Tray

if TYPE_CHECKING:
    from simulator.behaviour_controller import ControllerBase
    import simulator.objects.system


class StopperInfo(TypedDict):
    destiny: list[str]
    steps: list[int]
    move_behaviour: list[str]
    rest_steps: list[int]
    default_locked: bool


class Stopper:

    def __init__(self, external_stopper_id: str, simulation_description: simulator.objects.system.SystemDescription, simulation: dict, events_register: TimedEventsManager, behaviour_controller, results_controller, debug):
        self.debug = debug

        self.request_time = 0

        self.behaviour_controller = behaviour_controller
        self.results_controller = results_controller
        self.stopper_id = external_stopper_id
        self.simulation = simulation
        self.description = simulation_description[external_stopper_id]

        self.output_ids = simulation_description[external_stopper_id]['destiny']

        self.steps = {
            self.output_ids[k]: v
            for k, v in enumerate(self.description['steps'])
        }
        self.rest_steps = {
            self.output_ids[k]: v
            for k, v in enumerate(self.description['rest_steps'])
        }
        self.move_behaviour = {
            self.output_ids[k]: v
            for k, v in enumerate(self.description['move_behaviour'])
        }

        self.default_locked = self.description['default_locked']

        self.events_register = events_register

        self.rest = True
        self.request = False
        self.move = {v: False for v in self.description['destiny']}
        self.stop = {v: True if self.description['default_locked'] else False for v in self.description['destiny']}

        self.output_trays = {v: False for v in self.description['destiny']}

        self.input_tray = False
        self.input_ids = []

        for external_stopper_id, stopper_info in simulation_description.items():
            if self.stopper_id in stopper_info['destiny']:
                self.input_ids += [external_stopper_id]

    def check_request(self):
        self.behaviour_controller.check_request(self.stopper_id, self.simulation)
        if not self.request:
            return
        for destiny in self.output_ids:
            if self.simulation[destiny].check_availability() and not self.move[destiny] and not self.stop[destiny]:
                self.start_move(destiny)
                return
        self.events_register.push(self.check_request, {}, 1)

    def input(self, tray: Tray):
        self.input_tray = tray
        self.rest = False
        self.request = True
        self.request_time = self.events_register.step
        self.results_controller.update_times(self, self.events_register.step)
        self.check_request()

    def start_move(self, destiny):
        self.request = False
        self.move[destiny] = True
        self.output_trays[destiny] = self.input_tray
        self.input_tray = False
        self.results_controller.update_times(self, self.events_register.step)
        self.events_register.push(self.end_move, {'destiny': destiny}, self.steps[destiny])
        if self.default_locked:
            self.lock(destiny)
        if self.move_behaviour == 'fast':
            self.events_register.push(self.return_rest, {}, self.rest_steps[destiny])

    def return_rest(self):
        self.rest = True
        self.results_controller.update_times(self, self.events_register.step)
        self.propagate_backwards()

    def propagate_backwards(self):
        for origin in self.input_ids:
            self.simulation[origin].check_request()

    def check_availability(self):
        for origin in self.input_ids:
            if self.simulation[origin].get_move_to(self.stopper_id):
                return False
        if not self.rest:
            return False
        return True

    def get_move_to(self, destiny):
        return self.move[destiny]

    def end_move(self, args):
        self.move[args['destiny']] = False
        self.simulation[args['destiny']].input(self.output_trays[args['destiny']])
        self.output_trays[args['destiny']] = False
        if self.move_behaviour != 'fast':
            self.return_rest()
        self.results_controller.update_times(self, self.events_register.step)

    def lock(self, output_id):
        self.stop[output_id] = True
        self.check_request()

    def unlock(self, output_id):
        self.stop[output_id] = False
        self.check_request()


if __name__ == '__main__':

    events_manager = TimedEventsManager()

    simulation_data_example = {}

    controller = ControllerBase()

    from src.simulator.helpers.test_utils import system_description_example

    for stopper_id, stopper_description in system_description_example.items():
        simulation_data_example[stopper_id] = Stopper(stopper_id, system_description_example, simulation_data_example, events_manager, controller, False)
        print(stopper_id)
        print(simulation_data_example[stopper_id])

    simulation_data_example['0'].input(Tray(23, 2))

    for i in range(0, 20000):
        print(i)
        events_manager.run()