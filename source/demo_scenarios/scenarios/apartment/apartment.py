"""
"""
import json
import pickle
import pathlib


def dt_to_ts(dt):
    """
    Convert datetime object to timestamp in milliseconds since epoch.
    """
    return round(dt.timestamp() * 1000)



class Apartment():
    """
    Simulates the operation of an apartment with a handful of smart devices.

    Attributes:
    -----------
    name : string
        A friendly name of the class for logs and so on.
    """

    name = "Apartment"

    def __init__(self):
        # Load the datapoint json defintion.
        self.datapoints = self._load_datapoints()

        # Also load the power profile per operation minute for all
        # three devices.
        self.power_profiles = self._load_power_profiles()

    def _load_power_profiles(self):
        pp_pickle_path = (
            pathlib.Path(__file__).parent / "appliances_profiles.pickle"
        )

        with open(pp_pickle_path, "rb") as f:
            power_profiles = pickle.load(f)
        return power_profiles

    def _load_datapoints(self):
        dp_json_path = pathlib.Path(__file__).parent / "datapoints.json"

        with open(dp_json_path, "r") as f:
            datapoints = json.load(f)
        return datapoints

    def compute_setpoints(self, simulation_dt):
        """
        Compute the setpoints for the three flexibile devices.

        Assume that the device should run while the familiy is out
        for work, leaving at 9:00. The dishwasher can operate between
        9:00 and 17:00 as the plates and stuff are required for dinner.
        The washing machine should be finsihed at 19:00 at the latest
        and the dryer can operate between 17:00 and 20:00, as no one is
        home to load the laundry into dryer before 17:00, and the residents
        would like to start watching TV at 20:00.

        Parameters
        ----------
        simulation_dt : datetime object.
            The current time of the simulation.

        Returns:
        --------
        setpoints : dict.
            Datapoint setpoints emited at the current simulation time, or
            Empty if if no data would have been emitted. This is at most
            one setpoint msg per datapoint and simulation_dt. Format is:
                {<origin_id_of_datapoint>: <value msg>}
        """
        sdt_full_hour = simulation_dt.replace(
            minute=0,
            second=0,
            microsecond=0,
        )

        setpoints = {}
        setpoints["apartment_dishwasher_active"] = {
            "timestamp": dt_to_ts(simulation_dt),
            "setpoint": [
                {
                    "from_timestamp": dt_to_ts(sdt_full_hour.replace(hour=9)),
                    "to_timestamp": dt_to_ts(sdt_full_hour.replace(hour=17)),
                    "preferred_value": "1",
                    "acceptable_values": [
                        "0",
                        "1",
                    ],
                },
                {
                    "from_timestamp": dt_to_ts(sdt_full_hour.replace(hour=17)),
                    "to_timestamp": None,
                    "preferred_value": "0",
                    "acceptable_values": [
                        "0",
                    ],
                },
            ],
        }
        setpoints["apartment_washing_machine_active"] = {
            "timestamp": dt_to_ts(simulation_dt),
            "setpoint": [
                {
                    "from_timestamp": dt_to_ts(sdt_full_hour.replace(hour=9)),
                    "to_timestamp": dt_to_ts(sdt_full_hour.replace(hour=19)),
                    "preferred_value": "1",
                    "acceptable_values": [
                        "0",
                        "1",
                    ],
                },
                {
                    "from_timestamp": dt_to_ts(sdt_full_hour.replace(hour=19)),
                    "to_timestamp": None,
                    "preferred_value": "0",
                    "acceptable_values": [
                        "0",
                    ],
                },
            ],
        }
        setpoints["apartment_dryer_active"] = {
            "timestamp": dt_to_ts(simulation_dt),
            "setpoint": [
                {
                    "from_timestamp": dt_to_ts(sdt_full_hour.replace(hour=17)),
                    "to_timestamp": dt_to_ts(sdt_full_hour.replace(hour=20)),
                    "preferred_value": "1",
                    "acceptable_values": [
                        "0",
                        "1",
                    ],
                },
                {
                    "from_timestamp": dt_to_ts(sdt_full_hour.replace(hour=20)),
                    "to_timestamp": None,
                    "preferred_value": "0",
                    "acceptable_values": [
                        "0",
                    ],
                },
            ],
        }

        return setpoints

    def compute_schedules(self, simulation_dt):
        """
        Compute the schedule for the three flexibile devices.

        This would in practice need a price forcast for the current
        day to optimize the operation times. Here we assume for simplicity
        that the lowest energy prices during the day are between 11:00 and
        14:00 and that the prices between 19:00 and 20:00 are cheaper then
        between 17:00 and 19:00. Once we enter one of those low price
        valleys we start the devices immediately.

        Parameters
        ----------
        simulation_dt : datetime object.
            The current time of the simulation.

        Returns:
        --------
        schedules : dict.
            Datapoint schedules emited at the current simulation time, or
            Empty if if no data would have been emitted. This is at most
            one schedule msg per datapoint and simulation_dt. Format is:
                {<origin_id_of_datapoint>: <value msg>}
        """
        sdt_full_hour = simulation_dt.replace(
            minute=0,
            second=0,
            microsecond=0,
        )

        schedules = {}
        schedules["apartment_dishwasher_active"] = {
            "timestamp": dt_to_ts(simulation_dt),
            "schedule": [
                {
                    "from_timestamp": None,
                    "to_timestamp": dt_to_ts(sdt_full_hour.replace(hour=11)),
                    "value": "0",
                },
                {
                    "from_timestamp": dt_to_ts(sdt_full_hour.replace(hour=11)),
                    "to_timestamp": dt_to_ts(sdt_full_hour.replace(hour=14)),
                    "value": "1",
                },
                {
                    "from_timestamp": dt_to_ts(sdt_full_hour.replace(hour=14)),
                    "to_timestamp": None,
                    "value": "0",
                },
            ],
        }
        schedules["apartment_washing_machine_active"] = {
            "timestamp": dt_to_ts(simulation_dt),
            "schedule": [
                {
                    "from_timestamp": None,
                    "to_timestamp": dt_to_ts(sdt_full_hour.replace(hour=11)),
                    "value": "0",
                },
                {
                    "from_timestamp": dt_to_ts(sdt_full_hour.replace(hour=11)),
                    "to_timestamp": dt_to_ts(sdt_full_hour.replace(hour=13)),
                    "value": "1",
                },
                {
                    "from_timestamp": dt_to_ts(sdt_full_hour.replace(hour=13)),
                    "to_timestamp": None,
                    "value": "0",
                },
            ],
        }
        schedules["apartment_dryer_active"] = {
            "timestamp": dt_to_ts(simulation_dt),
            "schedule": [
                {
                    "from_timestamp": None,
                    "to_timestamp": dt_to_ts(sdt_full_hour.replace(hour=19)),
                    "value": "0",
                },
                {
                    "from_timestamp": dt_to_ts(sdt_full_hour.replace(hour=19)),
                    "to_timestamp": dt_to_ts(sdt_full_hour.replace(hour=20)),
                    "value": "1",
                },
                {
                    "from_timestamp": dt_to_ts(sdt_full_hour.replace(hour=20)),
                    "to_timestamp": None,
                    "value": "0",
                },
            ],
        }

        return schedules

    def compute_values(self, setpoints, schedules, simulation_dt):
        """
        Compute the values of the simulated devices.

        Values should match the setpoints and schedules defined above.

        Parameters
        ----------
        setpoints : dict.
            As generated by self.compute_setpoits.
        schedules : dict.
            As generated by self.compute_schedules
        simulation_dt : datetime object.
            The current time of the simulation.

        Returns:
        --------
        schedules : dict.
            Datapoint schedules emited at the current simulation time, or
            Empty if if no data would have been emitted. This is at most
            one schedule msg per datapoint and simulation_dt. Format is:
                {<origin_id_of_datapoint>: <value msg>}
        """
        values = {}

        sim_ts = dt_to_ts(simulation_dt)

        # We assume every day is the same, hence compute the values only
        # as function of the time of day and not the date.
        sim_time = simulation_dt.time()

        # First compute the electricity costs matching the schedules
        if sim_time.hour <= 8:
            electricity_price_value = 18.0
        elif sim_time.hour <= 10:
            electricity_price_value = 29.0
        elif sim_time.hour <= 14:
            electricity_price_value = 20.0
        elif sim_time.hour <= 17:
            electricity_price_value = 25.0
        elif sim_time.hour <= 18:
            electricity_price_value = 27.0
        elif sim_time.hour <= 22:
            electricity_price_value = 22.0
        else:
            electricity_price_value = 18.0

        values["apartment_electrcity_price"] = {
            "timestamp": sim_ts,
            "value": str(electricity_price_value),
        }

        # Now the activity flags and energy consumption values per
        # smart appliance device.
        # Assume thereby that the schedules match the setpoints and
        # we don't need to check this.
        appliance_ids = (
            (
                "apartment_electric_power_dishwasher",
                "apartment_dishwasher_active",
            ),
            (
                "apartment_electric_power_washing_machine",
                "apartment_washing_machine_active",
            ),
            (
                "apartment_electric_power_dryer",
                "apartment_dryer_active",
            ),
        )
        for power_id, active_id in appliance_ids:
            # Our basic assumption is that the device is off.
            # Let's check if this is not true. First check if the device
            # should be operating according to the schedule.
            # We start by finding the entry in the device schedule that
            # is currently active.
            device_schedule = schedules[active_id]["schedule"]
            for schedule_item in device_schedule:
                from_timestamp = schedule_item["from_timestamp"]
                to_timestamp = schedule_item["to_timestamp"]
                if from_timestamp is None and sim_ts is None:
                    break
                elif from_timestamp is None:
                    if sim_ts < to_timestamp:
                        break
                    else:
                        # This schedule item is already in the past.
                        continue
                elif to_timestamp is None:
                    if from_timestamp <= sim_ts:
                        break
                    else:
                        # This schedule item is in the future.
                        continue
                elif from_timestamp <= sim_ts and sim_ts < to_timestamp:
                    break
            # Now that we have found our active schedule item, let's check
            # the value and see if the device should be operating.
            if schedule_item["value"] == "0":
                # Nope let's report the zeros and check the other devices.
                values[power_id] = {
                    "timestamp": sim_ts,
                    "value": "0.0",
                }
                values[active_id] = {
                    "timestamp": sim_ts,
                    "value": "0",
                }
                continue

            # Ok, so the schedule says the device should be in operation.
            # Let's see if it has been switched on in a previous loop, and
            # use these information to compute the runtime minute.
            if not hasattr(self, "device_start_times"):
                # This must be the very first run of the first device.
                self.device_start_times = {}
            if active_id not in self.device_start_times:
                # This device hasn't been run before.
                self.device_start_times[active_id] = simulation_dt
            elif (
                self.device_start_times[active_id].date() !=
                simulation_dt.date()
            ):
                # The last run was yesterday. Start a new one.
                self.device_start_times[active_id] = simulation_dt

            # Ok so the device should still be active. Let's compute
            # minutes the device is on already.
            start_time = self.device_start_times[active_id]
            timedelta = simulation_dt - start_time
            runtime_minute = round(timedelta.total_seconds() / 60)

            # So the device is operating, let's load the power profile (
            # the mapping between runtime minute and energy consumption)
            if active_id == "apartment_dishwasher_active":
                power_profile = self.power_profiles["dishwasher"]
            elif active_id == "apartment_washing_machine_active":
                power_profile = self.power_profiles["washingmachine"]
            elif active_id == "apartment_dryer_active":
                power_profile = self.power_profiles["dryer"]

            # Special case, check if the device has finished in the last
            # loop, i.e. last value has been extracted already.
            if runtime_minute >= len(power_profile):
                power_value = "0"
                active_value = "0"
            else:
                active_value = "1"
                power_value = str(power_profile[runtime_minute])

            # That's it. Store the values and continue.
            values[power_id] = {
                "timestamp": sim_ts,
                "value": power_value,
            }
            values[active_id] = {
                "timestamp": sim_ts,
                "value": active_value,
            }
            
        # Compute the total electric power.
        apartment_total_electric_power = (
            100 + 
            float(values["apartment_electric_power_dishwasher"]["value"]) + 
            float(values["apartment_electric_power_washing_machine"]["value"]) + 
            float(values["apartment_electric_power_dryer"]["value"])
        )
        values["apartment_total_electric_power"] = {
            "timestamp": sim_ts,
            "value": apartment_total_electric_power,
        }

        return values


    def simulate_timestep(self, simulation_dt):
        """
        Run the simulation for one timestep. This is intended for a
        timestep frequency of 60 seconds, i.e. simulation_dt should change
        by 60s between two consecutive calls to this method.

        This is NOT mulitprocessing safe, i.e. calls to simulate_timestep
        must be in chronlogical order, as intermediate states are stored
        in the class.

        This function computes not only values and schedules but also
        setpoints, which is not realistic as setpoints would been defined
        by the user via the Energy Management Panel in reality. However,
        in order to process larger times scales without the need for human
        interaction, we compute the setpoints directly here.

        Parameters
        ----------
        simulation_dt : datetime object.
            The current time of the simulation.

        Returns
        -------
        values : dict.
            Datapoint values emited at the current simulation time, or
            Empty if if no data would have been emitted. This is at most
            one value msg per datapoint and simulation_dt. Format is:
                {<origin_id_of_datapoint>: <value msg>}
        setpoints : dict.
            Datapoint setpoints emited at the current simulation time, or
            Empty if if no data would have been emitted. This is at most
            one setpoint msg per datapoint and simulation_dt. Format is:
                {<origin_id_of_datapoint>: <value msg>}
        schedules : dict.
            Datapoint schedules emited at the current simulation time, or
            Empty if if no data would have been emitted. This is at most
            one schedule msg per datapoint and simulation_dt. Format is:
                {<origin_id_of_datapoint>: <value msg>}
        """
        # Compute setpoints and values, as we might need these to compute
        # the values.
        setpoints = self.compute_setpoints(simulation_dt=simulation_dt)
        schedules = self.compute_schedules(simulation_dt=simulation_dt)
        values = self.compute_values(
            setpoints=setpoints,
            schedules=schedules,
            simulation_dt=simulation_dt
        )

        # Now check if setpoint and schedule entries have changed since
        # last call, and if not remove these to prevent flooding the
        # EMP DB with identical values. We simply remove anything that has
        # not changed, which leavs an empty dict if nothing is new.
        active_ids = (
            "apartment_dishwasher_active",
            "apartment_washing_machine_active",
            "apartment_dryer_active",
        )
        for a_id in active_ids:
            if not hasattr(self, "last_schedules"):
                self.last_schedules = {}
            if not hasattr(self, "last_setpoints"):
                self.last_setpoints = {}

            if a_id in self.last_schedules:
                # Timestamp fields should always change, negelect this.
                last_published_schedule = self.last_schedules[a_id]["schedule"]
                current_proposed_schedule = schedules[a_id]["schedule"]
                if last_published_schedule == current_proposed_schedule:
                    del schedules[a_id]
            if a_id in self.last_setpoints:
                last_published_setpoint = self.last_setpoints[a_id]["setpoint"]
                current_proposed_setpoint = setpoints[a_id]["setpoint"]
                if last_published_setpoint == current_proposed_setpoint:
                    del setpoints[a_id]

        # Anything left here is new, and is kept for publishing now and
        # as an udpated reference for the next iteration.
        self.last_setpoints.update(setpoints)
        self.last_schedules.update(schedules)

        return values, schedules, setpoints

