#!/usr/bin/env python
# coding: utf-8



# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt

def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)
    
    news_title, news_p = mars_news(browser)
    hemisphere_image_urls = hemisphere_images(browser)
    data = {
        "news_title": news_title,
        "news_p": news_p,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemispheres" : hemisphere_image_urls
    }
   
    browser.quit()
    return data


# # Scrape articles
# Visit the mars nasa news site
def mars_news(browser):
    url = 'https://redplanetscience.com'
    browser.visit(url)
    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    html = browser.html
    news_soup = soup(html, 'html.parser')
    try:
        slide_elem = news_soup.select_one('div.list_text')
        slide_elem.find('div', class_='content_title')

        news_title = slide_elem.find('div', class_='content_title').get_text()
        

        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    except AttributeError:
        return None, None   

    return news_title, news_p

# # Scrape Images
# Visit URL
def featured_image(browser):
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
    
    except AttributeError:
        return None    

    # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'
    
    return img_url


def mars_facts():
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('http://galaxyfacts-mars.com')[0]
    except BaseException:
        return None
    # Assign columns and set index of dataframe
    df.columns=['description','Mars','Earth']
    df.set_index('description', inplace=True)
    
    # Convert dataframe into HTML format, add bootstrap
    return df.to_html()

def hemisphere_images(browser):
    url = 'https://marshemispheres.com/'
    browser.visit(url)

    hemisphere_image_urls = []
    
    for i in range(4):
        hemispheres = {}
        try:
            browser.find_by_css("a.itemLink h3")[i].click()
            hemi_image_elem = browser.links.find_by_text("Sample")
            image_url = hemi_image_elem['href']
            title = browser.find_by_css("h2.title").text
            hemispheres["img_url"] = image_url
            hemispheres["title"] = title
            hemisphere_image_urls.append(hemispheres)
            browser.back()
        except AttributeError:
            return None
    return hemisphere_image_urls


if __name__ == "__main__":
    #if run as as script, print scraped data
    print(scrape_all())







