create_query = '''
drop table if exists users;
drop table if exists books;

CREATE TABLE IF NOT EXISTS public.books
(
    id serial PRIMARY KEY,
    name text,
    content jsonb
);

CREATE TABLE IF NOT EXISTS public.users
(
    user_id integer PRIMARY KEY,
    current_book integer,
    current_page integer,
    books integer[],
    book_marks jsonb,
	CONSTRAINT fkkey_users_current_book FOREIGN KEY (current_book) REFERENCES public.books (id)
);
'''