from __future__ import annotations

import wandb

from typing import TYPE_CHECKING, TypeVar

from sim.item import ProductTypeReferences

if TYPE_CHECKING:
    import desim.core
    import sim.results_controller
    from desim.core import Simulation

step_to_time = 0.1
wandb_data_dict: dict = {}


wandb.init(project="i4techlab-simulation", entity="soobbz")
config = wandb.config
wandb.define_metric("results/simulation_time")
wandb.define_metric("results/*", step_metric="results/simulation_time")


def step_callback(core: desim.core.Simulation):
    if wandb_data_dict != {}:
        wandb_data_dict["results/simulation_time"] = (
            core.timed_events_manager.step * step_to_time / 60
        )
        wandb.log(wandb_data_dict)
        wandb_data_dict.clear()


def production_update_callback(
    controller: sim.results_controller.CountersController,
    index: ProductTypeReferences,
    time: int,
) -> None:
    wandb_data_dict[f"results/production/{index.name}"] = controller.counters[index]


def time_update_callback(results: sim.results_controller.CronoController, step: int):
    wandb_data_dict["results/times"] = {
        key: results.stoppersResults[key] for key in ["DIR04", "PT05", "PT06"]
    }


def busyness_update_callback(controller, busyness, step: int):
    wandb_data_dict["results/busyness"] = busyness
