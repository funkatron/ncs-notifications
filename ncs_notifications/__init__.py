from flask import Flask, request, render_template, flash, redirect, url_for
from postmonkey import PostMonkey
from mandrill import Mandrill
from pprint import pformat
import datetime
import pytz
from .basic_auth import requires_auth

app = Flask(__name__)

# Configuration
app.config.from_object('settings.config.Config')


# handlers
@app.route('/')
@requires_auth
def home():

    return render_template('post_form.html',
                           page_title="E-Mail Post Form",
                           default_from_name=app.config["DEFAULT_FROM_NAME"],
                           default_from_email=app.config["DEFAULT_FROM_EMAIL"])


@app.route('/edit', methods=['POST'])
@requires_auth
def edit():

    app.logger.debug(request.form)

    # get form data (WE SHOULD VALIDATE)
    msg_text = request.form.get('message')
    subject = request.form.get('subject')
    from_email = request.form.get('from_email')
    from_name = request.form.get('from_name')
    test_list = request.form.get('test_list', None)

    return render_template('post_form.html',
                           page_title="E-Mail Post Form",
                           default_from_name=from_name,
                           default_from_email=from_email,
                           subject=subject,
                           message=msg_text,
                           test_list=test_list)


@app.route('/review', methods=['POST'])
@requires_auth
def review():

    app.logger.debug(request.form)

    # get form data (WE SHOULD VALIDATE)
    message = request.form.get('message')
    subject = request.form.get('subject')
    from_email = request.form.get('from_email')
    from_name = request.form.get('from_name')
    test_list = request.form.get('test_list', None)

    app.logger.debug(from_email)
    app.logger.debug(from_name)

    if (test_list):
        list_id = app.config['PM_TEST_LIST_ID']
    else:
        list_id = app.config['PM_LIST_ID']

    pm = PostMonkey(app.config['PM_API_KEY'])
    list_info = pm.lists(filters={'list_id': list_id})
    list_name = list_info['data'][0]['name']
    list_count = list_info['data'][0]['stats']['member_count']

    return render_template('review_form.html',
                           page_title="Review E-mail",
                           from_name=from_name,
                           from_email=from_email,
                           list_name=list_name,
                           list_count=list_count,
                           test_list=test_list,
                           message=message,
                           subject=subject)


@app.route('/send', methods=['POST'])
def send():
    """
    sends emails to a configured MailChimp list
    """

    # get form data (WE SHOULD VALIDATE)
    msg_text = request.form.get('message')
    subject = request.form.get('subject')
    from_email = request.form.get('from_email')
    from_name = request.form.get('from_name')
    test_list = request.form.get('test_list', None)

    if (test_list):
        list_id = app.config['PM_TEST_LIST_ID']
        app.logger.debug("sending to test list %s" % (list_id))
    else:
        list_id = app.config['PM_LIST_ID']
        app.logger.debug("sending to LIVE list %s" % (list_id))

    pm = PostMonkey(app.config['PM_API_KEY'])
    md = Mandrill(app.config['MD_API_KEY'])

    members = pm.listMembers(id=list_id, limit=1000)
    emails = []

    for mem in members['data']:
        emails.append(mem['email'])

    eastern = pytz.timezone('US/Eastern')
    now = eastern.localize(datetime.datetime.now())
    msg_text = "%s\n\n--------\n\nE-mail generated at %s" % (msg_text, now)

    for email in emails:
        message = {
            "text": msg_text,
            "subject": subject,
            "from_email": from_email,
            "from_name": from_name,
            "to": [{
                "email": email
            }]
        }

        app.logger.debug("sending to %s at %s" % (email, now))

        resp = md.messages.send(message, async=True)

        app.logger.debug(pformat(resp))

    flash("%s e-mails sent!" % len(emails))

    return redirect(url_for('home'))
