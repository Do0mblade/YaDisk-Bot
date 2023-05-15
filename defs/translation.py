
translation = {
    'en': {
        'Вы успешно зарегистрировались!': 'You have successfully registered!',
        'Вы уже зарегестрировались!': 'You have already registered!',
        'Добавлен новый пользователь': 'A new user has been added',
        'Профиль': 'Profile',
        'Настройки': 'Settings',
        'Язык был успешно обновлён!': 'The language has been successfully updated!',
        'Выберите язык': 'Select a language',
        'Выбранный язык уже установлен!': 'The selected language is already installed!',
        'Ваше имя': 'Your name',
        'Вас приглосил': 'Invited you',
        'Организатор': 'Organizer',
        'Участник': 'Participant',
        'Выберите ваш статус ниже': 'Select your status below',
        'Ваш статус был обновлён!': 'Your status has been updated!',
        'Удалить аккаунт': 'Delete Account',
        'Ваш статус': 'Your status',
        'Да': 'Yes',
        'Нет': 'No',
        'Ваш аккаунт был успешно удалён!': 'Your account has been successfully deleted!',
        'Ваша реферальная ссылка': 'Your referral link',
        'Ваш токен Яндекс': 'Your Yandex token',
        'Пожалуйста, напишите /token, чтобы получить инструкции по получению токена.': 'Please email /token to get instructions on how to get a token.',
        'Ваш токен был успешно загружен, можете приступать к работе.': 'Your token has been successfully loaded, you can get started.',
        'Вы ввели более 1 аргумента!': 'You have entered more than 1 argument!',
        'Пожалуйства введите команду /start': 'Please enter the command /start',
        'Для получения токена вам надо выполнить несколько несложных действий.\n\nНиже расписано всё по пунктам.': 'To get a token, you need to perform several simple actions.\n\n Everything is written down according to the points.',
        "1. Зайти на <a href='https://oauth.yandex.ru/client/new'>сайт</a> яндекса и создать приложение.\nНеобходимо придумать любое название для приложения, поставить галочку <b><u>Веб-сервисы</u></b> и вставить эту ссылку: <b><code>https://oauth.yandex.ru/verification_code</code></b>": "1. Go to <a href='https://oauth.yandex.ru/client/new'>yandex website</a> and create an application.\nit is necessary to come up with any name for the application, check the box <b><u>Web services</u></b> and insert this link: <b><code>https://oauth.yandex.ru/verification_code</code></b>",
        '2. Поставить разрешения как на скриншоте.': '2. Set the permissions as in the screenshot.',
        "3. Скопировать ваш <b><u>Client ID</u></b>, написать команду /client_id [ваш client id]\n\nНапример:\n<b>/client_id 80baa4fdjk4j54ff45gdba37</b>": "3. Copy your <b><u>Client ID</u></b>, write the command /client_id [your client id]\n\nexample:\n<b>/client_id 80baa4fdjk4j54ff45gdba37</b>",
        '4. Далее копируем ваш <b><u>Token</u></b> и отправляем боту при помощи команды /token [ваш token]\n\nНапример:\n<b>/token y0_AgAAAAAy60ZURNGEUIINM545NvFTICdggmle22U-cDkOwI</b>': '4. Next, copy your <b><u>Token</u></b> and send it to the bot using the command /token [your token]\n\nexample:\n<b>/token y0_AgAAAAAy60ZURNGEUIINM545NvFTICdggmle22U-cDkOwI</b>',
        'Этот токен уже установлен.': 'This token is already installed.',
        'Вы уверены, что хотите удалить аккаунт?': 'Are you sure you want to delete your account?',
        'Ваши рефералы': 'Your referrals',
        'Ваш токен не валиден, попробуйте отправить его снова или получить новый': 'Your token is not valid, try sending it again or getting a new one',
        'С вашим токеном всё в порядке!': 'Everything is fine with your token!',
        'Для начала ваш необходимо загрузить в бота токен!\n\nДля этого воспользуйтесь командой /token': 'Для начала ваш необходимо загрузить в бота токен!\n\nДля этого воспользуйтесь командой /token',
        'Путь к вашей папке <b><code>{}</code></b> был успешно загружен!': 'The path to your folder <b><code>{}</code></b> has been successfully uploaded!',
        'Неизвестная ошибка, попробуйте снова, если такое повторится, свяжитесь с администрацией.': 'Unknown error, try again, if this happens again, contact the administration.',
        'Ваша папка не найдена!': 'Your folder was not found!',
        'Вы уже добавляли эту папку!': 'You have already added this folder!',
        'Вы не можете воспользоваться данной командой, так как не являетесь организатором!': 'You cannot use this command because you are not the organizer!',
        'Вы не ввели путь к папке.': 'You have not entered the path to the folder.',
        'Данная папка больше не отслеживается': 'This folder is no longer tracked',
        'У вас пока нет отслеживаемых папок.': 'You don`t have any tracked folders yet.',
        'Вот все ваши папки:\n\n<b><code>{}</code></b>\n\nУдалить их можно введя команду <code>/del_folder [папка]</code>': 'Here are all your folders:\n\n<b><code>{}</code></b>\n\n You can delete them by entering the command <code>/del_folder [folder]</code>',
        'Укажите ваш client_id!': 'Specify your client_id!',
        '<a href="https://oauth.yandex.ru/authorize?response_type=token&client_id={}">Перейдите по ссылке</a>': '<a href="https://oauth.yandex.ru/authorize?response_type=token&client_id={}">Follow the link</a>',
        'Пользователь @{} добавил новый файл на свой Яндекс Диск.\nФайл: <a href="{}">{}</a>': 'User @{} added a new file to his Yandex Disk.\nFile: <a href="{}">{}</ a>'
    }
}

def _(text, lang='ru'):
    if lang == 'ru':
        return text
    else:
        global translation
        try:
            return translation[lang][text]
        except:
            return text