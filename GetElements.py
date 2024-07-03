import os
import time
import logging
import datetime
import re
import glob

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException


class GetElements:
    def __init__(self, websiteDict):
        # Initialize class variables
        self.websiteDict = websiteDict
        self.driver = None
        self.wait = None
        self.searchText = "Robotics"

        # Get the Media Folder
        file_path = os.path.dirname(os.path.realpath(__file__))
        self.full_path = file_path + "\\News_media\\"

    def start_browser(self, website: str, browser: int = 0):
        """Start the browser via Selenium and load the website."""

        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument('disable-notifications')

        logging.info("Starting application...")
        if browser == 0:
            logging.info("Starting browser Chrome")
            self.driver = webdriver.Chrome(options=chrome_options)

        ### IMPLEMENT FOR ANOTHER BROWSERS ###

        # Open the specified website and maximize window
        self.wait = WebDriverWait(self.driver, timeout=20)
        self.driver.maximize_window()
        self.driver.get(website)

    def close_browser(self):
        """Exit the application by closing the browser opened"""
        logging.info("Quiting application...")
        self.driver.quit()

    def search(self, TEXT_TO_SEARCH:str):
        """Open the Search bar and search the input text chosen by the user."""
        self.searchText = TEXT_TO_SEARCH
        # Open the Text input
        searchButtonElement = self.driver.find_element(By.CLASS_NAME, value=self.websiteDict['searchButton'])
        searchButtonElement.click()

        # Paste the text in the research bar and search
        textInputElement = self.driver.find_element(By.CLASS_NAME, value=self.websiteDict['textInput'])
        textInputElement.click()
        textInputElement.send_keys(self.searchText, Keys.ENTER)

    def filter(self):
        """Sort the news in the page by newest, the allow the user to choose one option of filtering categories."""

        # Sort the page elements by Newest
        Select(self.wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, self.websiteDict['selectionNewest']['element'])))).select_by_value(
            self.websiteDict['selectionNewest']['value'])
        time.sleep(5)

        # Get the filtering options from website
        self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, self.websiteDict['selectionFilter']['element']))).click()
        categories = self.driver.find_elements(By.CSS_SELECTOR, self.websiteDict['selectionFilter']['checkbox'])

        # Exhibits the options to user ate the terminal
        filter_msg = "The available filtering options are listed bellow:\n0 - EXIT FILTERING OPTIONS"
        n = 1
        for category in categories:
            filter_msg += f"\n{n} - {category.text}"
            n += 1
        print(filter_msg)

        # Get the user choice for filtering data
        while True:
            try:
                userInput = int(input("Enter your answer: "))
                if userInput >= n:
                    logging.warning("Invalid answer! Choose a number from the list above.")
            except ValueError:
                logging.warning("Not an integer! Choose a number from the list above.")
                continue
            if userInput == 0:
                print("Exiting filter options.")
                break
            else:
                print(f"{categories[userInput - 1].text} selected!")
                self.wait.until(EC.element_to_be_clickable(categories[userInput - 1])).click()
                print("Exiting filter options.")
                break

    def get_data(self, months: int = 0):
        """Get the news data from the website and store in a dictionary."""
        # Initialize variables
        i = 0
        news = {}
        # Get the month datas
        current_month = datetime.date.today().month
        start_month = current_month - months - 1
        months_list = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october',
                       'november', 'december']

        # Filter the months
        del months_list[start_month:current_month]

        # Insert elements in the dictionary
        while True:
            # Get all the news from the page
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.websiteDict['results'])))
            results = self.driver.find_elements(By.CSS_SELECTOR, self.websiteDict['results'])

            for result in results:
                while True:
                    try:
                        # Get the main data from each news
                        name = result.find_element(By.CSS_SELECTOR, value=self.websiteDict['resultElements']['name']).text
                        date = result.find_element(By.CSS_SELECTOR, value=self.websiteDict['resultElements']['date']).text
                        #name = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.websiteDict['resultElements']['name']))).text
                        #print(name)
                        try:
                            description = result.find_element(By.CSS_SELECTOR,
                                                              value=self.websiteDict['resultElements']['desc']).text
                            #description = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.websiteDict['resultElements']['desc']))).text
                        except TimeoutException as e:
                            print(e)
                            description = "No Description available"
                        #date = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.websiteDict['resultElements']['date']))).text

                        # Verify if the date of the news is valid
                        if any(month in date.lower() for month in months_list):
                            # If item isn't valid, return the actual News
                            return news

                        # Update the dictionary
                        news[i] = {
                            'name': name,
                            'description': description,
                            'date': date,
                            'media': self._image_exists(result, i),
                            'search_phrases': self.count_search_phrases(name) + self.count_search_phrases(description),
                            'contains_money': self.contains_money(name) or self.contains_money(description)
                        }
                        i += 1
                        break

                    except NoSuchElementException as e:
                        # Dealing with the possible pop up in the news page:
                        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.websiteDict['popUP']))).click()

            self._next_page()

    def count_search_phrases(self, text:str):
        """Count how much times the searched phrase shown in the input text."""
        return text.lower().count(self.searchText.lower())

    def contains_money(self, text:str):
        """Count how many times a text contains any amount of money shows in a text.
        Return True if any amount of money is found.
        Return False if not."""

        try:
            items = re.findall(r"(?:[$]{1}[.,\d]+|[.,\d]+\s*(?:dollars|USD))", text)
            if len(items) > 0:
                return True
            else:
                return False
        except:
            logging.error("Something went wrong when counting the amount of money is in a text")

    def _image_exists(self, result, i: int):
        """Verify the existence of the image for the selected news.
        If the media exists, save the file in a folder 'News_media'."""

        # Create the path if it doesn't exist.
        if not os.path.exists(self.full_path):
            os.makedirs(self.full_path)

        if bool(result.find_elements(By.CSS_SELECTOR, self.websiteDict['resultElements']['img'])):
            filename = 'filename' + str(i) + '.png'
            # Save the image file in a folder with name "filename + number of the selected news"
            with open(self.full_path + filename, 'wb') as file:
                file.write(result.find_element(By.CSS_SELECTOR, self.websiteDict['resultElements']['img']).screenshot_as_png)
            # Change for the image path
            return self.full_path + filename

        # For news without media
        else:
            return "No media Found"

    def _next_page(self):
        """Click in the next page button when the webpage is at the search tab"""
        self.driver.find_element(By.CSS_SELECTOR,
                                 value=self.websiteDict['nextPage']).click()