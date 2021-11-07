import os
import dotenv
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode, TelegramError
from telegram.ext import run_async
from . import renderers, models, authentication, pocket

from telegram import LabeledPrice
from emoji import emojize
from django.conf import settings


dotenv.load_dotenv()


@run_async
def main(update, context):
    query = update.callback_query
    query.answer()

    user = authentication.authenticate(update.effective_user)

    text, keyboard = renderers.main_markup(user)
    query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


@run_async
def help(update, context):
    query = update.callback_query
    query.answer()

    user = authentication.authenticate(update.effective_user)

    text, keyboard = renderers.help_markup(user)
    query.edit_message_text(
        text=emojize(text),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


@run_async
def donate(update, context):
    query = update.callback_query
    query.answer()

    user = authentication.authenticate(update.effective_user)

    text, keyboard = renderers.donate_markup(user)
    query.edit_message_text(
        text=emojize(text),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


@run_async
def lang(update, context):
    query = update.callback_query
    query.answer()

    user = authentication.authenticate(update.effective_user)

    text, keyboard = renderers.lang_markup(user)

    query.edit_message_text(
        text=emojize(text),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


@run_async
def set_lang(update, context):
    query = update.callback_query
    query.answer()

    user = authentication.authenticate(update.effective_user)

    params = query.data.split(' ')
    lang = params[1]
    origin = params[2]

    # Set lang
    user.language = lang
    user.save()

    if origin == 'settings':
        text, keyboard = renderers.lang_markup(user)
    else:
        text, keyboard = renderers.main_markup(user)

    query.edit_message_text(
        text=emojize(text),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


@run_async
def stats(update, context):
    query = update.callback_query
    query.answer()

    user = authentication.authenticate(update.effective_user)

    text, keyboard = renderers.stats_markup(user)

    query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN_V2
    )


@run_async
def disconnect_pocket(update, context):
    query = update.callback_query
    user = authentication.authenticate(update.effective_user)

    text = ''
    if user.language == 'es':
        text = '✅ Se desconectó tu cuenta de Pocket'
    elif user.language == 'en':
        text = '✅ Your Pocket account is disconnected'
    query.answer(text=text)

    # clean Pocket credentials
    user.pocket_request_token = None
    user.pocket_access_token = None
    user.pocket_username = None
    user.save()

    pocket.get_request_token(user)

    text, keyboard = renderers.main_markup(user)
    query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN_V2
    )
