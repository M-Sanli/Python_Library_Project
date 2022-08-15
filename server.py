"""
This module is the Bottle code that allows to serve pages to the end user.
Each function that is decorated with @route('/route') will add a reachable
URL to the server, for example http://localhost:8080/route.
"""
# These are imports of standard Python libraries included with python
import datetime
import logging
import time

# These are imports of libraries that need to be installed before running
# python server.py.
# The libraries to install are found in requirements.txt
# You install them by doing "pip install -r requirements.txt"
# See https://pip.pypa.io/en/stable/reference/pip_install/
from bottle import route, run, view, request, response, redirect, post, static_file, get, abort
from peewee import IntegrityError, fn, JOIN

# These are imports of files that are here in the project.
from models import User, Author, Book
from constants import SECRET_KEY, ALLOWED_BORROW_DAYS

# Create a logger we will use in the whole application to print things
# to the console
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# When running on http://localhost:8081 (See run command at the end of this file),
# the three @route decorators will allow to access this page at URLs:
# - http://localhost:8081
# - http://localhost:8081/
# - http://localhost:8081/home
# See https://bottlepy.org/docs/dev/tutorial.html#quickstart-hello-world
# For further functions, we will not explain how @route work.
#
# The @view("templates/home") decorator means we need to provide some data that will be used
# by bottle to render an HTML template, templates/home.tpl.
# We need to provide some data to it. The mechanism to provide data to a template is by returning
# a dictionary. See https://bottlepy.org/docs/dev/tutorial.html#templates
# For other functions, we won't document this mechanism anymore.
@route("")
@route("/")
@route('/home')
@view("templates/home")
def home():
    """
    This is the homepage of the website, accessible only to logged in users.

    It provides its template:
    - The logged in user, an instance of class User (see models.py).
    - Today's date.
    """
    # The get_logged_in_user is called first, which will make sure only logged in users see
    # the homepage. If not, they're redirected to the login page. See get_logged_in_user for
    # more details.
    user = get_logged_in_user()
    return {
        "user": user,
        "today": datetime.date.today(),
    }


@route("/borrow_books")
@view("templates/borrow_books")
def borrow_books():
    """
    This is a page with a list of books to borrow, accessible only to logged in users.

    It provides its template:
    - The logged in user, an instance of class User (see models.py).
    - A list of books the logged in user has not borrowed yet, instances of class Book.
    :return:
    """
    # The get_logged_in_user is called first, which will make sure only logged in users see
    # the homepage. If not, they're redirected to the login page. See get_logged_in_user for
    # more details.
    user = get_logged_in_user()

    # This query is a bit complex, since we have a ManyToMany relationship (with a get_through_model() which
    # is just a table with book IDs and Author IDs
    # For querying, see http://docs.peewee-orm.com/en/latest/peewee/querying.html
    # SQL:
    # SELECT id, title, publication_year, average_rating, ratings_count, image_url, borrowed_by_id, borrowed_at, user.id,
    # GROUP_CONCAT(author.name) AS author_list
    # FROM book
    # LEFT OUTER JOIN user ON (borrowed_by_id = user.id)
    # LEFT OUTER JOIN book_author_through ON (book_author_throug.book_id = id)
    # INNER JOIN author ON (book_author_trough.author_id = author.id)
    # GROUP BY id
    # ORDER BY title
    books = (
        Book
        .select(Book, User.id, fn.GROUP_CONCAT(Author.name).alias("author_list"))
        .join(User, JOIN.LEFT_OUTER)
        .switch()
        .join(Book.authors.get_through_model(), JOIN.LEFT_OUTER)
        .join(Author)
        .order_by(Book.title)
        .group_by(Book.id)

    )
    # Keep only the books that are not already borrowed by the current user, because
    # it does not make sense to show it in a list of borrowable books if the user already
    # has it.
    books_not_borrowed_by_current_user = [book for book in books if book.borrowed_by != user]
    return {"books": books_not_borrowed_by_current_user, "user": user}


