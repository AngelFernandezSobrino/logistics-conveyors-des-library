from __future__ import annotations
from typing import TYPE_CHECKING
import os

from desim.events_manager import CustomEventListener

from sim.item import Product
import sim.settings as settings

import sim.data_storage as data_storage

import desim.core

if TYPE_CHECKING:
    import desim.config_parser

import sim.controller as custom_behaviour


def get_simulator_config():

    config_path = os.path.dirname(os.path.abspath(__file__)) + "/config.xlsx"
    config_parser = desim.config_parser.ConfigParser(config_path)
    config_parser.parse("config_parser")

    return config_parser


def create_simulator(
    config_parser: desim.config_parser.ConfigParser, max_containers verbose: bool = False
):

    sim_core = desim.core.Simulation[Product](config_parser.config, debug=verbose)

    behavior = custom_behaviour.SimulationController(
        sim_core, settings.MAX_CONTAINERS_AMMOUNT
    )

    sim_core.register_external_events(
        behavior.external_functions,
        # step_callback,
    )

    for data_storage_step in range(0, settings.STEPS, 100):
        sim_core.timed_events_manager.add(
            CustomEventListener(
                data_storage.save_actual_results, (), {"controller": behavior}
            ),
            data_storage_step,
        )

    return sim_core, behavior
