from flask import json, request
import feedparser
from urllib.parse import quote
from datetime import datetime
from validate import convert_gmt_to_ist
from string_literals import JSON_PATH, BASE_URL, POST_ON_X_URL, GEO_LOCATION
import urllib.request
import json
import ssl
import requests
import concurrent.futures

ssl_context = ssl._create_unverified_context()


def get_location():
    with urllib.request.urlopen(GEO_LOCATION, context=ssl_context) as url:
        geo_data = json.loads(url.read().decode())

    location_data = {
        "country_code": geo_data.get('country_code'),
        "country_name": geo_data.get('country_name'),
        # "city": geo_data.get('city'),
        # "postal": geo_data.postal,
        # "latitude":geo_data.latitude,
        # "IPv4":geo_data.IPv4,
        # "state": geo_data.state
    }

    return location_data


def fetch_content(article_url):
    try:
        content_response = requests.get(article_url)
        if content_response.status_code == 200:
            return content_response.url
    except Exception as e:
        pass

    return article_url


def getResult():
    # Read configure from JSON file
    with open(JSON_PATH, 'r') as file:
        configure = json.load(file)

    geo_location = get_location()

    geo_country_code = geo_location.get('country_code')
    country = request.form.get('cnt', request.args.get('cnt', geo_country_code))
    category = request.form.get('ctgry', request.args.get('ctgry', None))
    encoded_category = quote(category, safe='') if category else ''
    base_url = BASE_URL

    selected_country = next((c for c in configure['countries'] if c['gl'] == country), None)
    language_param = selected_country.get('hl', 'en') if selected_country else 'en'

    # Construct parameters based on conditions
    rss_feed_url = (
        f"{base_url}/search?q={encoded_category}" if not country and category else
        f"{base_url}?hl={language_param}-{country}&gl={country}&ceid={country}:{language_param}" if country and not category else
        f"{base_url}/search?q={encoded_category}&hl={language_param}-{country}&gl={country}&ceid={country}:{language_param}" if country and category else
        base_url
    )
    feed = feedparser.parse(rss_feed_url)

    processed_results = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(fetch_content, entry.link) for entry in feed.entries]

        for entry, future in zip(feed.entries, concurrent.futures.as_completed(futures)):
            try:
                content_url = future.result()
            except Exception as e:
                content_url = entry.link

            # Convert GMT time to IST with offset
            gmt_time = datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %Z")
            ist_date_time_str = convert_gmt_to_ist(gmt_time)

            selected_country_name = next(
                (c['name'] for c in configure['countries'] if c['gl'] == country), None)

            processed_results.append({
                'news_url': content_url,
                'news_text': entry.title,
                'published_date_time_gmt': gmt_time,  # Original GMT time
                'published_date_time_ist': ist_date_time_str + ' IST',
                'category': category if category else "All News",
                'country': selected_country_name,
                'post_on_x': POST_ON_X_URL
            })

    return processed_results, configure


def getNewsProcessed(processed_results):
    processed_results = sorted(
        processed_results, key=lambda x: x['published_date_time_gmt'], reverse=True)

    return processed_results
