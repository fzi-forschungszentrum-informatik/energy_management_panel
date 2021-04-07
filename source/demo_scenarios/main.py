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
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException

from scenarios.apartment.apartment import Apartment, ApartmentNoOpt
from scenarios.apartment.apartment import dt_to_ts
from timestamp import datetime_from_timestamp, timestamp_utc_now

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
    -----------
    active_scenario_classes : list of classes.
        A list of all scenarios we consider active, i.e. which will be
        automatically, and the data is pushed to the EMP.
    active_scenario_classes : dict of classes.
        A list of all scenarios which we we can use passively. E.g.
        which can be used for representing optimization algorithms that
        support hindcasting or forecasting datapoints. However, these
        operations must be called exlicitly.
    emp_baseurl : string
        Protocol, hostname and port of the EMP instance. E.g:
        http://localhost:8000
    simulation_timedelta : datetime.timedelta.
        The simulation timestep. Check how these affect the scenario
        code before changing this from 60 seconds.
    start_time : datatime.datetime
        The time (reasonably in the past) when we start to run simulating
        the active scenarios.
    """
    active_scenario_classes = [
        Apartment,
    ]

    passive_scenario_classes = {
        "apt": Apartment,
        "apt-no": ApartmentNoOpt,
    }

    emp_baseurl = "http://localhost:8000"

    simulation_timedelta = timedelta(seconds=60)

    start_time = (datetime.utcnow() - timedelta(days=1)).replace(
        hour=8, minute=50
    )

    run_passive_cache = {k: {} for k in passive_scenario_classes}
    run_passive_tasks = []

    def __init__(self):
        logger.info("Starting Scenario Runner")

        self.scenarios = []
        scenario_classes = set(self.active_scenario_classes)
        # Also create datapoints for passive scenarios.
        scenario_classes.update(self.passive_scenario_classes.values())
        for scenario_class in scenario_classes:
            scenario = scenario_class()
            logger.info("Initiated Scenario: %s", scenario.name)
            if scenario_class in self.active_scenario_classes:
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
                response = requests.post(dp_url, json=datapoint)
                # We also keep a mapping from the origin_id we use here
                # to the datapoint id used by the EMP. It looks e.g. like this
                # {'apartment_total_electric_power': 8, ... }
                emp_id = response.json()["id"]
                self.datapoint_id_mapping[datapoint["origin_id"]] = emp_id

    async def run_active(self):
        """
        Simulate operation of active scenarios.
        """
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
                # This is nice for checking the values computed above.
                logger.debug(
                    "Simulated: %s\n\n"
                    "Schedules:\n%s\n\n"
                    "Setpoints:\n%s\n\n"
                    "Values:\n%s",
                    *(
                        scenario.name,
                        json.dumps(schedules, indent=4),
                        json.dumps(setpoints, indent=4),
                        json.dumps(values, indent=4)
                    )
                )

                # Push all the computed stuff to the EMP.
                url_root = self.emp_baseurl + "/api/datapoint/"
                for origin_id in setpoints:
                    dp_id = self.datapoint_id_mapping[origin_id]
                    url = url_root + "%s/setpoint/" % dp_id
                    data = setpoints[origin_id]
                    response = requests.post(url, json=data)
                    if response.status_code != 201:
                        logger.warning(
                            "Error posting to EMP with status code: %s. \n\n"
                            "URL was:\n%s\n\n"
                            "Returned message was:\n%s\n\n"
                            "Data was:\n%s",
                            *(
                                response.status_code,
                                url,
                                json.dumps(response.json(), indent=4),
                                json.dumps(data, indent=4),
                            )
                        )
                for origin_id in schedules:
                    dp_id = self.datapoint_id_mapping[origin_id]
                    url = url_root + "%s/schedule/" % dp_id
                    data = schedules[origin_id]
                    response = requests.post(url, json=data)
                    if response.status_code != 201:
                          logger.warning(
                              "Error posting to EMP with status code: %s. \n\n"
                              "URL was:\n%s\n\n"
                              "Returned message was:\n%s\n\n"
                              "Data was:\n%s",
                              *(
                                  response.status_code,
                                  url,
                                  json.dumps(response.json(), indent=4),
                                  json.dumps(data, indent=4),
                              )
                          )
                for origin_id in values:
                    dp_id = self.datapoint_id_mapping[origin_id]
                    url = url_root + "%s/value/" % dp_id
                    data = values[origin_id]
                    response = requests.post(url, json=data)
                    if response.status_code != 201:
                          logger.warning(
                              "Error posting to EMP with status code: %s. \n\n"
                              "URL was:\n%s\n\n"
                              "Returned message was:\n%s\n\n"
                              "Data was:\n%s",
                              *(
                                  response.status_code,
                                  url,
                                  json.dumps(response.json(), indent=4),
                                  json.dumps(data, indent=4),
                              )
                          )

            simulation_dt += self.simulation_timedelta
            if simulation_dt > datetime.utcnow():
                # Wait until reality has reached our next simulation
                # timestamp.
                sleep_s = (simulation_dt - datetime.utcnow()).total_seconds()
                await asyncio.sleep(sleep_s)
            else:
                # Give the asyncio thread some time to do other stuff.
                await asyncio.sleep(0.01)

    async def run_passive(self, scenario_name, start_dt, end_dt):
        """
        Simulate that an optimizer would be querried for a hind- or forecast.

        Parameters
        ----------
        scenario_name: string
            The scenario to run. Must be one of the keys of
            self.passive_scenario_classes.
        start_dt : datetime.datetime.
            The first datetime that is included in the simulation.
        end_dt : TYPE
            The datetime after which this function returns once the
            simulation times reaches or exceeds this value.

        Returns
        -------
        all_values, all_setpoints, all_schedules : lists
            A list of all objects computed during the simulation time.
            Sorted by datapoint.

        """
        logger.info(
            "Triggering passive run for scenario %s between %s and %s.",
            *(scenario_name, start_dt, end_dt)
        )

        scenario = self.passive_scenario_classes[scenario_name]()

        all_values = {dp["origin_id"]: [] for dp in scenario.datapoints}
        all_setpoints = {dp["origin_id"]: [] for dp in scenario.datapoints}
        all_schedules = {dp["origin_id"]: [] for dp in scenario.datapoints}


        simulation_dt = start_dt.replace(second=0, microsecond=0)
        while simulation_dt <= end_dt:
            # Compute the value, schedule nad setpoint messages that
            # belong to this simulation_dt.
            values, schedules, setpoints = scenario.simulate_timestep(
               simulation_dt=simulation_dt
            )
            # This is nice for checking the values computed above.
            logger.debug(
                "Simulated: %s\n\n"
                "Schedules:\n%s\n\n"
                "Setpoints:\n%s\n\n"
                "Values:\n%s",
                *(
                    scenario.name,
                    json.dumps(schedules, indent=4),
                    json.dumps(setpoints, indent=4),
                    json.dumps(values, indent=4)
                )
            )
            # TODO: Write to cache here instead of returning values.
            cache_content = {
                "values": values,
                "schedules": schedules,
                "setpoints": setpoints,
            }
            self.run_passive_cache[scenario_name][simulation_dt] = cache_content
            simulation_dt += self.simulation_timedelta

            # Give the thread some time to do other stuff.
            await asyncio.sleep(0.001)

        logger.info(
            "Finished passive run for scenario %s between %s and %s.",
            *(scenario_name, start_dt, end_dt)
        )

scenario_runner = ScenarioRunner()
app = FastAPI()

@app.on_event("startup")
async def run_scenarios_in_bg():
    asyncio.create_task(scenario_runner.run_active())

def validate_and_parse_ts(from_ts, to_ts):
    now = timestamp_utc_now()
    if from_ts >= to_ts:
        raise HTTPException(
            status_code=400,
            detail=(
                "from_must be smaller then to_ts."
            )
        )
    for timestamp in [from_ts, to_ts]:
        if timestamp is None:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Timestamps must be provided."
                )
            )
        if timestamp > now + 1e11:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Timestamp (%s) seems unreasonably high. Check if it is "
                    "in milliseconds and contact your adminstrator if this is the "
                    "case." %
                    str(timestamp)
                )
            )

        if timestamp < now - 1e11:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Timestamp (%s) seems unreasonably low. Check if it is "
                    "in milliseconds and contact your adminstrator if this is the "
                    "case." %
                    str(timestamp)
                )
            )
    from_dt = datetime_from_timestamp(from_ts)
    to_dt = datetime_from_timestamp(to_ts)
    return from_dt, to_dt

@app.get("/{scenario_name}/simulation/status/")
async def status(scenario_name, from_ts: int = None, to_ts: int = None):

    # Evaluate parameters.
    if scenario_name not in scenario_runner.passive_scenario_classes:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unknown scenario: %s." % scenario_name
            )
        )
    from_dt, to_dt = validate_and_parse_ts(from_ts, to_ts)

    requested_dts = set()
    from_dt = from_dt.replace(second=0, microsecond=0)
    simulation_dt = from_dt
    while simulation_dt <= to_dt:
        requested_dts.add(simulation_dt)
        simulation_dt += scenario_runner.simulation_timedelta
    existing_dts = set(scenario_runner.run_passive_cache[scenario_name].keys())

    existing_dts = set(scenario_runner.run_passive_cache[scenario_name].keys())
    already_computed = existing_dts.intersection(requested_dts)
    percent_complete = round(100 * len(already_computed)/len(requested_dts), 1)
    eta_seconds = round(((len(requested_dts)-len(already_computed)) * 0.002), 1)

    logger.info(
        "Status requested for scenario {} data between {} and {}, "
        "is {:.1f}% with ETA {}s".format(
            scenario_name,
            from_dt,
            to_dt,
            percent_complete,
            eta_seconds
        )
    )

    return {
        "percent complete": percent_complete,
        "ETA seconds": eta_seconds,
    }

@app.get("/{scenario_name}/simulation/result/")
async def result(scenario_name, from_ts: int = None, to_ts: int = None):

    # Evaluate parameters.
    if scenario_name not in scenario_runner.passive_scenario_classes:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unknown scenario: %s." % scenario_name
            )
        )
    from_dt, to_dt = validate_and_parse_ts(from_ts, to_ts)

    requested_dts = set()
    from_dt = from_dt.replace(second=0, microsecond=0)
    simulation_dt = from_dt
    while simulation_dt <= to_dt:
        requested_dts.add(simulation_dt)
        simulation_dt += scenario_runner.simulation_timedelta
    existing_dts = set(scenario_runner.run_passive_cache[scenario_name].keys())

    # Check that computation of all requested dts is completed.
    if requested_dts.difference(existing_dts):
        raise HTTPException(
            status_code=400,
            detail=(
                "Simulation has not completed for the requested period. "
                "use /simulation/status/ to verify that the request is "
                "complete before attempting to fetch results."
            )
        )

    # Build the return message.
    msg_types = ["values", "schedules", "setpoints"]
    response = {k: {} for k in msg_types}
    scenario_data = scenario_runner.run_passive_cache[scenario_name]
    for requested_dt in sorted(requested_dts):
        for msg_type in msg_types:
            # This is the payload dict, with datapoint_ids as keys of
            # the computed data.
            data = scenario_data[requested_dt][msg_type]

            for dp_id in data.keys():
                dp_values = response[msg_type].setdefault(dp_id, list())
                dp_values.append(data[dp_id])
    return response


@app.post("/simulation/request/")
async def request(scenario_name, from_ts: int = None, to_ts: int = None):
    """
    Start simulation in background and return the appropriate timestamps
    the client needs to request status and fetch results.
    """

    # Evaluate parameters.
    if scenario_name not in scenario_runner.passive_scenario_classes:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unknown scenario: %s." % scenario_name
            )
        )
    from_dt, to_dt = validate_and_parse_ts(from_ts, to_ts)

    requested_dts = set()
    from_dt = from_dt.replace(second=0, microsecond=0)
    simulation_dt = from_dt
    while simulation_dt <= to_dt:
        requested_dts.add(simulation_dt)
        simulation_dt += scenario_runner.simulation_timedelta
    existing_dts = set(scenario_runner.run_passive_cache[scenario_name].keys())
    to_dt_simulated = max(requested_dts)

    coro = asyncio.create_task(
        scenario_runner.run_passive(
            scenario_name,
            from_dt,
            to_dt_simulated,
        )
    )

    return {
        "from_ts": dt_to_ts(from_dt),
        "to_ts": dt_to_ts(to_dt_simulated),
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8018)