@route("/borrow_book/<book_id:int>")
@view("templates/borrow_book")
def borrow_book(book_id):
    """
    This is the page the user lands on when he clicks on the "Borrow" Button in the
    borrow_books page.

    It will show which book was successfully borrowed and how many days the user
    has to return it.

    It provides its template:
    - The logged in user, an instance of class User.
    - The book borrowed, an instance of class Book.
    - The maximum number of days it is allowed to keep a book in the library (see constants.py)
    """
    # The get_logged_in_user is called first, which will make sure only logged in users see
    # the homepage. If not, they're redirected to the login page. See get_logged_in_user for
    # more details.
    user = get_logged_in_user()
    try:
        # Try to get the book from the ID provided in the URL (http://localhost/borrow_book/1 would
        # mean we have to search for the book with ID 1)
        # We could again be smart and do a complex join to get authors, but since it's a single book,
        # the optimization won't give us a lot of benefits, and simplicity is better here
        # SQL:
        # SELECT id, title, publication_year, average_rating, ratings_count, image_url, borrowed_by_id, borrowed_at
        # FROM book
        # WHERE (id = 25)
        book = Book.get(id=book_id)
    except Book.DoesNotExist:
        # If the URL is wrong (example http://localhost/borrow_book/100 with no book with id 100
        # in the DB, we send the user to an error page.
        abort(404, "Book not found.")

    # Set the user which is borrowing the book as the logged in user.
    book.borrowed_by = user
    # Set the date the book was borrowed.
    book.borrowed_at = datetime.date.today()
    book.save()
    # Provide the necessary info to the template (templates/borrow_book.tpl) so it can show
    # information about the book borrowed and in how many days he has to return it.
    return {"user": user, "book": book, "allowed_borrowed_days": str(ALLOWED_BORROW_DAYS)}


@route("/return_book/<book_id:int>")
def return_book(book_id):
    """
    When a user clicks on the "Return" button in his list of borrowed books (his home)
    The book is updated to make it returned, and the user is redirected to the same page
    (his home).
    """
    get_logged_in_user()
    # Try to find the Book with the ID which is in the URL.
    # If not found, send the user to an error page.
    try:
        # SELECT id, title, publication_year, average_rating, ratings_count, image_url, borrowed_by_id, borrowed_at
        # FROM book
        # WHERE (id = 25)
        book = Book.get(id=book_id)
    except Book.DoesNotExist:
        abort(404, "Book not found.")
    # The book was returned. Remove information about the last borrower
    # and the date it was borrowed.
    book.borrowed_by = None
    book.borrowed_at = None
    book.save()
    # Redirect to home, and since this page was accessed from a button on a book in the home,
    # it means it reloads the home with one book less in the list of borrowed books.
    redirect("/home")
    return True


@route("/logout")
def logout():
    """
    Logout of the page. Just set the user a logged_in = False
    and redirect him to the login page since we don't have any
    public homepage.
    """
    user = get_logged_in_user()
    # Set the user as logged out
    user.logged_in = False
    # SQL:
    # UPDATE user
    # SET logged_in = 0
    # WHERE ID = 25
    user.save()
    redirect("/login")


@route("/register")
@view("templates/register")
def register_landing_page():
    """
    This page is the one the user lands on when he is redirected to the
    Register page. It has a form with information to fill to register.

    This page is not the one that treats information the user provides
    when he clicks on the "Register" Button. That page is the function
    register below (with the @post("/register"), see
    https://bottlepy.org/docs/dev/tutorial.html#http-request-methods).

    We just provide the template (templates/register.tpl) empty values
    for everything.
    """
    return {
        "email": "",
        "password": "",
        "first_name": "",
        "last_name": "",
        "error": ""
    }

