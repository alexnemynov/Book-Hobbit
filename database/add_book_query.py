import os
import sys
import json
import logging


# Инициализируем логгер
logger = logging.getLogger(__name__)
logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

def content_str() -> str:
    from services.file_handling import prepare_book
    # Вызов функции prepare_book для подготовки книги из текстового файла
    prepare_book()
    logger.info('Book file .json created')

    # Преобразование
    with open(os.path.join(sys.path[0], os.path.normpath('book/book.json')), mode='r', encoding='utf-8') as f:
        content = json.load(f)
        logger.info('Book file .json loaded and ready to insert into database')
        return json.dumps(content)

add_book_query = 'INSERT INTO books (name, content) VALUES (%s, %s)'
values = ('📖 Tolkien J. R. R.: The Hobbit or There and Back Again', content_str())