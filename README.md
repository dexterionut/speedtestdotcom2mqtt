speedtestdotcom2mqtt
====================

Runs a speed test every X seconds and publish the result to an mqtt topic   

Usage:
------
 * Copy `.env.example` to `.env`
 * Add values to the following variables in the created `.env`:
    * `RUN_EVERY` 
        * \<= 0  run only once
        * \> 0  run every X seconds
    * `MQTT_HOSTNAME`
    * `MQTT_USER`
    * `MQTT_PASSWORD`
    * `MQTT_TOPIC`
 * Manual run:
     * Run `pip install requirements.txt` to install the dependencies
     * Run `python3 app.py` to publish to mqtt
 * ***Run using docker: `docker-compose up`***
