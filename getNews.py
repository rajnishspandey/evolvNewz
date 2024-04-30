from flask import json, request
import requests
import feedparser
from urllib.parse import quote
from datetime import datetime
from validate import convert_gmt_to_ist
from string_literals import JSON_PATH, BASE_URL, POST_ON_X_URL,TREND_BASE_URL
import json
import ssl

ssl_context = ssl._create_unverified_context()

# get the value of selected country
def getSelectedCountry():
    country = request.form.get('cnt', None)
    return country

# get json files data
def getJsonData():
    with open(JSON_PATH, 'r') as file:
        configure = json.load(file)

    return configure

# country wise trends
def getTrends(country=None):
    if country:
        trends_feed = f"{TREND_BASE_URL}?geo={country}"
    else:
        trends_feed = TREND_BASE_URL
    
    feed_data = feedparser.parse(trends_feed)
    trending_data = []
    for entry in feed_data.entries:
        trend = {
            'title': entry.title,
        }
        trending_data.append(trend)
    return trending_data

# get news data from google rss feed
def getNewsFeed(encoded_category, country, category, language_param, trending_topic=None):
    rss_feed_url = (
        f"{BASE_URL}/search?q={encoded_category}" if not country and category else
        f"{BASE_URL}?hl={language_param}-{country}&gl={country}&ceid={country}:{language_param}" if country and not category else
        f"{BASE_URL}/search?q={encoded_category}&hl={language_param}-{country}&gl={country}&ceid={country}:{language_param}" if country and category else
        BASE_URL
    )

    # If a trending topic is provided, append it to the URL
    if trending_topic:
        rss_feed_url += f"&q=%23{quote(trending_topic)}"

    feed = feedparser.parse(rss_feed_url)
    return feed


# get the result based on country and category
# Modify the getResult function to accept the trending_category parameter
def getResult(trending_category=None, selected_category=None, selected_country=None):
    configure = getJsonData()
    country = selected_country or getSelectedCountry()

    # Use the selected_category if provided, otherwise use the trending_category
    if selected_category:
        encoded_category = quote(selected_category.encode('utf-8'), safe='')
    elif trending_category:
        encoded_category = quote(trending_category.encode('utf-8'), safe='')
    else:
        # Handle the case when neither selected_category nor trending_category is provided
        encoded_category = ''

    selected_country = next((c for c in configure['countries'] if c['gl'] == country), None)
    language_param = selected_country.get('hl', 'en') if selected_country else 'en'

    # Use getNewsFeed function to get news articles for the selected category
    feed = getNewsFeed(encoded_category, country, encoded_category, language_param)
    processed_results = []

    for entry in feed.entries:
        gmt_time = datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %Z")
        ist_date_time_str = convert_gmt_to_ist(gmt_time)

        selected_country_name = next((c['name'] for c in configure['countries'][1:] if c['gl'] == country), None)
        category_value = selected_category if selected_category else trending_category if trending_category else "All-News"

        # Extract the final destination URL
        actual_url = get_final_destination_url(entry.link)

        if actual_url:
            processed_results.append({
                'news_url': actual_url,
                'news_text': entry.title,
                'published_date_time_gmt': gmt_time,
                'published_date_time_ist': ist_date_time_str + ' IST',
                'country': selected_country_name,
                'category': category_value,
                'post_on_x': POST_ON_X_URL,
            })

    return processed_results, configure

def get_final_destination_url(url):
    try:
        response = requests.head(url, allow_redirects=True)
        return response.url
    except Exception as e:
        print(f"Error fetching final destination URL for {url}: {e}")
        return None

# sorting of news based on published date in descending order
def getNewsSorted(processed_results):
    processed_results = sorted(
        processed_results, key=lambda x: x['published_date_time_gmt'], reverse=True)

    return processed_results