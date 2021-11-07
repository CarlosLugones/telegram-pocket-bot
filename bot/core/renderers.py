from emoji import emojize
from telegram import InlineKeyboardButton

from . import models


def render_boolean_button(name, value):
    text = name
    if value:
        text = ':check_mark_button: ' + text
    else:
        text = ':black_square_button: ' + text
    return emojize(text)


def main_markup(user):

    text = ''
    keyboard = []

    connect_url = 'https://getpocket.com/auth/authorize?request_token={token}&redirect_uri={redirect}'.format(
        token=user.pocket_request_token,
        redirect='https://t.me/ToReadingListBot?start=callback'
    )

    if user.language == 'en':
        text = 'Welcome, {first_name}'.format(first_name=user.first_name)

        keyboard = [
            [
                InlineKeyboardButton(text=emojize(':rainbow_flag: Language'), callback_data='lang'),
                InlineKeyboardButton(text=emojize(':red_question_mark: Help'), callback_data='help')
            ],
            [
                InlineKeyboardButton(text=emojize(':bar_chart: Stats'), callback_data='stats'),
                InlineKeyboardButton(text=emojize(':megaphone: Channel'), url='https://t.me/LugodevBots'),
            ],
            [
                InlineKeyboardButton(text=emojize(':credit_card: Donate'), callback_data='donate'),
                InlineKeyboardButton(text=emojize(':star: Rate bot'), url='https://t.me/BotsArchive/2046')
            ]
        ]

        connect_button = None

        if user.pocket_access_token is None:
            connect_button = InlineKeyboardButton(text=emojize(':locked: Connect with Pocket'), url=connect_url)
        else:
            connect_button = InlineKeyboardButton(text=emojize('❌ Disconnect Pocket'), callback_data='disconnect_pocket')

        keyboard.insert(0, [connect_button])

    elif user.language == 'es':
        text = 'Bienvenido, {first_name}'.format(first_name=user.first_name)
        keyboard = [
            [
                InlineKeyboardButton(text=emojize(':rainbow_flag: Idioma'), callback_data='lang'),
                InlineKeyboardButton(text=emojize(':red_question_mark: Ayuda'), callback_data='help')
            ],
            [
                InlineKeyboardButton(text=emojize(':bar_chart: Estadísticas'), callback_data='stats'),
                InlineKeyboardButton(text=emojize(':megaphone: Canal'), url='https://t.me/LugodevBots'),
            ],
            [
                InlineKeyboardButton(text=emojize(':credit_card: Donar'), callback_data='donate'),
                InlineKeyboardButton(text=emojize(':star: Calificar bot'), url='https://t.me/BotsArchive/2046')
            ]
        ]

        connect_button = None

        if user.pocket_access_token is None:
            connect_button = InlineKeyboardButton(text=emojize(':locked: Conectar con Pocket'), url=connect_url)
        else:
            connect_button = InlineKeyboardButton(text=emojize('❌ Desconectar Pocket'), callback_data='disconnect_pocket')

        keyboard.insert(0, [connect_button])

    return text, keyboard


def help_markup(user):

    text = ''
    keyboard = []

    if user.language == 'en':

        text = ':red_question_mark: Help'
        keyboard = [
            [
                InlineKeyboardButton(text=emojize(':information: Tutorial'), url='https://telegra.ph/Reading-List-Bot---Tutorial-05-12'),
                InlineKeyboardButton(text=emojize(':information: Changelog'), url='https://telegra.ph/Reading-List-Bot---Changelog-05-12')
            ],
            [InlineKeyboardButton(text=emojize(':information: Use Terms & Privacy Policy'), url='https://telegra.ph/Reading-List-Bot---Use-Terms-and-Privacy-Policy-05-12')],
            [InlineKeyboardButton(text=emojize(':speech_balloon: Send feedback'), callback_data='feedback')],
            [InlineKeyboardButton(text=emojize(':speech_balloon: Live support'), url='https://t.me/LugodevSupportBot')],
            [InlineKeyboardButton(text=emojize(':left_arrow: Go back'), callback_data='main')]
        ]

    elif user.language == 'es':

        text = ':red_question_mark: Ayuda'
        keyboard = [
            [
                InlineKeyboardButton(text=emojize(':information: Tutorial'), url='https://telegra.ph/Reading-List-Bot---Tutorial-05-12'),
                InlineKeyboardButton(text=emojize(':information: Versiones'), url='https://telegra.ph/Reading-List-Bot---Changelog-05-12')
            ],
            [InlineKeyboardButton(text=emojize(':information: Términos y Privacidad'), url='https://telegra.ph/Reading-List-Bot---Use-Terms-and-Privacy-Policy-05-12')],
            [InlineKeyboardButton(text=emojize(':speech_balloon: Enviar opinión'), callback_data='feedback')],
            [InlineKeyboardButton(text=emojize(':speech_balloon: Soporte'), url='https://t.me/LugodevSupportBot')],
            [InlineKeyboardButton(text=emojize(':left_arrow: Regresar'), callback_data='main')]
        ]

    return text, keyboard


