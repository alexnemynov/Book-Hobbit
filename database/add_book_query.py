import os
import sys
import json


with open(os.path.join(sys.path[0], os.path.normpath('book/book.json')), mode='r', encoding='utf-8') as f:
    content = json.load(f)
    content_str = json.dumps(content)

add_book_query = 'INSERT INTO books (name, content) VALUES (%s, %s)'
values = ('📖 Tolkien J. R. R.: The Hobbit or There and Back Again', content_str)