from copy import deepcopy

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message
from database.database import bot_database as db
from filters.filters import IsDelBookmarkCallbackData, IsDigitCallbackData
from keyboards.bookmarks_kb import (create_bookmarks_keyboard,
                                    create_edit_keyboard)
from keyboards.pagination_kb import create_pagination_keyboard
from lexicon.lexicon import LEXICON
from services.file_handling import prepare_book


router = Router()


# Этот хэндлер будет срабатывать на команду "/start" -
# добавлять пользователя в базу данных, если его там еще не было
# и отправлять ему приветственное сообщение
@router.message(CommandStart())
async def process_start_command(message: Message):
    db.user_interface.create_if_not_exists(
        user_id=message.from_user.id,
        current_page=1,
        current_book=1,
        books=[1],
        book_marks={}
    )
    prepare_book()
    await message.answer(LEXICON[message.text])


# Этот хэндлер будет срабатывать на команду "/help"
# и отправлять пользователю сообщение со списком доступных команд в боте
@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(LEXICON[message.text])


# Этот хэндлер будет срабатывать на команду "/beginning"
# и отправлять пользователю первую страницу книги с кнопками пагинации
@router.message(Command(commands='beginning'))
async def process_beginning_command(message: Message):
    user_book = db.user_interface.get_current_book(message.from_user.id)
    db.user_interface.set_current_page(message.from_user.id, 1)
    user_page = db.user_interface.get_current_page(message.from_user.id)
    text = db.book_interface.get_page_content(user_book, 1)
    book_length = db.book_interface.get_length(user_book)
    await message.answer(
        text=text,
        reply_markup=create_pagination_keyboard(
            'backward',
            f'{user_page}/{book_length}',
            'forward'
        )
    )


# Этот хэндлер будет срабатывать на команду "/continue"
# и отправлять пользователю страницу книги, на которой пользователь
# остановился в процессе взаимодействия с ботом
@router.message(Command(commands='continue'))
async def process_continue_command(message: Message):
    user_book = db.user_interface.get_current_book(message.from_user.id)
    user_page = db.user_interface.get_current_page(message.from_user.id)
    text = db.book_interface.get_page_content(user_book, user_page)
    book_length = db.book_interface.get_length(user_book)
    await message.answer(
        text=text,
        reply_markup=create_pagination_keyboard('backward', f'{user_page}/{book_length}', 'forward')
    )


# Этот хэндлер будет срабатывать на команду "/bookmarks"
# и отправлять пользователю список сохраненных закладок,
# если они есть или сообщение о том, что закладок нет
@router.message(Command(commands='bookmarks'))
async def process_bookmarks_command(message: Message):
    user_book = db.user_interface.get_current_book(message.from_user.id)
    book_marks = db.user_interface.get_book_marks(message.from_user.id)
    if book_marks:
        await message.answer(
            text=LEXICON[message.text],
            reply_markup=create_bookmarks_keyboard(*book_marks[user_book])
        )
    else:
        await message.answer(text=LEXICON['no_bookmarks'])


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки "вперед"
# во время взаимодействия пользователя с сообщением-книгой
@router.callback_query(F.data == 'forward')
async def process_forward_press(callback: CallbackQuery):
    user_page = db.user_interface.get_current_page(callback.from_user.id)
    user_book = db.user_interface.get_current_book(callback.from_user.id)
    book_length = db.book_interface.get_length(user_book)
    if user_page < book_length:
        next_page = user_page + 1
        db.user_interface.set_current_page(callback.from_user.id, next_page)
        text = db.book_interface.get_page_content(user_book, next_page)

        await callback.message.edit_text(
            text=text,
            reply_markup=create_pagination_keyboard('backward', f'{next_page}/{book_length}', 'forward')
        )
    else:
        await callback.answer()


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки "назад"
# во время взаимодействия пользователя с сообщением-книгой
@router.callback_query(F.data == 'backward')
async def process_backward_press(callback: CallbackQuery):
    user_page = db.user_interface.get_current_page(callback.from_user.id)
    user_book = db.user_interface.get_current_book(callback.from_user.id)
    book_length = db.book_interface.get_length(user_book)

    if user_page > 1:
        next_page = user_page - 1
        db.user_interface.set_current_page(callback.from_user.id, next_page)
        text = db.book_interface.get_page_content(user_book, next_page)

        await callback.message.edit_text(
            text=text,
            reply_markup=create_pagination_keyboard('backward', f'{next_page}/{book_length}', 'forward')
        )
    else:
        await callback.answer()


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки
# с номером текущей страницы и добавлять текущую страницу в закладки
@router.callback_query(lambda x: '/' in x.data and x.data.replace('/', '').isdigit())
async def process_page_press(callback: CallbackQuery):
    user_page = db.user_interface.get_current_page(callback.from_user.id)
    user_book = db.user_interface.get_current_book(callback.from_user.id)
    db.user_interface.add_book_mark(callback.from_user.id, user_book, user_page)
    await callback.answer(f'Страница {user_page} добавлена в закладки!')


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки
# с закладкой из списка закладок
@router.callback_query(IsDigitCallbackData())
async def process_bookmark_press(callback: CallbackQuery):
    user_book = db.user_interface.get_current_book(callback.from_user.id)
    page = int(callback.data)
    text = db.book_interface.get_page_content(user_book, page)
    book_length = db.book_interface.get_length(user_book)
    await callback.message.edit_text(
        text=text,
        reply_markup=create_pagination_keyboard('backward', f'{page}/{book_length}', 'forward')
    )


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки
# "редактировать" под списком закладок
@router.callback_query(F.data == 'edit_bookmarks')
async def process_edit_press(callback: CallbackQuery):
    user_book = db.user_interface.get_current_book(callback.from_user.id)
    book_marks = db.user_interface.get_book_marks(callback.from_user.id)
    await callback.message.edit_text(
        text=LEXICON[callback.data],
        reply_markup=create_edit_keyboard(
            *book_marks[user_book]
        )
    )


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки
# "отменить" во время работы со списком закладок (просмотр и редактирование)
@router.callback_query(F.data == 'cancel')
async def process_cancel_press(callback: CallbackQuery):
    await callback.message.edit_text(text=LEXICON['cancel_text'])


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки
# с закладкой из списка закладок к удалению
@router.callback_query(IsDelBookmarkCallbackData())
async def process_del_bookmark_press(callback: CallbackQuery):
    user_book = db.user_interface.get_current_book(callback.from_user.id)
    db.user_interface.remove_book_mark(callback.from_user.id, user_book, int(callback.data[:-3]))
    book_marks = db.user_interface.get_book_marks(callback.from_user.id)
    if book_marks:
        await callback.message.edit_text(
            text=LEXICON['edit_bookmarks'],
            reply_markup=create_edit_keyboard(
                *book_marks[user_book]
            )
        )
    else:
        await callback.message.edit_text(text=LEXICON['no_bookmarks'])