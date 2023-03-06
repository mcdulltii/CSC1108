from typing import List, Dict
from tqdm import tqdm
from bs4 import BeautifulSoup
import pickle
import requests
import re


class BusFreqScraper:
    def __init__(self):
        # Bas Muafakat Johor website
        self.url = 'https://businterchange.net/johorbus/routes/routeinfo.php?service={}'
        # URL Query for bus numbers and routes
        self.queries = ['P101', 'P102', 'P106', 'P202', 'P211', 'P411', 'P403']

    def scrape_freq(self) -> Dict[str, List]:
        # Bus frequencies
        bus_freq_dict: Dict[str, List] = {}

        print("Scraping bus frequencies")
        for query in tqdm(self.queries):
            # Retrieve frequency from website url
            page = requests.get(self.url.format(query))
            soup = BeautifulSoup(page.text, 'html.parser')
            # Retrieve article section
            content = soup.find_all('section', {'class': 'article-content'})[0]
            # Retrieve bus frequency table
            table_data = content.find_all('table')[2]
            # Store bus frequencies
            table_freq_arr = table_data.find_all('td', style=lambda x: 'width: 65%' in x)
            for table_freq in table_freq_arr:
                bus_freq = [each.text for each in table_freq.find_all('div')]
                if query not in bus_freq_dict.keys():
                    bus_freq_dict[query] = []
                bus_freq_dict[query].append({
                                    'Start': bus_freq[0],
                                    'Intervals': [int(j) - int(i) for i, j in zip(bus_freq, bus_freq[1:])],
                                    'Frequency': bus_freq
                                })
        
        # Return dictionary of bus number to bus frequencies
        return bus_freq_dict


def main():
    # Start web scraping
    freq_scraper = BusFreqScraper()
    freq = freq_scraper.scrape_freq()

    # Save bus frequencies
    fname = 'freq.bin'
    with open(fname, 'wb') as f:
        pickle.dump(freq, f)
    print(f'Bus frequencies saved to {fname}')


if __name__ == '__main__':
    main()
