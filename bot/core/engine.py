import telegram
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    Filters,
    PreCheckoutQueryHandler,
)
from django.conf import settings
from django.core.validators import URLValidator

from . import commands, callbacks, conversation, constants, messages, models


class Bot(object):

    command_handlers = {
        'start': commands.start,
        'stats': commands.stats,
        'broadcast': commands.broadcast,
        'feedback': commands.feedback,
        'admin': commands.admin
    }

    callback_query_handlers = {
        'main': callbacks.main,
        'help': callbacks.help,
        'donate': callbacks.donate,
        'stats': callbacks.stats,
        'set_lang': callbacks.set_lang,
        'lang': callbacks.lang,
        'disconnect_pocket': callbacks.disconnect_pocket,
    }

    conversation = {
        'entry_points': {
            'command_handlers': {
                'users': commands.users
            },
            'callback_query_handlers': {
                'feedback': conversation.feedback,
                'broadcast': conversation.broadcast,
                'md': conversation.direct_message,
                'confirm_md': conversation.send_direct_message,
                'cancel_md': conversation.cancel_direct_message,
            }
        },
        'states': {
            constants.INPUT_FEEDBACK: conversation.input_feedback,
            constants.INPUT_BROADCAST_MESSAGE: conversation.input_broadcast_message,
            constants.INPUT_DIRECT_MESSAGE: conversation.input_direct_message,
            constants.INPUT_USER_CRITERIA: conversation.input_user_criteria,
        }
    }

    def __init__(self):

        token = settings.TELEGRAM_TOKEN

        self.updater = Updater(token=token, use_context=True, workers=200)
        self.bot = telegram.Bot(token=token)

        # Notify admins
        for user in models.BotUser.objects.filter(is_admin=True):
            self.bot.send_message(chat_id=user.chat_id, text='🤖 Bot is running')

        dp = self.updater.dispatcher
        dp.add_error_handler(self.error_handler)

        # Init command handlers
        for key, value in self.command_handlers.items():
            dp.add_handler(CommandHandler(key, value))

        # Init callback query handlers
        for key, value in self.callback_query_handlers.items():
            dp.add_handler(CallbackQueryHandler(value, pattern=key))

        # Init conversation
        entry_points = []

        handlers = self.conversation['entry_points']['command_handlers']
        for key, value in handlers.items():
            entry_points.append(CommandHandler(key, value))

        handlers = self.conversation['entry_points']['callback_query_handlers']
        for key, value in handlers.items():
            entry_points.append(CallbackQueryHandler(value, pattern=key))

        states = {}
        handlers = self.conversation['states']
        for key, value in handlers.items():
            states[key] = [MessageHandler(Filters.text, value)]

        dp.add_handler(
            ConversationHandler(
                entry_points=entry_points,
                states=states,
                fallbacks=[]
            )
        )

        # Filter messages
        dp.add_handler(MessageHandler(Filters.regex(URLValidator.regex), messages.add_link))

    def error_handler(self, update, context):
        try:
            raise context.error
        except telegram.TelegramError as e:
            print(e.message)

    def start(self):
        self.updater.start_polling()
        print('[BOT] Running at https://t.me/{}'.format(self.bot.username))
        self.updater.idle()
