import emoji
import requests
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from telegram.ext import run_async, ConversationHandler
from django.conf import settings

from . import renderers, constants, models, pocket
from .authentication import authenticate


@run_async
def start(update, context):

    user = authenticate(update.message.chat)

    parts = update.message.text.split(' ')

    if parts.__len__() > 1:
        if parts[1] == 'callback':
            # Returning from authorized Pocket
            # Convert a request token into a Pocket access token

            response = requests.post(
                url='https://getpocket.com/v3/oauth/authorize',
                json={
                    'consumer_key': settings.POCKET_CONSUMER_KEY,
                    'code': user.pocket_request_token
                }
            )

            if response.status_code == 200:

                parts = str(response.text).split('&')

                access_token = str(parts[0]).split('=')[1]
                username = str(parts[1]).split('=')[1]
                username = str(username).replace('%40', '@')

                user.pocket_access_token = access_token
                user.pocket_username = username
                user.save()

                _, keyboard = renderers.main_markup(user)

                text = ''
                if user.language == 'en':
                    text = '✅ Connected to Pocket'
                elif user.language == 'es':
                    text = '✅ Conectado a Pocket'

                context.bot.send_message(
                    chat_id=user.chat_id,
                    text=text,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )

            else:

                pocket.get_request_token(user, context.bot.username)

                _, keyboard = renderers.main_markup(user)

                text = ''
                if user.language == 'en':
                    text = '⚠️ No fue posible conectar con Pocket. Autentícate en Pocket e inténtalo de nuevo.'
                elif user.language == 'es':
                    text = '⚠️ It was not possible to connect with Pocket. Login into pocket and try again.'

                context.bot.send_message(
                    chat_id=user.chat_id,
                    text=text,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )

    else:

        if user.pocket_request_token is None:
            pocket.get_request_token(user, context.bot.username)

        if update.message.chat.type == 'private':

            # Set language
            if user.language is None:
                text = 'Selecciona tu idioma | Select your language'
                keyboard = []
                keyboard.append(
                    [
                        InlineKeyboardButton(text=emoji.emojize(':Spain: Español'), callback_data='set_lang es start'),
                        InlineKeyboardButton(text=emoji.emojize(':England: English'), callback_data='set_lang en start'),
                    ]
                )

            # Main menu
            else:
                text, keyboard = renderers.main_markup(user)

            update.message.reply_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )


@run_async
def stats(update, context):

    user = authenticate(update.message.chat)

    text, keyboard = renderers.stats_markup(user)

    update.message.reply_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN_V2
    )


@run_async
def broadcast(update, context):

    user = authenticate(update.message.chat)

    if user.is_admin:

        if models.Broadcast.objects.filter(sent=False).count() == 0:
            models.Broadcast.objects.create()

        text, keyboard = renderers.broadcast_markup(user, context)

        update.message.reply_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


@run_async
def feedback(update, context):

    user = authenticate(update.message.chat)

    if user.is_admin:

        qs = models.Feedback.objects.all()
        for f in qs:
            context.bot.send_message(
                chat_id=user.chat_id,
                text='{user}\n\n{message}'.format(
                    user=f.bot_user,
                    message=f.message
                )
            )


@run_async
def admin(update, context):

    user = authenticate(update.message.chat)

    if user.is_admin:
        update.message.reply_text(
            text=(
                '/admin Ver este mensaje\n\n'
                '/feedback Ver mensajes de feedback\n\n'
                '/broadcast Enviar notificación masiva\n\n'
                '/users vacío (buscar) | all | connected\n\n'
                '/stats Ver estadísticas'
            )
        )


@run_async
def users(update, context):

    user = authenticate(update.message.chat)
    parts = str(update.message.text).split(' ')

    if user.is_admin:

        if parts.__len__() > 1:

            users = []

            if parts[1] == 'all':
                users = models.BotUser.objects.all()

            elif parts[1] == 'connected':
                users = models.BotUser.objects.all().exclude(pocket_access_token=None)

            elif parts[1] == 'gift':
                users = models.BotUser.objects.filter(gift_premium=True)

            if users.__len__() > 0:

                context.bot.send_message(
                    chat_id=user.chat_id,
                    text='{} resultados'.format(users.count()),
                )

                for u in users:
                    text, keyboard = renderers.user_markup(u)

                    context.bot.send_message(
                        chat_id=user.chat_id,
                        text=text,
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )

            else:

                context.bot.send_message(
                    chat_id=user.chat_id,
                    text='No hay resultados.',
                )

        else:

            update.message.chat.send_message(
                '¿Qué usuarios estás buscando?'
            )

            return constants.INPUT_USER_CRITERIA

    return ConversationHandler.END
