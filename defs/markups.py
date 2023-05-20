
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

from defs.translation import _

# этот файл содержит в себе все клавиатуры проекта

def choose_lang(ref=''): # выбор языка

    langMenu = InlineKeyboardMarkup(row_width=2)

    langRu = InlineKeyboardButton(text='🇷🇺 Русский', callback_data=f'lang_ru {ref}')
    langEn = InlineKeyboardButton(text='🇬🇧 English', callback_data=f'lang_en {ref}')

    langMenu.insert(langRu)
    langMenu.insert(langEn)

    return langMenu

def MainMenu(lang): # главное меню
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    btnProfile = KeyboardButton('👤 '+_('Профиль', lang))
    btnSettings = KeyboardButton('⚙️ '+_('Настройки', lang))

    keyboard.add(btnProfile, btnSettings)
    return keyboard

def chooseStatus(status, lang): # выбор статуса

    if status is None:
        statusMenu = InlineKeyboardMarkup(row_width=2)

        organizer = InlineKeyboardButton(text='⚜️ '+_('Организатор', lang), callback_data=f'status_organizer')
        participant = InlineKeyboardButton(text='🃏 '+_('Участник', lang), callback_data=f'status_participant')

        statusMenu.insert(organizer)
        statusMenu.insert(participant)

        return statusMenu
    else:
        DeleteProfileMenu = InlineKeyboardMarkup()

        DeleteBtn = InlineKeyboardButton(text='❌ '+_('Удалить аккаунт', lang), callback_data='delete_account')

        DeleteProfileMenu.insert(DeleteBtn)

        return DeleteProfileMenu

def delete_account(lang): # удалить аккаунт
    DelProfileMenu = InlineKeyboardMarkup()

    DelBtn = InlineKeyboardButton(text='✅ '+_('Да', lang), callback_data='delet_acc_yes')
    DelBtn2 = InlineKeyboardButton(text='❌ '+_('Нет', lang), callback_data='delet_acc_no')

    DelProfileMenu.insert(DelBtn)
    DelProfileMenu.insert(DelBtn2)

    return DelProfileMenu