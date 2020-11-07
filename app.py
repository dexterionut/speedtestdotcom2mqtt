import json
import logging
import os
import ssl
import sys
from time import sleep

import schedule
from dotenv import load_dotenv
import speedtest

load_dotenv()


class SpeedTestException(Exception):

    def __init__(self, message):
        self.message = message


class MQTTException(Exception):

    def __init__(self, message):
        self.message = message


def config_logging():
    import time
    logging.getLogger().setLevel(logging.INFO)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.basicConfig(format='{}: GMT: %(asctime)s %(levelname)s %(message)s'.format(os.path.split(sys.argv[0])[1]))
    logging.Formatter.converter = time.gmtime


def bypass_https():
    if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
            getattr(ssl, '_create_unverified_context', None)):
        ssl._create_default_https_context = ssl._create_unverified_context


def get_stats():
    try:
        servers = []

        s = speedtest.Speedtest(secure=False)
        s.get_servers(servers)
        s.get_best_server()
        s.download()
        s.upload()
        s.results.share()

        result_dict = s.results.dict()

        return {
            'download': round(result_dict['download'] / 1024 / 1024, 2),
            'upload': round(result_dict['upload'] / 1024 / 1024, 2),
            'unit': 'Mbps',
            'ping': int(round(result_dict['ping'], 0)),
            'server': '{} [{}, {}]'.format(result_dict['server']['sponsor'], result_dict['server']['name'],
                                           result_dict['server']['country'])
        }
    except Exception as e:
        raise SpeedTestException(str(e))


def mqtt_publish(topic, payload, hostname, port=1883, username=None, password=None):
    try:
        import paho.mqtt.publish as publish

        auth = None

        if username and password:
            auth = {'username': username, 'password': password}

        publish.single(
            hostname=hostname,
            port=port,
            auth=auth,
            topic=topic,
            payload=payload,
            keepalive=10
        )
    except Exception as e:
        raise MQTTException(str(e))


def main():
    MQTT_HOSTNAME = os.getenv('MQTT_HOSTNAME')
    MQTT_PORT = int(os.getenv('MQTT_PORT'))
    MQTT_USER = os.getenv('MQTT_USER')
    MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')
    MQTT_TOPIC = os.getenv('MQTT_TOPIC')

    config_logging()
    bypass_https()

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

    if RUN_EVERY <= 0:
        main()
    else:
        schedule.every(RUN_EVERY).seconds.do(main)

        while True:
            schedule.run_pending()
            sleep(1)
