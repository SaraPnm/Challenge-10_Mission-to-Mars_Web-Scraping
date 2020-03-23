# Import Splinter and BeautifulSoup and pandas
from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt
import traceback
#executable_path = {'executable_path': 'chromedriver'}
#browser = Browser('chrome', **executable_path)

def scrape_all():
    print('**scrape_all')
    # Initiate headless driver for deployment
    browser = Browser("chrome", executable_path="chromedriver", headless=True)        
    news_title, news_paragraph = mars_news(browser)
    # Run all scraping functions and store results in dictionary
    data = {
        'news_title': news_title,
        'news_paragraph': news_paragraph,
        'featured_image': featured_image(browser),
        'facts': mars_facts(),
        'last_modified': dt.datetime.now()
    }

    # Read scrape_hemispheres function
    hemis_list = scrape_hemispheres(browser)
    counter = 1
    for hemis in hemis_list:
        data[f'hemis_{counter}_title'] = hemis['title']
        data[f'hemis_{counter}_img_url'] = hemis['img_url']
        counter += 1

    print(data)
    browser.quit()
    return data

# Set the executable path and initialize the chrome browser in splinter


def mars_news(browser):
    print('**mars_news')
    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    # Optional delay for loading the page
    browser.is_element_present_by_css('ul.item_list li.slide', wait_time=1)

    html = browser.html
    news_soup = BeautifulSoup(html, 'html.parser')
    slide_elem = news_soup.select_one('ul.item_list li.slide')

    # Add tyr/except for error handling
    try:
        slide_elem.find('div', class_='content_title')
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
        return news_title, news_p
    except AttributeError:
        return None, None

# # Featured Images

def featured_image(browser):
    print('**featured_image')
    # Visit URL
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_id('full_image')
    full_image_elem.click()

    # Find the more info button and click that
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.find_link_by_partial_text('more info')
    more_info_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = BeautifulSoup(html, 'html.parser')

    try:
        # Find the relative image url
        img_url_rel = img_soup.select_one('figure.lede a img').get('src')
    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://www.jpl.nasa.gov{img_url_rel}'

    return img_url

def mars_facts():
    print('**mars_facts')
    try:
        # use 'read_html" to scrape the facts table into a dataframe
        df = pd.read_html('http://space-facts.com/mars/')[1]
    #except BaseException:
    #    return None
    except BaseException as e:
        print(str(e))
        traceback.print_exc()
        return None
    # Assign columns and set index of dataframe
    df.columns=['description', 'value_Mars', 'value_earth']
    df.set_index('description', inplace=True)
    # Convert dataframe into HTML format, add bootstrap
    return df.to_html()


def scrape_hemispheres(browser):
    print('**hemisphere')
    # Visit the hemispheres' website
    #browser = Browser("chrome", executable_path="chromedriver", headless=True)        
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)
    # Optional delay for loading the page
    browser.is_element_present_by_css('div.item', wait_time=1)
    html = browser.html
    hem_soup = BeautifulSoup(html, 'html.parser')
    # Find all hemispheres
    descrs = hem_soup.find_all('div', class_='description')

    hemispheres_list = list()

    # Loop through the descriptions
    for descr in descrs:

        # Find each hemisphere
        url_rel = descr.find('a', class_='itemLink product-item').get('href')
        url = f'https://astrogeology.usgs.gov{url_rel}'
        browser.visit(url)
        
        # Open the high resolution image
        open_jpg = browser.find_by_id('wide-image-toggle')
        open_jpg.click()
        
        # Parse the data
        html = browser.html
        img_soup = BeautifulSoup(html, 'html.parser')
        
        # Find image url
        img_rel_url = img_soup.select_one('img.wide-image').get('src')
        img_url = f'https://astrogeology.usgs.gov{img_rel_url}'
        
        # Find image title
        img_title = img_soup.select_one('h2.title').get_text()
        
        # Append the scraped data to the hemispheres' list
        hemispheres_list.append({'title': img_title, 'img_url': img_url})
    return hemispheres_list


if __name__ == '__main__':
    # If running as script, print scraped data
    #scrape_all()
    print('Good Job!')