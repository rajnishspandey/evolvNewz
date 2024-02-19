from flask import Flask, render_template, json, request, make_response
import feedparser
from datetime import datetime, timedelta
from urllib.parse import quote
from string_literals import JSON_PATH
from validate import convert_gmt_to_ist

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
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

    # Dynamically construct the RSS feed URL with the selected category, if provided
    if category:
        # Encode the category to handle spaces and special characters
        encoded_category = quote(category, safe='')
        rss_feed_url = f"https://news.google.com/rss/search?q={encoded_category}&hl=en-{country}&gl={country}&ceid={country}:en"
    else:
        rss_feed_url = f"https://news.google.com/rss?hl=en-{country}&gl={country}&ceid={country}:en"

    feed = feedparser.parse(rss_feed_url)
    print("category", category)
    print("url ", rss_feed_url)

    processed_results = []

    for entry in feed.entries:
        image_url = None
        # Check if 'media_thumbnail' is present in the entry
        if 'media_thumbnail' in entry:
            # Attempt to get the URL of the first thumbnail
            image_url = entry.media_thumbnail[0]['url']
        elif 'links' in entry:
            # Look for an image link in 'links'
            for link in entry.links:
                if link.type == 'image/jpeg':
                    image_url = link.href
                    break

        # Convert GMT time to IST with offset
        gmt_time = datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %Z")
        ist_date_time_str = convert_gmt_to_ist(gmt_time)

        processed_results.append({
            'news_url': entry.link,
            'news_text': entry.title,
            'news_image_url': image_url,
            'published_date_time_gmt': gmt_time,  # Original GMT time
            'published_date_time_ist': ist_date_time_str + ' IST',
            'category': category if category else "All News"
        })

    # Sort the processed_results by published date in descending order
    processed_results = sorted(processed_results, key=lambda x: x['published_date_time_gmt'], reverse=True)

    return render_template('index.html', processed_results=processed_results, configure=configure)

@app.route('/sitemap.xml', methods=['GET'])
def sitemap():
    pages = []

    # Add the main page to the sitemap
    pages.append({'url': 'index', 'lastmod': datetime.now().strftime('%Y-%m-%d')})

    # Add other pages dynamically if needed
    # pages.append({'url': 'other_page', 'lastmod': datetime.now().strftime('%Y-%m-%d')})

    sitemap_xml = render_template('sitemap_template.xml', pages=pages)

    response = make_response(sitemap_xml)
    response.headers["Content-Type"] = "application/xml"

    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
