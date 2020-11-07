import json
import logging
import os
import sys
from time import sleep

import schedule
from dotenv import load_dotenv

from fast_com import get_stats, SpeedTestException
from mqtt import mqtt_publish, MQTTException

load_dotenv()


def config_logging():
    import time
    logging.getLogger().setLevel(logging.INFO)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.basicConfig(format='{}: GMT: %(asctime)s %(levelname)s %(message)s'.format(os.path.split(sys.argv[0])[1]))
    logging.Formatter.converter = time.gmtime


def main():
    MQTT_HOSTNAME = os.getenv('MQTT_HOSTNAME')
    MQTT_PORT = int(os.getenv('MQTT_PORT'))
    MQTT_USER = os.getenv('MQTT_USER')
    MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')
    MQTT_TOPIC = os.getenv('MQTT_TOPIC')

    config_logging()

    try:
        stats = get_stats()
        logging.info('[INFO] Stats: {}'.format(stats))

        payload = json.dumps(stats)
        mqtt_publish(MQTT_TOPIC, payload, MQTT_HOSTNAME, port=MQTT_PORT, username=MQTT_USER, password=MQTT_PASSWORD)

    except SpeedTestException as e:
        logging.error('[ERROR] SpeedTestException: {}'.format(e.message))

    except MQTTException as e:
        logging.error('[ERROR] MQTTException: {}'.format(e.message))

    except Exception as e:
        logging.error('[ERROR] UNKNOWN Exception: {}'.format(str(e)))


if __name__ == '__main__':
    RUN_EVERY = int(os.getenv('RUN_EVERY', -1))

    main()

    if RUN_EVERY > 0:
        schedule.every(RUN_EVERY).seconds.do(main)

        while True:
            schedule.run_pending()
            sleep(1)
