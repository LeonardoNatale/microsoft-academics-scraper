from selenium.webdriver import FirefoxOptions

from scrapers.utils.ma_driver import MADriver


class DriverFactory:

    def __init__(self):
        pass

    @staticmethod
    def get_driver(headless: bool = True, timeout: int = 5) -> MADriver:
        options = FirefoxOptions()
        if headless:
            options.add_argument('--headless')
        return MADriver(firefox_options=options, timeout=timeout)

