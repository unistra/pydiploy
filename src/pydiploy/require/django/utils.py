# -*- coding: utf-8 -*-

import random
import string
from fabric.api import env


def generate_secret_key():
    """
    Generate the django's secret key
    """

    letters = string.ascii_letters + string.punctuation.replace('\'', '')
    random_letters = map(lambda i: random.SystemRandom().choice(letters),
                         range(50))

    env.secret_key = ''.join(random_letters)
