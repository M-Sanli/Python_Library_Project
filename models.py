"""
A module to create DB models using peewee.
See http://docs.peewee-orm.com/en/latest/peewee/
"""
import csv
import datetime
import os

from peewee import BooleanField, CharField, DateField, ForeignKeyField, Model, SmallIntegerField, SqliteDatabase, FloatField, ManyToManyField

from constants import DB_PATH, ALLOWED_BORROW_DAYS

# The Sqlite DB instance
db = SqliteDatabase(DB_PATH)  # type: SqliteDatabase


class User(Model):
    """
    A class to represent a User.

    The login is the email.

    The password should be hashed for security reasons but won't be.
    See https://culttt.com/2013/01/21/why-do-you-need-to-salt-and-hash-passwords/

    A user can be an admin or not.

    """
    # The email will be the user's login name
    email = CharField(unique=True)
    first_name = CharField()
    last_name = CharField()
    password = CharField()
    # These two fields, logged_in and last_seen
    # are required to securely log in a user as seen in 08_Web_Apps_with_Python
    logged_in = BooleanField(default=False)
    last_seen = SmallIntegerField(null=True)
    is_admin = BooleanField(default=False)

    class Meta:
        """
        Class to define some meta attributes for the model.

        See http://docs.peewee-orm.com/en/latest/peewee/quickstart.html#model-definition
        """
        database = db

class Author(Model):
    """
    A class to represent an author.

    We could simply use a CharField on Book but if we want to add extra features
    (e.g. search all books from authors of the 18th century), it's better to have
    it as a model.
    """
    # We should probably split this into first name/last name, but since we're going
    # to generate initial data from a CSV found online that doesn't distinguish between
    # first name and last name, it's easier to just put a name in there.
    name = CharField(index=True)

    class Meta:
        """
        Class to define some meta attributes for the model.

        See http://docs.peewee-orm.com/en/latest/peewee/quickstart.html#model-definition
        """
        database = db


class Book(Model):
    title = CharField(unique=True)
    # A book can have many authors, and an author can be an author of many books
    # We use a ManyToManyField. When using ManyToManyFields, there is an intermediary
    # table created in SQLite, which has two fields: an author_id and a book_id. This
    # is how many to many relationships can be modelled.
    # In create_tables, we explicitly create this intermediary function
    authors = ManyToManyField(Author, backref="books")
    publication_year = SmallIntegerField()
    # The max rating is 5
    average_rating = FloatField(null=True)
    # The number of ratings or "votes" for the book
    ratings_count = SmallIntegerField(default=0)
    image_url = CharField()
    # If borrowed_by is empty (allowed by null=True), it means the book is available
    borrowed_by = ForeignKeyField(User, null=True, backref="borrowed_books")
    borrowed_at = DateField(null=True)

    class Meta:
        """
        Class to define some meta attributes for the model.

        See http://docs.peewee-orm.com/en/latest/peewee/quickstart.html#model-definition
        """
        database = db

    def return_date(self):
        """
        Return the return date of the book.

        If the book is not borrowed, return today's date
        If the book is borrowed, return the date it was borrowed + ALLOWED_BORROWED_DAYS
        """
        if not self.borrowed_at:
            return datetime.date.today()
        else:
            return self.borrowed_at + datetime.timedelta(days=ALLOWED_BORROW_DAYS)


def create_tables():
    """
    The recommended way by Peewee to create tables.

    See http://docs.peewee-orm.com/en/latest/peewee/quickstart.html#model-definition
    """
    db.connect()
    # Book.authors is a ManyToManyField, so we need to create an intermediary table
    # See http://docs.peewee-orm.com/en/latest/peewee/api.html?highlight=get_through_model#ManyToManyField.get_through_model
    db.create_tables(
        [User, Author, Book, Book.authors.get_through_model()]
    )

