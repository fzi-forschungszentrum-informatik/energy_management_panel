# Generic libraries used in [BEMCom](https://github.com/fzi-forschungszentrum-informatik/BEMCom)
# as well as in the EMP. The code should move into a dedicated OS repo once there is spare time.
FROM bemcom/energy-service-generics:0.12.3

ENV PYTHONUNBUFFERED 1

# Create the required folder structure.
RUN mkdir -p /source/emp

WORKDIR /source

# Installs dependencies of the service.
COPY --chown=$MAMBA_USER:$MAMBA_USER environment.yml /tmp/environment.yml
RUN micromamba install --yes --file /tmp/environment.yml && \
    micromamba clean --all --yes && \
    rm /tmp/environment.yml
# Install packages not available on conda.
COPY --chown=$MAMBA_USER:$MAMBA_USER requirements.txt /tmp/requirements.txt
RUN /opt/conda/bin/pip install --no-cache-dir -r /tmp/requirements.txt && \
      rm /tmp/requirements.txt

# Install source code.
COPY --chown=$MAMBA_USER:$MAMBA_USER . /source/emp/

# Start the service by default on container startup.
ENTRYPOINT ["/usr/local/bin/_entrypoint.sh", "bash", "/source/emp/entrypoint.sh"]
