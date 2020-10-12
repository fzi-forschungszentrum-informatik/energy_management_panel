 # Data Format

In order the exchange information with the hardware or other external components (e.g. a optimization algorithm) the EMP expects and provides data in the format specified in this document. We thereby distinguish between value, setpoint and schedule messages. The first carries thereby the value of a sensor or actuator datapoint at a given time. A setpoint message allows defining a set of desired values in future, and a schedule may be computed by an optimization algorithm as the most effective way of realizing the defined setpoints.   

### Datapoint Value

Represents a measurement emitted by an entity, e.g. by a sensor, or a setpoint for an actuator. 

#### Format

```
{
    "value": <string, or null>,
    "type": <integer>,
}
```

#### Fields

| Field       | Description                                                  |
| ----------- | ------------------------------------------------------------ |
| `value`     | The last value of the datapoint. Will be a string or null. Values of numeric datapoints are given as string too.<br /> |
| `timestamp` | The timestamp of the value in milliseconds since 1970-01-01 UTC. |

#### Example

```json
{
    "value": "18.0",
    "timestamp": 1585858832910
}
```

### Datapoint Schedule

This is only applicable to actuator datapoints. A schedule is a plan of actuator values that should be executed by the hardware, and that is received and handled for this reason by a controller service.

#### Format

```
{
    "schedule": <array>,
    "type": <integer>,
}
```

#### Fields

| Field       | Description                                                  |
| ----------- | ------------------------------------------------------------ |
| `schedule`  | The schedule of the datapoint. Each schedule array will hold zero or more schedule items as defined below. |
| `timestamp` | The timestamp the schedule has been created or was received in milliseconds since 1970-01-01 UTC. |

Schedule item fields:

| Field            | Description                                                  |
| ---------------- | ------------------------------------------------------------ |
| `from_timestamp` | The time in milliseconds since 1970-01-01 UTC that the value should be applied. Can be `null` in which case the value should be applied immediately after the schedule is received by the controller. |
| `to_timestamp`   | The time in milliseconds since 1970-01-01 UTC that the value should no longer be applied. Can be `null` in which case the value should be applied forever, or more realistic, until a new schedule is received. |
| `value`          | The value that should be sent to the actuator datapoint. <br /> |

#### Example

Here a schedule that could request a setpoint of 19.0 °C for an AC, starting immediately, and lasting until  Tuesday, 30. July 2019 12:26:53. After that time it would request the AC to be switched off. The interpretation of the null for value depends on the datapoint and should be explicitly mentioned in the datapoint description field. 

```json
{
    "schedule": [
        {
            "from_timestamp": null,
            "to_timestamp": 1564489613000,
            "value": "19.0"
        },
        {
            "from_timestamp": 1564489613000,
            "to_timestamp": null,
            "value": null
        }
    ],
    "timestamp": 1586290918529
}
```

### Datapoint Setpoint

This is only applicable to actuator datapoints. A setpoint is a planed demand for a sensor value. It is the counterpart of the schedule and that is received and handled by a controller service.

#### Format

```
{
    "setpoint": <array>,
    "type": <integer>,
}
```

#### Fields

| Field       | Description                                                  |
| ----------- | ------------------------------------------------------------ |
| `setpoint`  | The setpoint of the datapoint. Each setpoint array will hold zero or more setpoint items as defined below. |
| `timestamp` | The time the REST API received the setpoint message in milliseconds since 1970-01-01 UTC. |

Setpoint item fields:

| Field               | Description                                                  |
| ------------------- | ------------------------------------------------------------ |
| `from_timestamp`    | The time in milliseconds since 1970-01-01 UTC that the setpoint item should be applied. Can be `null` in which case it should be applied immediately after the setpoint is received by the controller. |
| `to_timestamp`      | The time in milliseconds since 1970-01-01 UTC that the setpoint item should no longer be applied Can be `null` in which case it should be applied forever, or more realistic, until a new setpoint is received. |
| `preferred_value`   | The preferred value of the user. This will usually be executed if no schedule is present.<br /> |
| `acceptable_values` | Only applicable to datapoints with discrete data format.<br />A listing of other set values that are acceptable for the user. The controller will ensure that controlled datapoint value remains in the values listed here. Can be an empty array to indicate that there is no flexibility, the controller will always execute the `preferred_value` and ignore the schedule. |
| `min_value`         | Only applicable to datapoints with continuous_numeric data format.<br />Indicates the minimum value of the controlled variable the user is willing to accept. The range between minimum_value and maximum_value is the flexibility of the user. Can be `null` to indicate that no minimum exists. The controller will ignore the schedule and execute `preferred_value` if the controlled datapoint value is below `min_value`. |
| `max_value`         | Only applicable to datapoints with continuous_numeric data format.<br />Indicates the maximum value of the controlled variable the user is willing to accept. The range between minimum_value and maximum_value is the flexibility of the user. Can be `null` to indicate that no maximum exists. The controller will ignore the schedule and execute `preferred_value` if the controlled datapoint value is above `max_value`. |

#### Example

Here a setpoint that could belong to the set temperature of an AC, which only accepts discrete temperatures. The message indicates that setpoint should be applied immediately and should last until Tuesday, 30. July 2019 12:26:53. The user would prefer a temperature of 19°C, but would also accept 17, 18, 20 and 21°C set temperatures.

```json
{
    "setpoint": [
        {
            "from_timestamp": null,
            "to_timestamp": 1564489613491,
            "preferred_value": "19",
            "acceptable_values": [
                "17",
                "18",
                "19",
                "20",
                "21"
            ]
        }
    ],
    "timestamp": 1586301356394
}
```