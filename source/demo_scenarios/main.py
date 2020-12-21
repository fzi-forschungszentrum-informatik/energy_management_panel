"""
This is the workhorse of the scenario demos.
"""
import json
import asyncio
import logging
import requests
from time import monotonic
from datetime import datetime, timedelta

import uvicorn
from fastapi import FastAPI

from scenarios.apartment.apartment import Apartment

# Setup a logger for the scenario runner to use.
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
formatter.datefmt = "%H:%M:%S"
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class ScenarioRunner():
    """
    This executes the scenario simulation.

    It will start with a simulated wall clock time of start_time and
    trys to catchup with presence as fast as possible. This way we can
    generate some fake history that might look good on UIs. Once presence
    is reached the runner will couple simulation time to real time.

    Attributes:

    """
    scenario_classes = [
        Apartment,
    ]

    emp_baseurl = "http://localhost:8000"

    simulation_timedelta = timedelta(seconds=60)
    start_time = datetime.utcnow() - timedelta(seconds=300)

    def __init__(self):
        logger.info("Starting Scenario Runner")

        self.scenarios = []
        for scenario_class in self.scenario_classes:
            scenario = scenario_class()
            logger.info("Initiated Scenario: %s", scenario.name)
            self.scenarios.append(scenario)

            # We exepect that the each scenario returns a python
            # dict that matches the convention epxected by the EMPs
            # POST /api/datapoint endpoint.
            logger.info(
                "Pushing datapoints to EMP for scenario: %s", scenario.name
            )
            dp_url = self.emp_baseurl + "/api/datapoint/"
            self.datapoint_id_mapping = {}
            for datapoint in scenario.datapoints:
                response = requests.post(dp_url, data=datapoint)
                # We also keep a mapping from the origin_id we use here
                # to the datapoint id used by the EMP. It looks e.g. like this
                # {'apartment_total_electric_power': 8, ... }
                emp_id = response.json()["id"]
                self.datapoint_id_mapping[datapoint["origin_id"]] = emp_id

    async def run(self):
        simulation_dt = self.start_time.replace(second=0, microsecond=0)
        while True:
            logger.info("Processing simulation_dt: %s", simulation_dt)
            # For every scenario we simulate ...
            for scenario in self.scenarios:
                # Compute the value, schedule nad setpoint messages that
                # belong to this simulation_dt.
                values, schedules, setpoints = scenario.simulate_timestep(
                   simulation_dt=simulation_dt
                )
                # TODO Push to EMP
                # TODO Check values

            simulation_dt += self.simulation_timedelta
            if simulation_dt > datetime.utcnow():
                # Wait until reality has reached our next simulation
                # timestamp.
                sleep_s = (simulation_dt - datetime.utcnow()).total_seconds()
                await asyncio.sleep(sleep_s)
            else:
                # Give the asyncio thread some time to do other stuff.
                await asyncio.sleep(0.1)


scenario_runner = ScenarioRunner()
app = FastAPI()

@app.on_event("startup")
async def run_scenarios_in_bg():
    asyncio.create_task(scenario_runner.run())


@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8018)