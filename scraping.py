# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager

def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=False)

    hemisphere_image_urls = hemisphere_images(browser)
    news_title, news_paragraph = mars_news(browser)
    featured_image_url = featured_image(browser)

    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image_url,
        "facts": mars_facts(),
        "hemispheres": hemisphere_image_urls,
        "last_modified": dt.datetime.now()
    }

    # Stop webdriver and return data
    browser.quit()
    return data

def mars_news(browser):
    # Scrape Mars News
    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)
    
    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')
    
    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one("ul.item_list li.slide")
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find("div", class_="content_title").get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find("div", class_="article_teaser_body").get_text()
    
    except AttributeError:
        return None, None
    
    return news_title, news_p

def featured_image(browser):
    # Visit URL
    url = 'https://spaceimages-mars.com/'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
    
    except AttributeError:
        return None
    
    # Use the base url to create an absolute url
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'
    
    return img_url

def mars_facts():
    
    # Add try/exceept for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('https://galaxyfacts-mars.com')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['description', 'Mars', 'Earth']
    df.set_index('description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")

def hemisphere_images(browser):

# 1. Use the browser to visit the URL
    url = 'https://marshemispheres.com/'
    browser.visit(url)

# 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []
    #imgs_links= browser.find_by_css("a.product-item h3")

# 3. Write code to retrieve the image urls and titles for each hemisphere.
    for i in range(4):      
    # Dictionary to store assets
        hemispheres = {}

        browser.find_by_css('a.product-item h3')[i].click()

        element = browser.links.find_by_text('Sample').first
        img_url = element['href']
        title = browser.find_by_css("h2.title").text

        hemispheres["img_url"] = img_url
        hemispheres["title"] = title
        hemisphere_image_urls.append(hemispheres)
        browser.back()

    return hemisphere_image_urls

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())