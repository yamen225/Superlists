from unittest import skip
from selenium.webdriver.common.keys import Keys
from .base import FunctionalTest


class ItemValidationTest(FunctionalTest):

    def test_cannot_add_empty_list_items(self):
        # Edith goes to the home page and accidentally tries to submit
        # an emoty list item. She hits Enter on the empty input box
        self.browser.get(self.live_server_url)

        self.get_item_input_box().send_keys(Keys.ENTER)
        # The home page refreshes, and there is an error message saying
        # that list items cannot be empty.
        self.wait_for(lambda: self.browser.find_element_by_css_selector(
                '#id_text:invalid'
            ))
        # She tries again with some text and the error disappear
        self.get_item_input_box().send_keys('Buy milk')
        self.wait_for(lambda: self.browser.find_element_by_css_selector(
                '#id_text:valid'
            ))
        # And she can submit successfuly
        self.get_item_input_box().send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1: Buy milk')

        # Perversly, she now decides to submit a second blank list item
        self.get_item_input_box().send_keys(Keys.ENTER)
        # She recieves a similar warning on the list page
        self.wait_for(lambda: self.browser.find_element_by_css_selector(
                '#id_text:invalid'
            ))

        # And she can correct it by filling some text in
        self.get_item_input_box().send_keys('Make tea')
        self.wait_for(lambda: self.browser.find_element_by_css_selector(
                '#id_text:valid'
            ))
        self.get_item_input_box().send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1: Buy milk')
        self.wait_for_row_in_list_table('2: Make tea')
