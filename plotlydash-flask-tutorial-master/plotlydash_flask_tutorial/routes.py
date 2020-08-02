"""Routes for parent Flask app."""
from flask import render_template, url_for, redirect, flash
from flask import current_app as app
from .forms import FeedbackForm
from pymongo import MongoClient
import pandas as pd

@app.route('/', methods=['POST', 'GET'])
def home():
    """Landing page."""
    form=FeedbackForm()
    #if form.validate_on_submit():
    if request.method == 'POST':
        client =  MongoClient("mongodb+srv://covid19Scraper:Covid-19@cluster0-rvjf8.mongodb.net/FlaskTable?retryWrites=true&w=majority")
        db = client.FlaskTable
        name = 'Feedback'
        collection = db[name]
        feedback = form.body
        feedBackRaw = {'FeedbackVal': [feedback]}
        dataFrame = pd.DataFrame(data=feedBackRaw)
        dataFrame.reset_index(inplace=True)
        data_dict = dataFrame.to_dict("records")
        collection.insert_many(data_dict)
        flash('We have received your feedback. Thank you!', "success")
        return redirect(url_for('home'))
    else:
        return render_template(
            'index.jinja2',
            title='COVID-19 Student Research Opportunities',
            description='This database is designed by students for students! Please use this searchable database to identify current opportunities for you to work on COVID-19 research and relief efforts at UT and beyond. Select the contact button to get in touch with the initiative leader. If you know of other opportunities or have feedback for us, please submit your ideas through the form at the bottom of the page. Thank you!',
            template='home-template',
            body="This is a homepage served with Flask.",
            form=form
        )
