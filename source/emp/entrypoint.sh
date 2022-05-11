#!/bin/bash
set -e
set -u

echo "Entering entrypoint.sh"

# Ensure the DB layout matches the current state of the application
printf "\n\nCreating and applying migrations."
python3 /source/emp/manage.py makemigrations
python3 /source/emp/manage.py migrate

# Run prod deploy checks if not in devl.
if [ "${DJANGO_DEBUG:-False}" != "TRUE" ]
then
    printf "\n\n"
    echo "Running Djangos production deploy checks"
    python3 /source/emp/manage.py check --deploy
    printf "\nDjango production tests done\n\n"
fi

# Load the demo data.
python3 /source/emp/manage.py loaddata /source/emp/demo_data.json

# Create the admin account from environment variables.
if [ ! -z "${DJANGO_SUPERUSER_PASSWORD}" ] && [ ! -z "${DJANGO_SUPERUSER_USERNAME}" ] && [ ! -z "${DJANGO_SUPERUSER_EMAIL}" ]
then
  printf "\n\n"
  echo "Attempting to create admin account for user $DJANGO_SUPERUSER_USERNAME"
  # The printf should produce no output but catches errors.
  python3 /source/emp/manage.py createsuperuser --no-input || printf ""
fi

# Create a temporary directory as this is required for the Prometheus exporter
# running in multiprocess mode.
export PROMETHEUS_MULTIPROC_DIR="$(mktemp -d)"

# Start up the server, use the internal devl server in debug mode.
# Both serve plain http on port 8080 within the container.
if  [[ "${DJANGO_DEBUG:-FALSE}" == "TRUE" ]]
then
    # --noreload prevents duplicate entries in DB.
    printf "\n\nStarting up Django development server.\n\n\n"
    python3 /source/emp/manage.py runserver 0.0.0.0:8080 &
else
    printf "\n\nCollecting static files."
    python3 /source/emp/manage.py collectstatic --no-input
    printf "\n\nStarting up Gunicorn/UVicorn production server.\n\n\n"
    # Note that the default value of `1` is important here, as
    # emp_main/settings.py expects this default value while processing
    # DJANGO_SECRET_KEY. If you change this to a higher value you will likely
    # get suspicious session warnings and people will need to login on
    # every page the load or so.
    cd /source/emp
    gunicorn emp_main.asgi:application /source/emp/ --workers ${N_WORKER_PROCESSES:-1} --worker-class uvicorn.workers.UvicornWorker -b 0.0.0.0:8080 &
fi

# Patch SIGTERM and SIGINT to the django application.
emp_pid=$!
trap "kill -TERM $emp_pid" SIGTERM
trap "kill -INT $emp_pid" INT

# Run until the container is stopped. Give the EMP maximal 2 seconds to
# clean up and shut down, afterwards we pull the plug hard.
wait
sleep 2
