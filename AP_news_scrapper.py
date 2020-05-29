# Import required libs
from bs4 import BeautifulSoup as bs
import requests
import time
from datetime import datetime
import pickle
import os

# FUNCTIONS
# Collects the number of cycles the program should run for, 30 min between each cycle
def set_cycles():
    try:
        cycles = input('Enter number of 30 min AP news scrapper cycle desired = ')
        val = int(cycles)
        done_time = (int(cycles) * 31) - 30
        print('Program running for ' + cycles + ' cycles. Estimated completion in ' + str(done_time) + ' minutes.')
    except ValueError:
        try:
            val = float(cycles)
            print('Invalid input, please enter an integer.')
            set_cycles()
        except ValueError:
            print('Invalid input, please enter a number.')
            set_cycles()
    return cycles

# Function for setting up the soup
def get_soup(base_url, location):
    page = requests.get(base_url + location)
    soup = bs(page.content, 'html.parser')
    return soup


# Checks the URLs pulled from the AP news site for new articles not seen last time and prepares them to be pulled
def new_article_url_pull(refresh_list, master_list, save_location):
    for x in refresh_list:
        if x not in master_list:
            master_list.append(x)
            save_location.append(x)

# Function for pulling the title and body text from the AP Articles
def ap_article_lookup(links, base_url, save_location):
    for link in links:
        v = ''
        soup = get_soup(base_url, link)
        k = soup.find('h1')
        if k is not None:
            k = k.get_text()
            article = soup.find_all('p')
            for paragraph in article:
                if paragraph is not None:
                    clean = paragraph.get_text()
                    if clean is not None:
                        clean = clean.replace('\n', ' ')
                        v = v + ' ' + clean
                        save_location.update({k:v})
    return save_location


# SCRIPT

# Set the site URL
base_url = 'https://apnews.com'

# Sets up the master article URL list
ap_stories_all = []

# Gets the AP site soup
soup = get_soup(base_url, '')

# Starts the program loop
cycles = (int(set_cycles()))

while cycles > 0:
    # Iterates the Soup to the articles
    ap_stories_list = soup.find_all(attrs={'data-key':'card-headline'})
    ap_stories_refresh = []

    # Pulls the article URLs
    for item in ap_stories_list:
        ap_stories_refresh.append(item.get('href'))

    # Filters any None entries
    ap_stories_refresh = list(filter(None, ap_stories_refresh))

    # Creates the list of new article URLs
    ap_stories_new = []
    new_article_url_pull(ap_stories_refresh, ap_stories_all, ap_stories_new)

    # Pulls the titles and test for each article and places them in a dictionary
    ap_article_text = {}
    ap_article_lookup(ap_stories_new, base_url, ap_article_text)

    # Creates a timestamp for teh output file
    dt = datetime.now()
    ts = dt.strftime("%d-%b-%Y (%H %M %S.%f)")

    # Names and dumps teh output file
    dump_file_name = 'AP Articles' + ' ' + ts + '.p'
    pickle.dump(ap_article_text, open(dump_file_name,'wb'))

    # Flavor text and the sleep function
    print(dump_file_name + " pickle dumped to " + os.getcwd())
    cycles = cycles - 1
    if cycles > 0:
        time_remaining = (cycles * 31) - 30
        print(str(cycles) + ' more loops remaining, approx ' + str(time_remaining) + ' minutes left to run.')
        time.sleep(1800)
    else:
        print('Program finished, have a nice day!')

