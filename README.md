<p align="center">
      <img src="https://cdn.icon-icons.com/icons2/1381/PNG/512/yandexdisk_94467.png" width="250">
</p>

<p align="center">
   <img src="https://img.shields.io/badge/Version-v1.6 (Alpha)-blue" alt="Version">
   <img src="https://img.shields.io/badge/License-MIT-green" alt="License">
</p>

## О проекте

Проектом является Telegram бот, который умеет периодически проверять Яндекс Диск Организатора на новые файлы. Так же есть возможность отсылать Участникам, данного Организатора, сообщения о новом файле на диске и предоставлении ссылки на его скачивание.

## Документация

### Начало работы

В файл **config/bot.py** необходимо в переменную **TOKEN** вписать ваш токен бота
```python
TOKEN = '<Your Token Bot>' # Токен вашего бота
```

Токен бота можно получить в [BotFather](https://t.me/BotFather)

- Организатор - ответственный за выгрузку файлов на диск ( реферер )
- Участник - получает сообщения о новых файлах ( реферал )

#### Нужные пакеты
```python
aiogram
sqlite3
```

### Команды бота

- /start - начало работы с ботом
- /me - профиль
- /add_folder - добавить папку для отслеживания ( Организатор )
- /del_folder - удалить папку из отслеживаемых ( Организатор )
- /folders - посмотреть все отслеживаемые папки ( Организатор )
- /token - инструкция по получению Яндекс токена для работы я диском ( Организатор )
- /check - проверка на валидность токена ( Организатор )
- /client_id - выдаёт ссылку, по которой вы получаете Яндекс токен ( Организатор ) ( расширенная информация /token )

## Разработчики

- [Do0mblade](https://github.com/Do0mblade)

## Лицензия
Проект YaDisk-Bot распространяется под лицензией MIT
