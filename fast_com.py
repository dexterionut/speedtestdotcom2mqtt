import pingparsing
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from contextlib import contextmanager


class SpeedTestException(Exception):

    def __init__(self, message):
        self.message = message


def get_chrome_options():
    """Sets chrome options for Selenium.
    Chrome options for headless browser is enabled.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_prefs = {"profile.default_content_settings": {"images": 2}}
    chrome_options.experimental_options["prefs"] = chrome_prefs
    return chrome_options


@contextmanager
def get_chrome() -> Chrome:
    opts = get_chrome_options()
    driver = Chrome(options=opts)
    yield driver
    driver.close()


def wait_until_present(driver: Chrome, selector: str, timeout: int = 5):
    condition = EC.presence_of_element_located((By.CSS_SELECTOR, selector))
    try:
        WebDriverWait(driver, timeout).until(condition)
    except TimeoutException as e:
        raise LookupError(f'{selector} is not present after {timeout}s') from e


def extract_speed_info(soup: BeautifulSoup) -> dict:
    dl_speed = round(float(soup.select_one('#speed-value').text), 2)
    dl_unit = soup.select_one('#speed-units').text
    upload_speed = round(float(soup.select_one('#upload-value').text), 2)
    upload_unit = soup.select_one('#upload-units').text
    server_locations = soup.select_one('#server-locations').text

    return {
        'download': f'{dl_speed} {dl_unit}',
        'upload': f'{upload_speed} {upload_unit}',
        'server_locations': server_locations.replace(u'\xa0', ' ')
    }


def run_speed_test() -> dict:
    with get_chrome() as driver:
        driver.get('https://fast.com')

        # wait at most 60s until upload results come in
        upload_done_selector = '#upload-value.succeeded'
        wait_until_present(driver, upload_done_selector, timeout=100)

        # this is the parent element that contains both download and upload results
        results_selector = '.speed-container'
        results_el = driver.find_element_by_css_selector(results_selector)
        results_html = results_el.get_attribute('outerHTML')

    # we're finished with chrome, let it close (by exiting with block)

    soup = BeautifulSoup(results_html, 'html.parser')
    info = extract_speed_info(soup)
    return info


def run_ping_test():
    ping_parser = pingparsing.PingParsing()
    transmitter = pingparsing.PingTransmitter()
    transmitter.destination = "google.com"
    transmitter.count = 10
    result = transmitter.ping()

    result_dict = ping_parser.parse(result).as_dict()

    return result_dict


def get_stats():
    try:
        ping_results = run_ping_test()
        speed_results = run_speed_test()

        results = {
            **speed_results,
            'ping': int(round(ping_results['rtt_avg'], 0))
        }

        return results
    except Exception as e:
        raise SpeedTestException(str(e))
