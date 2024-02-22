from flask import Flask, render_template, request, redirect, url_for,flash,jsonify,render_template_string
from string_literals import INDEX_TITLE,FEEDBACK_TITLE
from validate import send_email
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
        feedback_name = request.form['name'][:50]
        feedback_text = request.form['feedback'][:250]
        send_email(feedback_name,feedback_text)

        # Use the 'success' category for the flash message
        flash('Your Feedback is our motivation towards improvement', 'success')

        return redirect(url_for('index'))

    return render_template('feedback.html', title=FEEDBACK_TITLE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)