class ApartmentNoOpt(Apartment):
    """
    Simulates the operation of an apartment with a handful of smart devices,
    but without any optimizer scheduling these devices.

    Attributes:
    -----------
    name : string
        A friendly name of the class for logs and so on.
    """

    name = "Apartment without optimizer."

    def compute_schedules(self, simulation_dt):
        """
        Compute the schedule for the three flexibile devices.

        Assume we have no optimization algorithm, hence we will start ASAP
        according to the setpoints.

        Parameters
        ----------
        simulation_dt : datetime object.
            The current time of the simulation.

        Returns:
        --------
        schedules : dict.
            Datapoint schedules emited at the current simulation time, or
            Empty if if no data would have been emitted. This is at most
            one schedule msg per datapoint and simulation_dt. Format is:
                {<origin_id_of_datapoint>: <value msg>}
        """
        sdt_full_hour = simulation_dt.replace(
            minute=0,
            second=0,
            microsecond=0,
        )

        schedules = {}
        schedules["apartment_dishwasher_active"] = {
            "timestamp": dt_to_ts(simulation_dt),
            "schedule": [
                {
                    "from_timestamp": None,
                    "to_timestamp": dt_to_ts(sdt_full_hour.replace(hour=9)),
                    "value": "0",
                },
                {
                    "from_timestamp": dt_to_ts(sdt_full_hour.replace(hour=9)),
                    "to_timestamp": dt_to_ts(sdt_full_hour.replace(hour=12)),
                    "value": "1",
                },
                {
                    "from_timestamp": dt_to_ts(sdt_full_hour.replace(hour=12)),
                    "to_timestamp": None,
                    "value": "0",
                },
            ],
        }
        schedules["apartment_washing_machine_active"] = {
            "timestamp": dt_to_ts(simulation_dt),
            "schedule": [
                {
                    "from_timestamp": None,
                    "to_timestamp": dt_to_ts(sdt_full_hour.replace(hour=9)),
                    "value": "0",
                },
                {
                    "from_timestamp": dt_to_ts(sdt_full_hour.replace(hour=9)),
                    "to_timestamp": dt_to_ts(sdt_full_hour.replace(hour=11)),
                    "value": "1",
                },
                {
                    "from_timestamp": dt_to_ts(sdt_full_hour.replace(hour=11)),
                    "to_timestamp": None,
                    "value": "0",
                },
            ],
        }
        schedules["apartment_dryer_active"] = {
            "timestamp": dt_to_ts(simulation_dt),
            "schedule": [
                {
                    "from_timestamp": None,
                    "to_timestamp": dt_to_ts(sdt_full_hour.replace(hour=17)),
                    "value": "0",
                },
                {
                    "from_timestamp": dt_to_ts(sdt_full_hour.replace(hour=17)),
                    "to_timestamp": dt_to_ts(sdt_full_hour.replace(hour=18)),
                    "value": "1",
                },
                {
                    "from_timestamp": dt_to_ts(sdt_full_hour.replace(hour=18)),
                    "to_timestamp": None,
                    "value": "0",
                },
            ],
        }

        return schedules
