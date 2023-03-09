from typing import List, Dict
from tqdm import tqdm
import pickle
import time

from selenium import webdriver
from selenium.webdriver.firefox.options import Options


class BusRouteScraper:
    def __init__(self):
        # Bas Muafakat Johor website
        self.url = 'https://businterchange.net/johorbus/routes/routeinfo.php?service={}&selection=Direction+{}'
        # URL Query for bus numbers and routes
        self.queries = ['P101_1', 'P102_1', 'P102_2', 'P106_1', 'P202_1', 'P211_1', 'P211_2', 'P411_1', 'P411_2', 'P403_1']
        # JS routes variable
        self.route = 'busPolylineArray'
        # Amount of seconds to wait for website to load
        self.wait = 5

    def scrape_routes(self) -> Dict[str, List]:
        # Bus Routes
        bus_routes: Dict[str, List] = {}

        # Selenium web driver
        options = Options()
        options.add_argument('-headless')
        driver = webdriver.Firefox(options=options)
        print("Scraping bus routes")
        for query in tqdm(self.queries):
            # Retrieve route from website url
            driver.get(self.url.format(*query.split('_')))
            time.sleep(self.wait)
            bus_routes[query] = driver.execute_script(f'return {self.route}')
        driver.quit()

        # Return dictionary of bus number to bus routes
        return bus_routes


def main():
    # Start web scraping
    route_scraper = BusRouteScraper()
    routes = route_scraper.scrape_routes()

    # Save bus routes
    fname = 'routes.bin'
    with open(fname, 'wb') as f:
        pickle.dump(routes, f)
    print(f'Bus routes saved to {fname}')


if __name__ == '__main__':
    main()
