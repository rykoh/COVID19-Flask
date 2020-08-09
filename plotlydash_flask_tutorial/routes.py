"""Routes for parent Flask app."""
from flask import render_template
from flask import current_app as app


@app.route('/')
def home():
    """Landing page."""
    return render_template(
        'index.jinja2',
        title='COVID-19 Student Research Opportunities',
        description='This database is designed by students for students! Please use this searchable database to identify current opportunities for you to work on COVID-19 research and relief efforts at UT and beyond. Select the contact button to get in touch with the initiative leader. If you know of other opportunities or have feedback for us, please submit your ideas through the form at the bottom of the page. Thank you!',
        template='home-template',
        body="This is a homepage served with Flask."
    )
