# Deployment

Here some instructions to deploy a EMP container. Please note that the EMP needs a [Timescale DB](https://hub.docker.com/r/timescale/timescaledb) and a [Redis](https://hub.docker.com/_/redis) instance to work, which you likely want to deploy as containers too. [Grafana](https://hub.docker.com/r/grafana/grafana) is optional but integrates nicely to display the historic development of datapoint values.   

## Ports

This service serves plain HTTP only.

**Note: If the API service should be exposed on the public it is absolutely important to place a reverse proxy like nginx in front of the service to secure the connection with HTTPS.**

**Note further: The `api/` endpoint is currently not protected by reasonable authorization measures. It is strongly advised to restrict access, e.g. by configuring a reverse proxy accordingly.**

| Port | Usage/Remarks                                   |
| ---- | ----------------------------------------------- |
| 8080 | REST interface and user interface on plain HTTP |

## Environment Variables

| Enironment Variable              | Example  Value                                               | Usage/Remarks                                                |
| -------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| N_WORKER_PROCESSES               | 16                                                           | The number of parallel worker processes that are used by the production server (UVicorn) to run the application. A sane number may be roughly 2-4 times the number of cores. Defaults to 1.<br />**NOTE: Don't go over 1 here yet. The update mechanism for new permissions isn't process safe yet.** |
| LOGLEVEL                         | INFO                                                         | Defines the log level. Should be one of the following strings: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`. See the [Django docs on logging](https://docs.djangoproject.com/en/3.1/topics/logging/) for details. Defaults to `INFO`. |
| HTTPS_ONLY                       | FALSE                                                        | If set to `TRUE` (the string) will assume that the EMP is only served via HTTPs and additional security measures can be activated. (i.e. [SESSION_COOKIE_SECURE](https://docs.djangoproject.com/en/3.2/ref/settings/#session-cookie-secure) and [CSRF_COOKIE_SECURE](https://docs.djangoproject.com/en/3.2/ref/settings/#csrf-cookie-secure)). This is advised for production use. Defaults to `FALSE`. |
| DJANGO_SECRET_KEY                | oTg2aWkM...                                                  | Can be used to specify the [SECRET_KEY](https://docs.djangoproject.com/en/3.1/ref/settings/#std:setting-SECRET_KEY) setting of Django. Defaults to a random sequence of 64 chars generated on container startup. Note that changing the secret key will invalidate all cookies and thus force all user to login again. |
| DJANGO_ALLOWED_HOSTS             | ["emp.domain.com"]                                           | A list of fully qualified hostnames the API service should be hosted on. Must be encoded as JSON string. See the [ALLOWED_HOSTS](https://docs.djangoproject.com/en/3.1/ref/settings/#allowed-hosts) setting of Django for details. Defaults to `'["localhost"]'`, which means that API can only be accessed from the local machine. |
| DJANGO_DEBUG                     | FALSE                                                        | If set to `TRUE` (the string) will activate the [debug mode of django](https://docs.djangoproject.com/en/3.1/ref/settings/#debug), which should only be used while developing not during production operation. Defaults to False |
| DJANGO_ADMINS                    | '["John", "john@example.com"]'                               | Must be a valid JSON string. Is set to [ADMINS setting](https://docs.djangoproject.com/en/3.1/ref/settings/#admins) of Django. Defaults to an empty list. |
| DJANGO_ADDITIONAL_INSTALLED_APPS | ["your_emp_app.apps.YourEmpAppConfig"]                       | Must be a valid JSON array. Allows to extend the EMP with custom apps by simply mounting the files into the EMP container, i.e. without the need to adjust [INSTALLED_APPS](https://docs.djangoproject.com/en/4.1/ref/settings/#std-setting-INSTALLED_APPS) in [emp_main/settings.py](../source/emp/emp_main/settings.py). |
| DJANGO_SUPERUSER_USERNAME        | admin                                                        | If username, password and email is provided will attempt to create a superuser account with these credentials. |
| DJANGO_SUPERUSER_PASSWORD        | pass                                                         | See above.                                                   |
| DJANGO_SUPERUSER_EMAIL           | admin@example.com                                            | See above.                                                   |
| EMPDB_HOST                       | timescaledb.domain.de                                        | The DNS name or IP address of the TimescaleDB used to persist data. Note that `localhost` will not work, use the full DNS name of the host machine instead. If left empty defaults to use a SQLite with data stored in file source/db.sqlite3 . |
| EMPDB_PORT                       | 5433                                                         | The port of the TimescaleDB. Defaults to `5432`.             |
| EMPDB_USER                       | johndoe                                                      | The username used for authentication at TimescaleDB. Defaults to `emp`. |
| EMPDB_PASSWORD                   | VerySecret123                                                | The password used for authentication at TimescaleDB. Defaults to `emp`. |
| EMPDB_DBNAME                     | bemcom                                                       | The name of the of the database inside TimescaleDB to store the data in. Defaults to `emp` |
| CHANNELS_REDIS_HOST              | redis.domain.de                                              | The DNS name or IP address of the Redis database used for pushing updates to websockets with [Django Channel Layers](https://channels.readthedocs.io/en/stable/topics/channel_layers.html). If left empty, will fall back to [In-Memory Channel Layer](https://channels.readthedocs.io/en/stable/topics/channel_layers.html) which is not suitable for production. |
| CHANNELS_REDIS_PORT              | 16379                                                        | The port of the Redis database. Defaults to `6379`.          |
| EMP_ADDITIONAL_APPS              | ["your_emp_app"]                                             | Like `DJANGO_ADDITIONAL_INSTALLED_APPS` above but for the `EMP_APPS` entry of [emp_main/settings.py](../source/emp/emp_main/settings.py). See details there. |
| EMP_PAGE_TITLE                   | See [emp_main/settings.py](../source/emp/emp_main/settings.py). | Allows to overwrite `PAGE_TITLE` setting in [emp_main/settings.py](../source/emp/emp_main/settings.py). See details there. |
| EMP_MANIFEST_JSON_STATIC         | See [emp_main/settings.py](../source/emp/emp_main/settings.py). | Allows to overwrite `MANIFEST_JSON_STATIC` setting in [emp_main/settings.py](../source/emp/emp_main/settings.py). See details there. |
| EMP_FAVICON_ICO_STATIC           | See [emp_main/settings.py](../source/emp/emp_main/settings.py). | Allows to overwrite `FAVICON_ICO_STATIC` setting in [emp_main/settings.py](../source/emp/emp_main/settings.py). See details there. |
| EMP_TOPBAR_LOGO_STATIC           | See [emp_main/settings.py](../source/emp/emp_main/settings.py). | Allows to overwrite `TOPBAR_LOGO_STATIC` setting in [emp_main/settings.py](../source/emp/emp_main/settings.py). See details there. |
| EMP_TOPBAR_NAME_SHORT            | See [emp_main/settings.py](../source/emp/emp_main/settings.py). | Allows to overwrite `TOPBAR_NAME_SHORT` setting in [emp_main/settings.py](../source/emp/emp_main/settings.py). See details there. |
| EMP_TOPBAR_NAME_LONG             | See [emp_main/settings.py](../source/emp/emp_main/settings.py). | Allows to overwrite `TOPBAR_NAME_LONG` setting in [emp_main/settings.py](../source/emp/emp_main/settings.py). See details there. |
| EMP_URLS_PERMISSION_WHITELIST    | See [emp_main/settings.py](../source/emp/emp_main/settings.py). | Allows to overwrite `URLS_PERMISSION_WHITELIST` setting in [emp_main/settings.py](../source/emp/emp_main/settings.py). See details there. |
| EMP_HOME_PAGE_URL                | See [emp_main/settings.py](../source/emp/emp_main/settings.py). | Allows to overwrite `HOME_PAGE_URL` setting in [emp_main/settings.py](../source/emp/emp_main/settings.py). See details there. |
| EMP_LOGIN_PAGE_URL               | See [emp_main/settings.py](../source/emp/emp_main/settings.py). | Allows to overwrite `LOGIN_PAGE_URL` setting in [emp_main/settings.py](../source/emp/emp_main/settings.py). See details there. |
| EMP_LOGOUT_PAGE_URL              | See [emp_main/settings.py](../source/emp/emp_main/settings.py). | Allows to overwrite `LOGOUT_PAGE_URL` setting in [emp_main/settings.py](../source/emp/emp_main/settings.py). See details there. |

## Volumes

None for most scenarios. Eventually a volume may be used to persist the SQLite database file.