def donate_markup(user):

    text = ''
    keyboard = []

    if user.language == 'en':

        text = (
            'This bot is provided as a free service, but it costs me money to run it.\n\n'
            'If you\'d like to support my work, consider donating.\n\n'
            'You can do so via my Ko-Fi profile, using a credit/debit card or PayPal.'
        )
        keyboard = [
            [InlineKeyboardButton(text=emojize(':credit_card: Make a donation'), url='https://ko-fi.com/lugodev')],
            [InlineKeyboardButton(text=emojize(':left_arrow: Go back'), callback_data='main')],
        ]

    elif user.language == 'es':

        text = (
            'Este bot se provee como un servicio gratuito, pero me cuesta dinero mantenerlo y ejecutarlo.\n\n'
            'Si deseas apoyar mi trabajo, considera realizar una donación.\n\n'
            'Puedes hacerlo por medio de mi perfil de Ko-Fi, usando una tarjeta de crédito/débito o PayPal.'
        )
        keyboard = [
            [InlineKeyboardButton(text=emojize(':credit_card: Realizar una donación'), url='https://ko-fi.com/lugodev')],
            [InlineKeyboardButton(text=emojize(':left_arrow: Regresar'), callback_data='main')],
        ]

    return text, keyboard


def lang_markup(user):

    text = ''

    keyboard = [
        [
            InlineKeyboardButton(
                text=render_boolean_button(emojize(':Spain: Español'), user.language == 'es'),
                callback_data='set_lang es settings'
            ),
            InlineKeyboardButton(
                text=render_boolean_button(emojize(':England: English'), user.language == 'en'),
                callback_data='set_lang en settings'
            ),
        ],
    ]

    if user.language == 'es':
        text = ':rainbow_flag: Idioma'
        keyboard.append([InlineKeyboardButton(text=emojize(':left_arrow: Regresar'), callback_data='main')])

    elif user.language == 'en':
        text = ':rainbow_flag: Language'
        keyboard.append([InlineKeyboardButton(text=emojize(':left_arrow: Go back'), callback_data='main')])

    return text, keyboard


def stats_markup(user):

    stats = models.Stats.load()
    users = models.BotUser.objects.all().count()

    keyboard = []
    text = ''

    if user.language == 'es':

        text += (
            f'*Usuarios:* `{users}`\n'
            f'*Enlaces guardados*: `{stats.saved}`'
        )

        # go back
        keyboard.append(
            [InlineKeyboardButton(text=emojize(':left_arrow: Regresar'), callback_data='main')]
        )

    elif user.language == 'en':

        text += (
            f'*Users:* `{users}`\n'
            f'*Links saved*: `{stats.saved}`'
        )

        # go back
        keyboard.append(
            [InlineKeyboardButton(text=emojize(':left_arrow: Go back'), callback_data='main')]
        )

    return text, keyboard


def broadcast_markup(user, context):

    keyboard = []

    text = 'Especifica el texto del broadcast para cada lenguaje'

    keyboard.append([
        InlineKeyboardButton(text='🇪🇸 Español', callback_data='broadcast lang es'),
        InlineKeyboardButton(text='🇻🇬 English', callback_data='broadcast lang en'),
    ])

    keyboard.append([
        InlineKeyboardButton(text='📤 Enviar', callback_data='broadcast send'),
    ])

    return text, keyboard


def user_markup(user):

    text = ''
    keyboard = []

    text = (
        f'Nombre: {user.first_name}\n'
        f'Apellidos: {user.last_name}\n'
        f'Username: {user.username}\n'        
        f'Última acción: {str(user.last_action_datetime)}\n'
        f'Idioma: {user.language}\n'
        f'Accepted TOS: {user.accepted_tos}\n'
        f'Pocket username: {user.pocket_username}'
    )

    keyboard = [
        [
            InlineKeyboardButton(
                text='📩 Mensaje directo',
                callback_data='md {id}'.format(id=user.id)
            )
        ]
    ]

    return text, keyboard
