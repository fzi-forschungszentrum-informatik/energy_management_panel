FROM iik-gitlab.fzi.de:5050/dwo/energy-service-generics:0.5.0

ENV PYTHONUNBUFFERED 1

# Create the required folder structure.
RUN mkdir -p /source/emp

WORKDIR /source

# Install dependencies
COPY ./requirements.txt /source/requirements.txt
RUN /opt/conda/bin/pip install -r /source/requirements.txt && \
    rm /source/requirements.txt

# Install source code.
COPY --chown=$MAMBA_USER:$MAMBA_USER ./emp/ /source/emp/
COPY --chown=$MAMBA_USER:$MAMBA_USER ./entrypoint.sh /source/entrypoint.sh

# Start the service by default on container startup.
ENTRYPOINT ["/usr/local/bin/_entrypoint.sh", "bash", "/source/entrypoint.sh"]
