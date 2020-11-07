class MQTTException(Exception):

    def __init__(self, message):
        self.message = message


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
