import time
import emoji
from telegram import InlineKeyboardMarkup, ParseMode, InlineKeyboardButton
from telegram.ext import run_async, ConversationHandler
from telegram.error import TelegramError
from django.db.models import Q
from . import constants, authentication, renderers, models


def send_broadcast(admin, broadcast, context):

    bot = context.bot

    success = 0
    errors = 0

    for user in models.BotUser.objects.all():

        try:

            if user.language == 'es':
                bot.send_message(
                    chat_id=user.chat_id,
                    text=broadcast.text_es
                )

            elif user.language == 'en':
                bot.send_message(
                    chat_id=user.chat_id,
                    text=broadcast.text_en
                )

            success += 1
        except Exception as e:
            user.has_blocked_bot = True
            user.save()
            errors += 1

        time.sleep(1)

    broadcast.success = success
    broadcast.errors = errors
    broadcast.sent = True
    broadcast.save()

    bot.send_message(
        chat_id=admin.chat_id,
        text='Enviados: {}\nErrores: {}'.format(
            success,
            errors
        ),
    )


@run_async
def feedback(update, context):
    query = update.callback_query
    query.answer()

    user = authentication.authenticate(update.effective_user)

    text = ''

    if user.language == 'es':
        text = (
            '¿Deseas enviar tu opinión para ayudarme a mejorar el bot?'
            '\n\nPuedes reportar errores, solicitar nuevas funcionalidades o mejoras.\n\n'
            'Envíame tu opinión o ejecuta /cancel.'
        )

    elif user.language == 'en':
        text = (
            'Do you want to send me your feedback to help me improve the bot?'
            '\n\nYou can report bugs, request new features or improvements.\n\n'
            'Send your feedback or execute /cancel.'
        )

    query.edit_message_text(
        text=text
    )

    return constants.INPUT_FEEDBACK


@run_async
def input_feedback(update, context):

    bot = context.bot
    message = update.message.text
    user = authentication.authenticate(update.effective_user)

    _, keyboard = renderers.main_markup(user)

    if str(message).lower() == '/cancel':

        if user.language == 'es':
            update.message.chat.send_message(
                text='✅ Se canceló la acción que estabas llevando a cabo.',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        elif user.language == 'en':
            update.message.chat.send_message(
                text='✅ The action has been canceled.',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

    else:

        name = user.first_name
        if user.last_name is not None:
            name += ' ' + user.last_name
        if user.username is not None:
            name += '(@{})'.format(user.username)

        text = (
            '💬 Feedback from {name}:'
            '\n\n{message}'.format(
                name=name,
                message=message
            )
        )

        # persist feedback
        models.Feedback.objects.create(
            bot_user=user,
            message=message
        )

        # send feedback to admins
        admins = models.BotUser.objects.filter(is_admin=True)
        for admin in admins:
            bot.send_message(
                chat_id=admin.chat_id,
                text=text
            )

        # thanks
        text = ''
        if user.language == 'es':
            text = 'Muchas gracias por tu opinión.'
        elif user.language == 'en':
            text = 'Thank you for your feedback.'

        bot.send_message(
            chat_id=user.chat_id,
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    return ConversationHandler.END


@run_async
def input_broadcast_message(update, context):
    message = update.message.text

    bot = context.bot

    user = authentication.authenticate(update.effective_user)

    try:

        broadcast = models.Broadcast.objects.get(sent=False)

        if broadcast.setting_lang == 'es':
            broadcast.text_es = message
        elif broadcast.setting_lang == 'en':
            broadcast.text_en = message

        broadcast.setting_lang = None
        broadcast.save()

        text, keyboard = renderers.broadcast_markup(user, context)

        bot.send_message(
            chat_id=user.chat_id,
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        return ConversationHandler.END

    except models.Notification.DoesNotExist:

        return ConversationHandler.END


@run_async
def input_direct_message(update, context):

    bot = context.bot
    message = update.message.text
    user = authentication.authenticate(update.effective_user)

    if user.is_admin:

        context.user_data['md_text'] = message

        bot.send_message(
            chat_id=user.chat_id,
            text=message,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(text='Enviar', callback_data='confirm_md')],
                [InlineKeyboardButton(text='Cancelar', callback_data='cancel_md')],
            ])
        )

        return ConversationHandler.END


@run_async
def broadcast(update, context):
    query = update.callback_query
    query.answer()

    user = authentication.authenticate(update.effective_user)

    params = query.data.split(' ')
    operation = params[1]
    value = None

    if params.__len__() > 2:
        value = params[2]

    try:

        broad = models.Broadcast.objects.get(sent=False)

        if operation == 'lang':

            broad.setting_lang = value
            broad.save()

            query.edit_message_text(
                text='Envíame el mensaje en idioma "{}"'.format(value)
            )

            return constants.INPUT_BROADCAST_MESSAGE

        if operation == 'send':

            send_broadcast(
                admin=user,
                broadcast=broad,
                context=context
            )

            return ConversationHandler.END

    except models.Broadcast.DoesNotExist:

        query.edit_message_text(
            text='No hay ninguna notificación en curso, comienza una nueva.'
        )

        return ConversationHandler.END


@run_async
def direct_message(update, context):
    query = update.callback_query
    query.answer()

    user = authentication.authenticate(update.effective_user)

    params = query.data.split(' ')
    id = params[1]

    if user.is_admin:
        context.user_data['md_id'] = id
        context.bot.send_message(
            chat_id=user.chat_id,
            text='🤖 Escribe el mensaje para enviar al usuario.'
        )
        return constants.INPUT_DIRECT_MESSAGE


@run_async
def send_direct_message(update, context):
    query = update.callback_query
    query.answer()

    user = authentication.authenticate(update.effective_user)

    if user.is_admin:

        bot = context.bot

        id = context.user_data.get('md_id')
        text = context.user_data.get('md_text')

        try:
            destiny_user = models.BotUser.objects.get(pk=id)
            try:
                bot.send_message(
                    chat_id=destiny_user.chat_id,
                    text=text
                )
                query.edit_message_text(
                    text='✅ Mensaje enviado.'
                )
                destiny_user.has_blocked_bot = False
                destiny_user.save()
            except:
                destiny_user.has_blocked_bot = True
                destiny_user.save()
                bot.send_message(
                    chat_id=user.chat_id,
                    text='⚠️ No fue posible enviar el mensaje.'
                )
        except models.BotUser.DoesNotExist:
            pass

        del context.user_data['md_id']
        del context.user_data['md_text']


@run_async
def cancel_direct_message(update, context):
    query = update.callback_query
    query.answer()

    user = authentication.authenticate(update.effective_user)

    if user.is_admin:

        bot = context.bot
        query.edit_message_text(
            text='✅ Envío cancelado.'
        )

        del context.user_data['md_id']
        del context.user_data['md_text']


@run_async
def input_user_criteria(update, context):

    bot = context.bot
    message = update.message.text
    user = authentication.authenticate(update.effective_user)

    if user.is_admin:

        criteria = message

        users = models.BotUser.objects.filter(
            Q(username__icontains=criteria) |
            Q(first_name__icontains=criteria) |
            Q(last_name__icontains=criteria)
        )

        bot.send_message(
            chat_id=user.chat_id,
            text='{} resultados'.format(users.count()),
        )

        for u in users:

            text, keyboard = renderers.user_markup(u)

            bot.send_message(
                chat_id=user.chat_id,
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

    return ConversationHandler.END
