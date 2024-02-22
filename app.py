from flask import Flask, render_template, json, request, redirect, url_for,flash
import feedparser
from datetime import datetime
from urllib.parse import quote
from string_literals import JSON_PATH,INDEX_TITLE,FEEDBACK_TITLE
from validate import convert_gmt_to_ist, send_email
import secrets
from flask.helpers import get_flashed_messages 

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

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

    # Sort the processed_results by published date in descending order
    processed_results = sorted(processed_results, key=lambda x: x['published_date_time_gmt'], reverse=True)
    
    flash_messages = []  # Initialize an empty list

    # Check if there are flash messages
    flash_messages = get_flashed_messages(category_filter=['success'])
    
    return render_template('index.html', 
                           processed_results=processed_results, 
                           configure=configure,
                           title=INDEX_TITLE,
                           flash_messages=flash_messages
                           )

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        feedback_name = request.form['name'][:50]
        feedback_text = request.form['feedback'][:250]
        send_email(feedback_name,feedback_text)

        # Use the 'success' category for the flash message
        flash('Your Feedback is our motivation towards improvement', 'success')

        return redirect(url_for('index'))

    return render_template('feedback.html', title=FEEDBACK_TITLE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
