from flask import Flask, render_template, request, redirect, url_for,flash, json
from string_literals import INDEX_TITLE,FEEDBACK_TITLE, SUCCESS_FEEDBACK_MESSAGE, SUCCESS, CHARACTERS_ERROR_MESSAGE, ERROR, FEEDBACK_FORM_VALIDATION_ERROR, ERROR_TITLE
from validate import is_valid_input, send_email
import secrets
from flask.helpers import get_flashed_messages 
from getNews import getResult, getNewsProcessed


app = Flask(__name__)
app.secret_key = secrets.token_hex(16)


@app.route('/', methods=['GET', 'POST'])
def index():

    processed_results,configure = getResult()
    # Sort the processed_results by published date in descending order
    processed_results = getNewsProcessed(processed_results)
    
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

# Custom error handler for 404 Not Found
# Custom error handler for both 404 Not Found and 500 Internal Server Error
@app.errorhandler(404)
@app.errorhandler(500)
def error_handler(error):
    error_title = 'Error'
    if error.code == 404:
        error_title = '404 Not Found'
        error_message = """
        The requested URL was not found on the server. 
        If you entered the URL manually, please check your spelling and try again.
        OR Just click on below button
        """
    else:
        error_message = """
        Oops! Something went wrong on our end. We\'re working to fix this issue. Please try again later.
        OR Just click on below button
        """

    return render_template('error.html', error_title=error_title, error_message=error_message , title=ERROR_TITLE), error.code

@app.route('/simulate_error')
def simulate_error():
    # Simulate a situation where an error occurs (e.g., division by zero)
    result = 1 / 0  # This will raise a ZeroDivisionError

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)