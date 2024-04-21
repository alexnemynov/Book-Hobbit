import json
import os
import sys


BOOK_PATH = os.path.join(sys.path[0], os.path.normpath('book/book.txt'))
PAGE_SIZE = 1050

book: dict[int, str] = {}


# Функция, возвращающая строку с текстом страницы и ее размер
def _get_part_text(text: str, start: int, size: int) -> tuple[str, int]:
    splitters = ",.!:;?"
    end = min(start + size, len(text))
    page_text = text[start:end]
    for i in range(end, start, -1):
        try:
            before, current, after = text[i], text[i-1], text[i-2]
        except IndexError:
            before, current, after = ' ', text[i-1], text[i-2]
        if current in splitters:
            if (before in splitters) or (before and after in splitters):
                continue
            else:
                page_text = text[start:i]
                break
    return page_text, len(page_text)


# Функция, формирующая словарь книги
def prepare_book() -> None:
    with open(BOOK_PATH, 'r', encoding="utf-8") as file:
        text = file.read()
    start, page_num = 0, 1

    while start < len(text):
        page, page_len = _get_part_text(text, start, PAGE_SIZE)
        book[page_num] = page.lstrip()
        page_num += 1
        start += page_len

    with open(os.path.join(sys.path[0], os.path.normpath('book/book.json')), mode='w', encoding='utf-8') as f:
        json.dump(book, f)



# Вызов функции prepare_book для подготовки книги из текстового файла
# prepare_book()