@post("/register")
@view("templates/register")
def register():
    """
    This is the page the user lands on when he clicks on the Register
    button after filling the form.

    It checks if the form is filled in correctly:
    - The user has entered a First Name.
    - The user has entered a Last Name.
    - The user has entered an Email address (we don't test the validity
      of the email address, only its existence). It is nonetheless an HTML element
      called "input" of type "email" (See https://www.w3schools.com/tags/att_input_type_email.asp)
      so it still verifies if it is a correctly formed email adress (example : banana@potato.com)
    - The user has entered a password.
    - A user with the same email does not already exist in the database.

    If any of the above is not True, we reload the register form, with all the fields unchanged
    and an error message.

    If all the tests pass, we create the User in our Database, set him as logged in and redirect him
    to his homepage.
    """
    # request.forms.get("email") is what we get from the email input in the templates/register.tpl
    # This input is defined like this:
    # <input name="email" value="{{email}}" type="email" class="form-control" id="email" aria-describedby="emailHelp" placeholder="Email">
    # The important part is value="{{email}}", which means whatever we return to the template in this function
    # in the "email" key of the dictionary, will be what the Input will have as a text when the user reloads the page.
    # So let's say the user enters an incorrect email and lands on this page.
    # We will check that the email is invalid, and return the entered email to the template.
    # That way, each time the user fails to register, the form has still the information he provided and is not empty.
    form_data = {
        "email": request.forms.get("email", default=""),
        "password": request.forms.get("password", default=""),
        "first_name": request.forms.get("first_name", default=""),
        "last_name": request.forms.get("last_name", default=""),
        "error": ""
    }
    # Check if all the fields were provided
    if not form_data["first_name"]:
        form_data["error"] = "Please enter a First Name."
        return form_data
    if not form_data["last_name"]:
        form_data["error"] = "Please enter a Last Name."
        return form_data
    if not form_data["email"]:
        form_data["error"] = "Please enter an email address."
        return form_data
    if not form_data["password"]:
        form_data["error"] = "Please enter a password."
        return form_data

    try:
        # Try to create the user. If it can't create it, it means
        # a User with the same email already exists. That's because we defined
        # User.email in models.py as : "email = CharField(unique=True)"
        # In SQL this would be
        # INSERT INTO user (first_name, last_name, email, password)
        # VALUES(Bob, Marley, kayanow@kaya.kaya, theWailersRule)
        user = User.create(
            first_name=form_data["first_name"],
            last_name=form_data["last_name"],
            email=form_data["email"],
            password=form_data["password"]
        )
    except IntegrityError:
        form_data["error"] = "User with email %s already registered. Please <a href='login'/>login</a> instead" % (form_data["email"])
        return form_data

    # The user was successfully created. Set him as logged in
    # and redirect him to his home.
    set_logged_in_user(user)
    redirect("/home")
    return True


@route("/login")
@view("templates/login")
def login_landing_page():
    """
    This page is the one the user lands on when he is redirected to the
    Login page. It has a form to login.

    This page is not the one that treats information the user provides
    when he clicks on the "Login" Button. That page is the function
    login below (with the @post("/login"),
    see https://bottlepy.org/docs/dev/tutorial.html#http-request-methods).

    We just provide the template (templates/register.tpl) empty values
    for everything.
    """
    return {
        "email": "",
        "password": "",
    }

