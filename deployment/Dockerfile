FROM python:3.10-slim-buster

ARG IOT_PATH
ENV IOT_ENV=${IOT_PATH}
WORKDIR /usr/src/app
# Copy the application files (common code)
COPY app /usr/src/app/app
COPY ../requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Define the entry point for the container (using the copied main.py)
CMD python3 -m $IOT_ENV --mqtt_host mosquitto --db_host postgres
# CMD ["/bin/bash", "-c", "which python3 && python3 --version || echo 'Python not found'"]