def recreate_all_tables():
    """
    Peewee has no way of altering existing models, so if we change the models,
    we delete the database file if it exists.

    These are the SQL queries that we would write by hand to create these tables:

    CREATE TABLE IF NOT EXISTS "author" (
        "id" INTEGER NOT NULL PRIMARY KEY,
        "name" VARCHAR(255) NOT NULL
    )

    CREATE TABLE IF NOT EXISTS "user" (
        "id" INTEGER NOT NULL PRIMARY KEY,
        "email" VARCHAR(255) NOT NULL,
        "first_name" VARCHAR(255) NOT NULL,
        "last_name" VARCHAR(255) NOT NULL,
        "password" VARCHAR(255) NOT NULL,
        "logged_in" INTEGER NOT NULL,
        "last_seen" INTEGER,
        "is_admin" INTEGER NOT NULL
    )

    CREATE TABLE IF NOT EXISTS "book" (
        "id" INTEGER NOT NULL PRIMARY KEY,
        "title" VARCHAR(255) NOT NULL,
        "publication_year" INTEGER NOT NULL,
        "average_rating" REAL,
        "ratings_count" INTEGER NOT NULL,
        "image_url" VARCHAR(255) NOT NULL,
        "borrowed_by_id" INTEGER,
        "borrowed_at" DATE,
        FOREIGN KEY ("borrowed_by_id") REFERENCES "user" ("id")
    )

    CREATE TABLE IF NOT EXISTS "book_author_through" (
        "id" INTEGER NOT NULL PRIMARY KEY,
        "book_id" INTEGER NOT NULL,
        "author_id" INTEGER NOT NULL,
        FOREIGN KEY ("book_id") REFERENCES "book" ("id"),
        FOREIGN KEY ("author_id") REFERENCES "author" ("id")
    )
    """
    # os.path.isfile will check if a file exists on disk
    if os.path.isfile(DB_PATH):
        # os.remove removes a file from disk
        os.remove(DB_PATH)
    create_tables()


def create_initial_data():
    """
    Create users, authors and books.

    Given a books.csv file gotten from https://github.com/zygmuntz/goodbooks-10k/blob/master/samples/books.csv,
    fill initial data about books.
    """
    User.create(
        email="diaz.ayax@gmail.com",
        first_name="Ayax",
        last_name="Diaz",
        password="chorizo",
        is_admin=True
    )

    User.create(
        email="mustafa.sanli@gmail.com",
        first_name="Mustafa",
        last_name="Sanli",
        password="1234",
        is_admin=True
    )

    # Open the file in read mode. "r" stands for read, "w" for write
    with open('books.csv', mode='r') as csv_file:
        # This DictReader allows to return the data in books.csv as a list of dictionaries
        # where keys are the name of the columns and values are the values for each column in the curent row.
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            # In each row, get rid of unwanted data
            for book_column in dict(row).keys():
                # We don't care about all the columns. It's data downloaded from the web, so we will
                # only use part of it.
                if book_column not in ["title", "authors", "publication_year", "average_rating", "ratings_count", "image_url"]:
                    del row[book_column]
            # First create the authors. Remove it from the row dictionary and make it a list.
            # In the CSV, authors are separated by a comma followed by a space.
            authors_list = row.pop("authors").split(", ")
            authors_data = []
            # Create all authors, if not already created
            for author in set(authors_list):
                # Either create the author, or get an already created author.
                # See http://docs.peewee-orm.com/en/latest/peewee/querying.html?highlight=get_or_create#create-or-get
                author, _ = Author.get_or_create(name=author)
                authors_data.append(author)
            # Create the book first, and then add the authors. You have to do it this way for a ManyToManyField because
            # of the intermediary table.
            book = Book.create(**row)
            book.authors = authors_data
            book.save()


# This if is True only if this code is executed by calling "python models.py"
# If we don't add the if, the code will also be executed when importing the module,
# and we would delete our database every time we import the module, which we don't want.
# This is just to create or reset the database.
# Our web app will run by calling "python server.py"
if __name__ == '__main__':
    # Delete and recreate the Database
    recreate_all_tables()
    # Create some books, authors and admin users
    create_initial_data()
    # Check if it worked
    # for author in Author.select():
    #     print(author.name)