@route("/login")
@post("/login")
@view("templates/login")
def login():
    """
    This is the page provided to log in.

    It first checks if the form is correctly filled:
    - The user has entered an Email address (we don't test the validity
      of the email address, only its existence). It is nonetheless an HTML element
      called "input" of type "email" (See https://www.w3schools.com/tags/att_input_type_email.asp)
      so it still verifies if it is a correctly formed email adress (example : banana@potato.com)
    - The user has entered a password.

    It then checks if it can find the user in the database. If it can, it sets the user as logged
    in (see set_logged_in_user function) and redirects him to his homepage.

    If it can't, it reloads the login page with an error message.
    """
    # The data entered by the User is the one we provide back to the template templates/login.tpl
    # with potentially an error message
    form_data = {
        "email": request.forms.get('email', default=""),
        "password": request.forms.get('password', default=""),
        "error": ""
    }
    if not form_data["email"]:
        form_data["error"] = "Please enter an email address."
        # Return to the same page with an error message
        return form_data
    if not form_data["password"]:
        form_data["error"] = "Please enter a password."
        return form_data

    try:
        # Try to find the User
        # SQL: SELECT id, email, first_name, last_name, password, logged_in, last_seen, is_admin
        # FROM user
        # WHERE ((email = bob.marley@wailers.com) AND (password = kayaNow))
        user = User.get(User.email==form_data["email"], User.password == form_data["password"])

        # The user is found, set him as logged in (some fields updated on the Database + encrypted cookie)
        # and redirect him to his home.
        set_logged_in_user(user)
        redirect("/home")
        return True
    except User.DoesNotExist:
        # The user does not exist. reload the same page with an error message.
        form_data["error"] = "Bad email/password. Please try again or Register."
        return form_data


@get("/static/<filepath:re:.*\.(jpg|png|gif|ico|svg)>")
def img(filepath):
    """
    This is the recommended way to serve static files (images, documents, etc) by bottle.

    See https://stackoverflow.com/questions/10486224/bottle-static-files
    """
    return static_file(filepath, root="static")


def set_logged_in_user(user):
    """
    When a User logs in or registers, make him logged in.

    1/ Set an encrypted cookie with the user's email and the password.
       It will help check if he is logged in.
    2/ Update some values on the User in the Database (logged_in, last_seen)
    """
    response.set_cookie("user-email", user.email, secret=SECRET_KEY)
    response.set_cookie("password", user.password, secret=SECRET_KEY)
    user.logged_in = True
    user.last_seen = time.time()
    user.save()

def get_logged_in_user():
    """
    This function needs to be called by any route that needs to be private
    (only accessible to a logged in User).

    It tries to match the information stored in an encrypted cookie
    (see the log_in function) with a User in the Database.

    The conditions are:
    - The email stored in the cookie must match
    - The password stored in the cookie must match
    - The User must have been logged in in the past hour (3600 seconds)

    If the conditions are met, we update the last time the user
    was seen logged in, and return the user.

    If they are not met, the user is redirected to the login page.
    """

    # Get the user email and the password stored in the cookie
    # They are encrypted by SECRET_KEY. Right now, SECRET_KEY is available
    # in constants.py, which means that it is not very safe. Normally SECRET_KEY
    # should be protected so that malicious users cannot read the cookie.
    user_email = request.get_cookie("user-email", secret=SECRET_KEY)
    password = request.get_cookie("password", secret=SECRET_KEY)
    try:
        # Try to see if the information in the cookie matches a User in the
        # Database which has been connected in the past hour.
        # SQL:
        # SELECT id, email, first_name, last_name, password, logged_in, last_seen, is_admin
        # FROM user
        # WHERE (
        #   (email = bob@bob.bob)
        #   AND (password = "fdasfdsfadf")
        #   AND (logged_in = 1)
        #   AND (12344567 - last_seen) < 3600)
        # )
        user = User.get(
            User.email == user_email,
            User.password == password,
            User.logged_in == True,
            time.time() - User.last_seen < 3600
        )
        # Update time last seen and return the connected User.
        user.last_seen = time.time()
        user.save()
        return user
    except User.DoesNotExist:
        # The user has never logged in, or has logged out,
        # or has been inactive on the site for more than an hour.
        redirect("/login")

# Run the service.
# The host is localhost, so it runs on the local machine, and the website
# will be available at http://localhost
# The port is 8081, so actually the full URL is http://localhost:8081
# reloader=True allows you, when you are running "python server.py",
# to change the code in "server.py", refresh the web page, and see the changes
# you made in your code. This is very helpful for developing.
run(host='localhost', port=8081, reloader=True, debug=True)