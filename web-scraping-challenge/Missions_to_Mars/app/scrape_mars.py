from splinter import Browser
from bs4 import BeautifulSoup
import requests
import pandas as pd
import datetime as dt
import time
import re
import pymongo
import pprint




def mars_news(browser):
    url = "https://mars.nasa.gov/news/"
    browser.visit(url)

    #Get first list item and wait a half sec if not immediately present
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=0.5)

    html = browser.html
    news_soup = BeautifulSoup(html, "html.parser")

    try:
        slide_elem = news_soup.select_one("ul.item_list li.slide")
        news_title = slide_elem.find("div", class_="content_title").get_text()
        news_paragraph = slide_elem.find("div", class_="article_teaser_body").get_text()
    except AttributeError:
        return None, None
    return news_title, news_paragraph



def featured_image(browser):
    url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(url)
    #find and click the full images button
    full_image_elem = browser.find_by_id("full_image")
    full_image_elem.click()

    #find the info button and click that
    browser.is_element_present_by_text("more info", wait_time=0.5)
    #more_info_elem = browser.find_link_by_partial_text('more info')
    more_info_elem = browser.links.find_by_partial_text('more info')
    more_info_elem.click()

    #Parse the resulting html with soup
    html = browser.html
    img_soup = BeautifulSoup(html, "html.parser")

    #Find the relative image url
    img = img_soup.select_one("figure.lede a img")

    try:
        img_url_rel = img.get("src")
    except AttributeError:
        return None

    #Use the base url to create an absolute url
    img_url = f"https://www.jpl.nasa.gov{img_url_rel}"

    return img_url

def hemispheres(browser):
    url = (
        "https://astrogeology.usgs.gov/search/"
        "results?q=hemisphere+enhanced&k1=target&v1=Mars"
        )
    browser.visit(url)
    hemisphere_image_urls = []
    links = browser.find_by_css("a.product-item h3")
    for i in range(len(links)):
        hemisphere = {}

        browser.find_by_css("a.product-item h3")[i].click()
        #sample_elem = browser.find_link_by_text('Sample').first
        sample_elem = browser.links.find_by_text('Sample').first
        hemisphere['img_url'] = sample_elem["href"]
        hemisphere['title'] = browser.find_by_css("h2.title").text

        hemisphere_image_urls.append(hemisphere)
        browser.back()

    return hemisphere_image_urls

def twitter_weather(browser):
    try:
        url = "https://twitter.com/marswxreport?lang=en"
        browser.visit(url)
        time.sleep(5)

        html = browser.html
        weather_soup = BeautifulSoup(html, 'html.parser')

        mars_weather_tweet = weather_soup.find('div', attrs={"class": "css-1dbjc4n", "span class": "css-901oao css-16my406 r-1qd0xha r-ad9z0x r-bcqeeo r-qvutc0"})

    #try :
        mars_weather = mars_weather_tweet.find("css-901oao css-16my406 r-1qd0xha r-ad9z0x r-bcqeeo r-qvutc0").get_text()
 
     
    except AttributeError:
        pattern = re.compile(r'sol')
        mars_weather = weather_soup.find('span', text=pattern).text
    
    return mars_weather



def mars_facts():
    try:
        df = pd.read_html("https://space-facts.com/mars/")[0]
    except BaseException:
        return None

    df.columns = ["description", "value"]
    df.set_index("description", inplace=True)

    return df.to_html(classes="table table-striped")


def scrape_all():
    executable_path = {"executable_path": 'chromedriver.exe'}
    #browser = Browser("chrome", executable_path ="chromedriver", headless=False)
    browser = Browser('chrome', **executable_path, headless=False)

    news_title, news_paragraph =  mars_news(browser)
    
    data = {
        
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "hemispheres": hemispheres(browser),
        "weather": twitter_weather(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now()
    } 

    browser.quit()

    return data

if __name__== "__main__":

    #if running as a script print scrape data
    print(scrape_all())