"""
A module to keep project constants
"""

# The relative path to the DB file
DB_PATH = "library.db"
# The number of days a book is allowed to be borrowed
ALLOWED_BORROW_DAYS = 30  # type: int

# This is the Secret Key of the application used to make login
# secure. As seen in 08_Web_Apps_with_python/Other (end of document)
# Normally this should not be stored here. It should be an environment
# variable (See https://kelvinmwinuka.com/setting-environment-variables-on-macos/)
# For simplicity, we store it here.
SECRET_KEY = "fdasfjkaldfghadfgbadfshjmbadsjflqrefeq"