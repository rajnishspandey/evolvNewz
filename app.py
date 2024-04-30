from flask import Flask, render_template, request, redirect, url_for,flash, json
from string_literals import *
from validate import is_valid_input, send_email
import secrets
from flask.helpers import get_flashed_messages 
from getNews import getResult, getNewsSorted,getSelectedCountry,getTrends


app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

@app.route('/', methods=['GET', 'POST'])
def index():
    
    processed_results,configure = getResult(selected_country=getSelectedCountry())
    # Sort the processed_results by published date in descending order
    processed_results = getNewsSorted(processed_results[:4])

    trending_topics = getTrends(country=getSelectedCountry())
    flash_messages = []  # Initialize an empty list
    # Check if there are flash messages
    flash_messages = get_flashed_messages(category_filter=['success'])

    return render_template('index.html', 
                           processed_results=processed_results, 
                           configure=configure,
                           title=INDEX_TITLE,
                           flash_messages=flash_messages,
                           trending_topics = trending_topics
                           )

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        feedback_name = request.form['name']
        feedback_text = request.form['feedback']

        if is_valid_input(feedback_name, feedback_text):
            send_email(feedback_name, feedback_text)
            flash(SUCCESS_FEEDBACK_MESSAGE, SUCCESS)
            return redirect(url_for('index'))
        else:
            if len(feedback_text.strip()) > 250:
                flash(CHARACTERS_ERROR_MESSAGE, ERROR)
            else:
                flash(FEEDBACK_FORM_VALIDATION_ERROR, ERROR)


    return render_template('feedback.html', title=FEEDBACK_TITLE)

@app.route('/trending/<title>')
def trending_detail(title):
    # Pass the clicked trending topic to getResult
    processed_results, configure = getResult(trending_category=title)
    
    # Sort the processed_results by published date in descending order
    processed_results = getNewsSorted(processed_results)

    return render_template('trending_detail.html', 
                           trend=title,
                           processed_results=processed_results, 
                           configure=configure,
                           title=TRENDING_TITLE,
                           )


@app.route('/category/<category_name>')
def category_detail(category_name):
    # Use getResult function to get news articles for the selected category
    processed_results, configure = getResult(selected_category=category_name)

    # Sort the processed_results by published date in descending order
    processed_results = getNewsSorted(processed_results)

    return render_template('category_detail.html', 
                           processed_results=processed_results, 
                           configure=configure,
                           title=f"{category_name} - {CATEGORY_TITLE}",
                           )

@app.route('/about')
def about():
    return render_template('about.html', 
                           title=ABOUT_TITLE,
                           )
    
# Custom error handler for 404 Not Found
# Custom error handler for both 404 Not Found and 500 Internal Server Error
@app.errorhandler(404)
@app.errorhandler(500)
def error_handler(error):
    error_title = 'Error'
    if error.code == 404:
        error_title = '404 Not Found'
        error_message = ERROR_404
    else:
        error_message = ERROR_500

    return render_template('error.html', error_title=error_title, error_message=error_message , title=ERROR_TITLE), error.code

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
