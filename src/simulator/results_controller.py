from __future__ import annotations

from typing import TYPE_CHECKING
from copy import deepcopy

from simulator.objects import Product, Stopper

if TYPE_CHECKING:
    import simulator.objects.system


class ResultsController:
    def __init__(self, system_description: simulator.objects.system.SystemDescription):
        self.production = {}
        self.times = {}
        self.previous_stoppers = {}
        self.system_description = system_description

        for stopper_id, stopper_description in system_description.items():
            self.times[stopper_id] = {'rest': 0, 'request': 0, 'move': {}}
            self.times[stopper_id]['move'] = {v: 0 for v in stopper_description['destiny']}
            self.previous_stoppers[stopper_id] = {}
            self.previous_stoppers[stopper_id]['state'] = {
                'rest': False,
                'request': False,
                'move': {v: False for v in stopper_description['destiny']}}
            self.previous_stoppers[stopper_id]['time'] = 0

    def produce(self, product: Product):
        self.production[product.model] += 1

    def update_times(self, stopper: Stopper, actual_time: int):
        if self.previous_stoppers[stopper.stopper_id]['state']['rest']:
            self.times[stopper.stopper_id]['rest'] += actual_time - self.previous_stoppers[stopper.stopper_id]['time']

        if self.previous_stoppers[stopper.stopper_id]['state']['request']:
            self.times[stopper.stopper_id]['request'] += actual_time - \
                                                         self.previous_stoppers[stopper.stopper_id]['time']

        for destiny in stopper.output_ids:
            if self.previous_stoppers[stopper.stopper_id]['state']['move'][destiny]:
                self.times[stopper.stopper_id]['move'][destiny] += \
                    actual_time - self.previous_stoppers[stopper.stopper_id]['time']

        self.previous_stoppers[stopper.stopper_id]['state']['rest'] = deepcopy(stopper.rest)
        self.previous_stoppers[stopper.stopper_id]['state']['request'] = deepcopy(stopper.request)
        self.previous_stoppers[stopper.stopper_id]['state']['move'] = deepcopy(stopper.move)
        self.previous_stoppers[stopper.stopper_id]['time'] = actual_time

    def update_all_times(self, simulation, actual_time: int):
        for stopper_id in self.system_description.keys():
            self.update_times(simulation[stopper_id], actual_time)
