FROM python:3.10-slim-buster

ARG IOT_PATH
ARG IOT_NAME
ARG MQTT_HOST
ARG DB_HOST

ENV IOT_PATH_ENV=${IOT_PATH}
ENV IOT_NAME_ENV=${IOT_NAME}
ENV MQTT_HOST_ENV=${MQTT_HOST}
ENV DB_HOST_ENV=${DB_HOST}

WORKDIR /usr/src/app
# Copy the application files (common code)
COPY app /usr/src/app/app
COPY ../requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Define the entry point for the container (using the copied main.py)
CMD python3 -m $IOT_PATH_ENV --name $IOT_NAME_ENV --mqtt_host $MQTT_HOST_ENV --db_host $DB_HOST_ENV
# CMD python3 -m $IOT_PATH_ENV --db_host $DB_HOST_ENV