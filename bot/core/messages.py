import requests
from emoji import emojize
from telegram import ChatAction
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from django.conf import settings

from .authentication import authenticate
from . import models


def add_link(update, context):

    if update.message.chat.type == 'private':

        url = update.message.text

        user = authenticate(update.message.chat)

        if user.pocket_access_token is None:

            connect_url = 'https://getpocket.com/auth/authorize?request_token={token}&redirect_uri={redirect}'.format(
                token=user.pocket_request_token,
                redirect=f'https://t.me/{context.bot.username}?start=callback'
            )

            text = ''
            connect_button = None

            if user.language == 'es':
                text = '🤖 Conecta to cuenta de Pocket para añadir enlaces desde Telegram.'
                connect_button = InlineKeyboardButton(text=emojize(':locked: Connect with Pocket'), url=connect_url)
            elif user.language == 'en':
                text = '🤖 Connect your Pocket account to add links from Telegram.'
                connect_button = InlineKeyboardButton(text=emojize(':locked: Conectar con Pocket'), url=connect_url)

            context.bot.send_message(
                chat_id=user.chat_id,
                text=text,
                reply_markup=InlineKeyboardMarkup([[connect_button]])
            )

        else:

            context.bot.send_chat_action(
                chat_id=user.chat_id,
                action=ChatAction.TYPING
            )

            response = requests.post(
                url='https://getpocket.com/v3/add',
                json={
                    'url': url,
                    'consumer_key': settings.POCKET_CONSUMER_KEY,
                    'access_token': user.pocket_access_token,
                }
            )

            if response.status_code == 200:

                text = ''
                if user.language == 'es':
                    text = '✅ Añadido a Pocket'
                elif user.language == 'en':
                    text = '✅ Saved to Pocket'

                stats = models.Stats.load()
                stats.saved += 1
                stats.save()

                context.bot.send_message(
                    chat_id=user.chat_id,
                    text=text
                )
