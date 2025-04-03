FROM mambaorg/micromamba:1.2.0

LABEL maintainer="Luca Freschi l.freschi@gmail.com"

USER root

# Install dos2unix to fix line endings
RUN apt-get update && apt-get install -y dos2unix

WORKDIR /app

# Copy the repository into the container
COPY . /app

# Grant full permissions to all files in /app
RUN chmod -R 777 /app

# Copy the environment YAML file into the container
COPY env/epc_cli.yaml /tmp/epc_cli.yaml

# Create the environment using the YAML file
RUN micromamba env create -f /tmp/epc_cli.yaml

# Clean up
RUN micromamba clean --all --yes

# Set environment path
ENV PATH /opt/conda/envs/epc_cli/bin:$PATH

# Convert line endings of the script to Unix style
RUN dos2unix /app/bin/epc_automatic_submission

# Ensure all scripts in /app/bin are executable
RUN chmod +x /app/bin/*

# Default command
CMD ["bash"]