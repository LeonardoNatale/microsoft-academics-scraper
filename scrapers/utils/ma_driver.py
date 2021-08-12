from typing import Optional, List, Callable, Union, Any

from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, \
    ElementClickInterceptedException, TimeoutException
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from scrapers.utils.custom_error_handling import custom_error_handling


class MADriver(Firefox):

    def __init__(self, firefox_options=None, timeout: int = 5):
        super().__init__(firefox_options=firefox_options)
        self.timeout = timeout

    def get(self, url: str):
        super().get(url=url)

    @custom_error_handling((NoSuchElementException, StaleElementReferenceException))
    def get_text(self, css_string: str, lambda_transform: Callable = None) -> str:
        """
        Gets the text of an element on the page identified by its CSS selector.

        :param css_string: The CSS selector
        :param lambda_transform: An optional transformation to apply to the data.
        :return: The text extracted from the element.
        """

        def dummy_lambda(x):
            return x
        lambda_transform = lambda_transform or dummy_lambda
        return lambda_transform(self.find_element_by_css_selector(css_string).text)

    @custom_error_handling((NoSuchElementException, StaleElementReferenceException))
    def get_text_list(self, css_string: str, lambda_transform: Callable = None) -> Optional[List[Any]]:
        """
        Gets the text of a list of elements on the page identified by a CSS selector.

        :param css_string: The CSS selector
        :param lambda_transform: An optional transformation to apply to the data.
        :return: The list of the texts extracted from the elements.
        """
        def dummy_lambda(x):
            return x
        lambda_transform = lambda_transform or dummy_lambda
        return [
            lambda_transform(elm.text)
            for elm in self.find_elements_by_css_selector(css_string)
            if elm.text
        ]

    @custom_error_handling((NoSuchElementException, StaleElementReferenceException))
    def get_href(self, css_string: str) -> str:
        """
        Gets the link of an element on the page identified by its CSS selector.

        :param css_string: The CSS selector
        :return: The link extracted from the element.
        """
        return self.find_element_by_css_selector(css_string).get_attribute('href')

    @custom_error_handling((NoSuchElementException, StaleElementReferenceException))
    def get_href_list(self, css_string: str) -> List[str]:
        """
        Gets the link of a list of elements on the page identified by a CSS selector.

        :param css_string: The CSS selector
        :return: The list of links extracted from the elements.
        """

        return [
            elm.get_attribute('href')
            for elm in self.find_elements_by_css_selector(css_string)
            if elm.get_attribute('href')
        ]

    @custom_error_handling(
        (NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException),
        False
    )
    def find_and_click(self, css_string) -> bool:
        """
        Try to click on an element given its CSS selector, if clicking is impossible, do nothing.

        :param css_string: The CSS selector.
        :return: True if the click was successful, False otherwise.
        """
        self.find_element_by_css_selector(css_string).click()
        return True

    @custom_error_handling(
        (NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException, TimeoutException),
        None
    )
    def wait_for_css_class(self, func: Callable, css_class: str) -> None:
        """
        Waits for an element to satisfy a given criteria defined by a selenium function.
        The element is identified by its css class.

        :param func: The selenium function to use to wait.
        :param css_class: The class (Not the css selector) to wait for.
        :return: None
        """
        WebDriverWait(self, self.timeout).until(func((By.CLASS_NAME, css_class)))

    def wait_for_papers_to_load(self) -> None:
        """
        Specification of `wait_for_css_class`, to specifically wait for the paper list to appear on the page.
        :return: None
        """
        self.wait_for_css_class(
            func=ec.visibility_of_element_located,
            css_class='primary_paper',
            ignore_exceptions=False
        )

    def wait_and_click(self, func: Callable, css_class: str, css_selector: str,
                       ignore_exceptions: List[bool] = None) -> bool:
        """
        Waits for an element to appear on the page and then clicks on another element.
        Uses the function `wait_for_css_class` to wait for an element.

        :param func: The selenium function to use to wait.
        :param css_class: The class (Not the css selector) to wait for.
        :param css_selector: The css selector of the element to be clicked on.
        :param ignore_exceptions: A List of length 2 specifying it exceptions should be ignored
        for both of the functions called.
        :return: A boolean indicating if the click was successful or not.
        """
        ignore_exceptions = ignore_exceptions or [False, False]
        self.wait_for_css_class(func=func, css_class=css_class, ignore_exceptions=ignore_exceptions[0])
        return self.find_and_click(css_string=css_selector, ignore_exceptions=ignore_exceptions[1])

    def get_next_page_link(self) -> Optional[WebElement]:
        try:
            return self.find_element_by_css_selector('i.icon-up.right')
        except NoSuchElementException:
            return None

    def go_to_next_page(self, next_page_element: WebElement) -> None:
        if next_page_element is not None:
            next_page_element.click()
            self.wait_for_papers_to_load()
