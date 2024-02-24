from flask import json, request
import feedparser
from urllib.parse import quote
from datetime import datetime
from validate import convert_gmt_to_ist
from string_literals import JSON_PATH, BASE_URL, POST_ON_X_URL

def getResult():
    # Read configure from JSON file
    with open(JSON_PATH, 'r') as file:
        configure = json.load(file)

    # Get values from the form submission or request
    country = request.form.get('cnt', request.args.get('cnt', None))
    category = request.form.get('ctgry', request.args.get('ctgry', None))

    selected_country = next((c for c in configure['countries'] if c['gl'] == country), None)
    language_param = selected_country.get('hl', 'en') if selected_country else 'en'

    # Encode the category to handle spaces and special characters
    encoded_category = quote(category, safe='') if category else ''

    # Construct the base URL
    base_url = BASE_URL

    # Construct parameters based on conditions
    rss_feed_url = (
        f"{base_url}/search?q={encoded_category}" if not country and category else
        f"{base_url}?hl={country}&gl={country}&ceid={country}" if country and not category else
        f"{base_url}/search?q={encoded_category}&hl={language_param}-{country}&gl={country}&ceid={country}:{language_param}" if country and category else
        base_url
    )

    feed = feedparser.parse(rss_feed_url)
    
    processed_results = []

    for entry in feed.entries:
        # Convert GMT time to IST with offset
        gmt_time = datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %Z")
        ist_date_time_str = convert_gmt_to_ist(gmt_time)

        selected_country_name = next((c['name'] for c in configure['countries'] if c['gl'] == country), None)

        processed_results.append({
            'news_url': entry.link,
            'news_text': entry.title,
            'published_date_time_gmt': gmt_time,  # Original GMT time
            'published_date_time_ist': ist_date_time_str + ' IST',
            'category': category if category else "All News",
            'country': selected_country_name,
            'post_on_x': POST_ON_X_URL
        })

    return processed_results, configure

def getNewsProcessed(processed_results):
    processed_results = sorted(processed_results, key=lambda x: x['published_date_time_gmt'], reverse=True)

    return processed_results