from flask import json, request
import feedparser
from urllib.parse import quote
from datetime import datetime
from validate import convert_gmt_to_ist
from string_literals import JSON_PATH

def getResult():
    # Read configure from JSON file
    with open(JSON_PATH, 'r') as file:
        configure = json.load(file)

    if request.method == 'POST':
        # Get values from the form submission
        country = request.form.get('cnt', configure['countries'][0]['value'])
        category = request.form.get('ctgry', None)  # Set default value to None
    else:
        # Get values from the request or use defaults
        country = request.args.get('cnt', configure['countries'][0]['value'])
        category = request.args.get('ctgry', None)  # Set default value to None

    if category:
        # Encode the category to handle spaces and special characters
        encoded_category = quote(category, safe='')
        rss_feed_url = f"https://news.google.com/rss/search?q={encoded_category}&hl=en-{country}&gl={country}&ceid={country}:en"
    else:
        rss_feed_url = f"https://news.google.com/rss?hl=en-{country}&gl={country}&ceid={country}:en"

    feed = feedparser.parse(rss_feed_url)
    # Dynamically construct the RSS feed URL with the selected category, if provided    
    processed_results = []

    for entry in feed.entries:
        # Convert GMT time to IST with offset
        gmt_time = datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %Z")
        ist_date_time_str = convert_gmt_to_ist(gmt_time)

        processed_results.append({
            'news_url': entry.link,
            'news_text': entry.title,
            'published_date_time_gmt': gmt_time,  # Original GMT time
            'published_date_time_ist': ist_date_time_str + ' IST',
            'category': category if category else "All News"
        })

    return processed_results, configure


def getNewsProcessed(processed_results):
    processed_results = sorted(processed_results, key=lambda x: x['published_date_time_gmt'], reverse=True)

    return processed_results