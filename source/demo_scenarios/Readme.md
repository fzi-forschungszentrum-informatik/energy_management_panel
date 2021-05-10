 

# Demo Scenarios

Simulate the operation of an energy management system incl. optimizer to generate data to demonstrate the UI elements of the EMP. 

This is all quick and dirty here. It's not meant to be used in production or anything.

### Installation

This needs Python 3.8. You need to have the requirements installed. These are not the same requirements as the remaining EMP needs. Use e.g:

```python
pip install -r requirements.txt
```

### Executing

Run the demo scenario by executing:

```python
python3 main.py
```



### Requesting simulation results via API call.

If wish to receive simulation results you first need to compute the timestamps of the corresponding start and ent times in UTC. E.g here between 1612526121000 (Friday, 5 February 2021 11:55:21) and 1612526241000 (Friday, 5 February 2021 11:57:21). You also need to define the scenario name (one of [apt, apt-no]). You can request a simulation run withe following command: 

```bash
curl -X POST "http://localhost:8018/simulation/request/?scenario_name=apt&from_ts=1612526121000&to_ts=1612526241000" -H  "accept: application/json" -d ""
```

The post will return a set of timestamps which have been aligned to match the simulation timestepping, e.g. 

```json
{
  "from_ts": 1612526100000,
  "to_ts": 1612526220000
}
```

Use these returned timestamps (1612526100000 =  Friday, 5 February 2021 11:55:00 and 1612526220000 = Friday, 5 February 2021 11:57:00) for your subsequent requests. 

Before you can download the simulated data you need to check if the data is already available. Do that by executing:

```bash
curl -X GET "http://localhost:8018/apt/simulation/status/?from_ts=1612526100000&to_ts=1612526220000" -H  "accept: application/json"
```

which should return:

```json
{
  "percent complete": 100,
  "ETA seconds": 0
}
```

Once the `percent_complete` has reached 100 it is possible to retrieve the data with:

```bash
curl -X GET "http://localhost:8018/apt/simulation/result/?from_ts=1612526100000&to_ts=1612526220000" -H  "accept: application/json"
```

which would return the following data:

```json
{
  "values": {
    "apartment_electrcity_price": [
      {
        "timestamp": 1612526100000,
        "value": "20.0"
      },
      {
        "timestamp": 1612526160000,
        "value": "20.0"
      },
      {
        "timestamp": 1612526220000,
        "value": "20.0"
      }
    ],
    "apartment_electric_power_dishwasher": [
      {
        "timestamp": 1612526100000,
        "value": "7"
      },
      {
        "timestamp": 1612526160000,
        "value": "7"
      },
      {
        "timestamp": 1612526220000,
        "value": "777"
      }
    ],
    "apartment_dishwasher_active": [
      {
        "timestamp": 1612526100000,
        "value": "1"
      },
      {
        "timestamp": 1612526160000,
        "value": "1"
      },
      {
        "timestamp": 1612526220000,
        "value": "1"
      }
    ],
    "apartment_electric_power_washing_machine": [
      {
        "timestamp": 1612526100000,
        "value": "7"
      },
      {
        "timestamp": 1612526160000,
        "value": "105"
      },
      {
        "timestamp": 1612526220000,
        "value": "7"
      }
    ],
    "apartment_washing_machine_active": [
      {
        "timestamp": 1612526100000,
        "value": "1"
      },
      {
        "timestamp": 1612526160000,
        "value": "1"
      },
      {
        "timestamp": 1612526220000,
        "value": "1"
      }
    ],
    "apartment_electric_power_dryer": [
      {
        "timestamp": 1612526100000,
        "value": "0.0"
      },
      {
        "timestamp": 1612526160000,
        "value": "0.0"
      },
      {
        "timestamp": 1612526220000,
        "value": "0.0"
      }
    ],
    "apartment_dryer_active": [
      {
        "timestamp": 1612526100000,
        "value": "0"
      },
      {
        "timestamp": 1612526160000,
        "value": "0"
      },
      {
        "timestamp": 1612526220000,
        "value": "0"
      }
    ]
  },
  "schedules": {
    "apartment_dishwasher_active": [
      {
        "timestamp": 1612526100000,
        "schedule": [
          {
            "from_timestamp": null,
            "to_timestamp": 1612522800000,
            "value": "0"
          },
          {
            "from_timestamp": 1612522800000,
            "to_timestamp": 1612533600000,
            "value": "1"
          },
          {
            "from_timestamp": 1612533600000,
            "to_timestamp": null,
            "value": "0"
          }
        ]
      }
    ],
    "apartment_washing_machine_active": [
      {
        "timestamp": 1612526100000,
        "schedule": [
          {
            "from_timestamp": null,
            "to_timestamp": 1612522800000,
            "value": "0"
          },
          {
            "from_timestamp": 1612522800000,
            "to_timestamp": 1612530000000,
            "value": "1"
          },
          {
            "from_timestamp": 1612530000000,
            "to_timestamp": null,
            "value": "0"
          }
        ]
      }
    ],
    "apartment_dryer_active": [
      {
        "timestamp": 1612526100000,
        "schedule": [
          {
            "from_timestamp": null,
            "to_timestamp": 1612551600000,
            "value": "0"
          },
          {
            "from_timestamp": 1612551600000,
            "to_timestamp": 1612555200000,
            "value": "1"
          },
          {
            "from_timestamp": 1612555200000,
            "to_timestamp": null,
            "value": "0"
          }
        ]
      }
    ]
  },
  "setpoints": {
    "apartment_dishwasher_active": [
      {
        "timestamp": 1612526100000,
        "setpoint": [
          {
            "from_timestamp": 1612515600000,
            "to_timestamp": 1612544400000,
            "preferred_value": "1",
            "acceptable_values": [
              "0",
              "1"
            ]
          },
          {
            "from_timestamp": 1612544400000,
            "to_timestamp": null,
            "preferred_value": "0",
            "acceptable_values": [
              "0"
            ]
          }
        ]
      }
    ],
    "apartment_washing_machine_active": [
      {
        "timestamp": 1612526100000,
        "setpoint": [
          {
            "from_timestamp": 1612515600000,
            "to_timestamp": 1612551600000,
            "preferred_value": "1",
            "acceptable_values": [
              "0",
              "1"
            ]
          },
          {
            "from_timestamp": 1612551600000,
            "to_timestamp": null,
            "preferred_value": "0",
            "acceptable_values": [
              "0"
            ]
          }
        ]
      }
    ],
    "apartment_dryer_active": [
      {
        "timestamp": 1612526100000,
        "setpoint": [
          {
            "from_timestamp": 1612544400000,
            "to_timestamp": 1612555200000,
            "preferred_value": "1",
            "acceptable_values": [
              "0",
              "1"
            ]
          },
          {
            "from_timestamp": 1612555200000,
            "to_timestamp": null,
            "preferred_value": "0",
            "acceptable_values": [
              "0"
            ]
          }
        ]
      }
    ]
  }
}
```

