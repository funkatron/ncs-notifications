# a sample config file. rename to config.py


class Config(object):
    DEBUG = True

    ##
    # make this something CRAY CRAY like:
    # >>> import os
    # >>> os.urandom(36)
    ##
    SECRET_KEY = "this is a secret"

    AUTH_USERNAME = "A_USERNAME"
    AUTH_PASSWORD = "A_COMPLEX_PASSWORD"  # yes, this is plain text.

    PM_API_KEY = 'MAILCHIMP_KEY'
    PM_TEST_LIST_ID = u'MAILCHIMP_TEST_LIST_ID'
    PM_LIST_ID = u'MAILCHIMP_LIST_ID'
    MD_API_KEY = 'MANDRILL_KEY'

    DEFAULT_FROM_EMAIL = 'postmaster@from.domain'
    DEFAULT_FROM_NAME = 'Postmaster'
