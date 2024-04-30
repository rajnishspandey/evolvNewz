from flask import json, request
import requests
import feedparser
from urllib.parse import quote
from datetime import datetime
from validate import convert_gmt_to_ist
from string_literals import JSON_PATH, BASE_URL, POST_ON_X_URL, TREND_BASE_URL
import json
import ssl
from concurrent.futures import ThreadPoolExecutor

ssl_context = ssl._create_unverified_context()

def getSelectedCountry():
    country = request.form.get('cnt', None)
    return country

def getJsonData():
    with open(JSON_PATH, 'r') as file:
        configure = json.load(file)
    return configure

def getTrends(country=None):
    trends_feed = f"{TREND_BASE_URL}?geo={country}" if country else TREND_BASE_URL
    feed_data = feedparser.parse(trends_feed)
    trending_data = [{'title': entry.title} for entry in feed_data.entries]
    return trending_data

def getNewsFeed(encoded_category, country, category, language_param, trending_topic=None):
    rss_feed_url = (
        f"{BASE_URL}/search?q={encoded_category}" if not country and category else
        f"{BASE_URL}?hl={language_param}-{country}&gl={country}&ceid={country}:{language_param}" if country and not category else
        f"{BASE_URL}/search?q={encoded_category}&hl={language_param}-{country}&gl={country}&ceid={country}:{language_param}" if country and category else
        BASE_URL
    )

    if trending_topic:
        rss_feed_url += f"&q=%23{quote(trending_topic)}"

    feed = feedparser.parse(rss_feed_url)
    return feed

def get_final_destination_url(url):
    try:
        response = requests.get(url, timeout=3)
        return response.url
    except requests.exceptions.RequestException:
        return None

def process_entry(entry, configure, country, selected_category, trending_category):
    gmt_time = datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %Z")
    ist_date_time_str = convert_gmt_to_ist(gmt_time)

    selected_country_name = next((c['name'] for c in configure['countries'][1:] if c['gl'] == country), None)
    category_value = selected_category if selected_category else trending_category if trending_category else "All-News"

    actual_url = get_final_destination_url(entry.link)

    if actual_url:
        return {
            'news_url': actual_url,
            'news_text': entry.title,
            'published_date_time_gmt': gmt_time,
            'published_date_time_ist': ist_date_time_str + ' IST',
            'country': selected_country_name,
            'category': category_value,
            'post_on_x': POST_ON_X_URL,
        }

def getResult(trending_category=None, selected_category=None, selected_country=None):
    configure = getJsonData()
    country = selected_country or getSelectedCountry()

    encoded_category = quote(selected_category.encode('utf-8'), safe='') if selected_category else quote(trending_category.encode('utf-8'), safe='') if trending_category else ''

    selected_country = next((c for c in configure['countries'] if c['gl'] == country), None)
    language_param = selected_country.get('hl', 'en') if selected_country else 'en'

    feed = getNewsFeed(encoded_category, country, encoded_category, language_param)

    with ThreadPoolExecutor() as executor:
        processed_results = list(executor.map(process_entry, feed.entries, [configure]*len(feed.entries), [country]*len(feed.entries), [selected_category]*len(feed.entries), [trending_category]*len(feed.entries)))

    return [result for result in processed_results if result], configure

def getNewsSorted(processed_results):
    processed_results = sorted(processed_results, key=lambda x: x['published_date_time_gmt'], reverse=True)
    return processed_results