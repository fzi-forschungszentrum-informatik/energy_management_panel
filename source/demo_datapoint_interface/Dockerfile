FROM bemcom/energy-service-generics:0.12.3

ENV PYTHONUNBUFFERED 1

# Create the required folder structure.
RUN mkdir -p /source/demo_datatapoint_interface

WORKDIR /source

# Activate this if you have additional dependencies.
#
# Install dependencies first, makes subsequent builds faster.
# COPY ./requirements.txt /source/demo_datatapoint_interface/requirements.txt
# RUN /opt/conda/bin/pip install -r /source/demo_datatapoint_interface/requirements.txt

# Install source code.
COPY --chown=$MAMBA_USER:$MAMBA_USER . /source/demo_datatapoint_interface/

# Start the service by default on container startup.
ENTRYPOINT ["/usr/local/bin/_entrypoint.sh", "bash", "/source/demo_datatapoint_interface/entrypoint.sh"]
