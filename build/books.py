#!/usr/bin/env python3

# Copyright (C) 2013-2018 Jean-Francois Romang (jromang@posteo.de)
#                         Shivkumar Shivaji ()
#                         Jürgen Précour (LocutusOfPenguin@posteo.de)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import os
import configparser


def write_book_ini():
    """Read the books folder and write the result to book.ini."""
    def is_book(fname):
        """Check for a valid book file name."""
        return fname.endswith('.bin')

    program_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    books_path = program_path + os.sep + 'books'

    book_list = sorted(os.listdir(books_path))
    config = configparser.ConfigParser()
    config.optionxform = str
    for book_file_name in book_list:
        if is_book(book_file_name):
            print(book_file_name)
            book = book_file_name[2:-4]
            config[book_file_name] = {}
            config[book_file_name]['small'] = book[:6]
            config[book_file_name]['medium'] = book[:8].title()
            config[book_file_name]['large'] = book[:11].title()
    with open(books_path + os.sep + 'books.ini', 'w') as configfile:
        config.write(configfile)


write_book_ini()
