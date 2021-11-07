import requests
from django.conf import settings


def get_request_token(user):
    response = requests.post(
        url='https://getpocket.com/v3/oauth/request',
        json={
            'consumer_key': settings.POCKET_CONSUMER_KEY,
            'redirect_uri': 'https://t.me/ToReadingListBot?start='
        },
    )

    token = str(response.text).split('=')[1]
    user.pocket_request_token = token
    user.save()
