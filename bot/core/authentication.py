from . import models


def authenticate(chat):
    user, _ = models.BotUser.objects.get_or_create(chat_id=chat['id'])

    user.chat_id = chat['id']

    # get username
    try:
        user.username = chat.username
    except Exception as e:
        user.username = None

    # get first name
    try:
        user.first_name = chat.first_name
    except Exception as e:
        user.first_name = None

    # get last name
    try:
        user.last_name = chat.last_name
    except Exception as e:
        user.last_name = None

    user.report_last_action()
    user.save()

    return user
