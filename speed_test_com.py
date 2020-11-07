import speedtest
import os
import ssl


class SpeedTestException(Exception):

    def __init__(self, message):
        self.message = message


def bypass_https():
    if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
            getattr(ssl, '_create_unverified_context', None)):
        ssl._create_default_https_context = ssl._create_unverified_context


def get_stats():
    bypass_https()

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
