# -*- coding: utf-8 -*-
from singletonDatabaseConnect import SingletonDatabaseConnect as SDC
import db_class
from factory import Factory
from sqlalchemy import update
from decorators import logger
import time
from sqlalchemy import and_
from pprint import pprint

class Datahandler:

    def __init__(self, session, engine):
        self.session = session 
        self.engine = engine

    def update_book_status(self, book_id, user_id, status_borrowed = None, status_reserved = None):
        # Fetch the book and user
        book = self.session.query(db_class.Book).filter_by(id = book_id).first()
        user = self.session.query(db_class.User).filter_by(id = user_id).first()

        if book is None or user is None:
            raise ValueError("Invalid book_id or user_id")

        # Fetch the latest book status
        book_status = self.session.query(db_class.BookStatus).filter_by(book_id = book_id).first()

        if book_status is None:
            # If no book status exists, create a new one
            book_status = db_class.BookStatus(int(time.time()), user_id, book_id, status_borrowed, status_reserved)
            self.session.add(book_status)
        else:
            if status_reserved != None:
                if book_status.status_reserved == True:
                    raise ValueError("book is already reserved")
                book_status.user_reserved = user_id
                book_status.status_reserved = status_reserved                    
            # If a book status exists, update it
            elif status_borrowed != None:
                book_status.timestamp = int(time.time())
                book_status.status_borrowed = status_borrowed
            
            # Update user_id based on status
                if status_borrowed:
                    book_status.user_id = user_id
                else:
                    book_status.user_id = 0
                    
                    if book_status.status_reserved == True:
                        # something with telling user_reserved book is ready
                        reserved_user = self.session.query(db_class.User).\
                            filter_by(id = book_status.user_reserved).first()
                        print(f'{reserved_user.name} the book {book.title} is now ready for being borrowed')
                        

        try:
            self.session.commit()
            return True
        except Exception as e:
            print(f"An error occurred: {e}")
            self.session.rollback()
            return False

    def add_user(self, name, address, email):
        user = Factory("user").create({"name": name, "address": address, "email": email})
        self.session.add(user)
        self.session.commit()
        return user.id
    
    def add_book(self, isbn, title, author, release_date):
        book = Factory("book").create({"isbn": isbn, "title": title, "author": author, "release_date": release_date})
        self.session.add(book)
        self.session.commit()
        self.__add_book_status(book.id)
        return book.id

    def __add_book_status(self, book_id, user_id = 0):
        book_status = Factory("book_status").create({"timestamp": time.time(), "book_id": book_id, "user_id": user_id, "status_borrowed": False, "status_reserved": False, "user_reserved" : 0})
        self.session.add(book_status)
        self.session.commit()
        return book_status.id

    @logger
    def reserve_book(self, book_isbn, user_id):
        book = self.session.query(db_class.Book).filter_by(isbn = book_isbn).first()
        user = self.session.query(db_class.User).filter_by(id = user_id).first()

        # check if book is already reserved by user
        if any(book_status.user_reserved == user_id for book_status in book.book_statuses):
            raise ValueError(f"Book with isbn {book_isbn} is already reserved by user with id {user_id}")

        # user should borrow instead of reserve if book is available
        if any(book_status.book_id == book.id and not book_status.status_borrowed for book_status in book.book_statuses):
            raise ValueError(f"User with id {user_id} should borrow book with id {book.id} instead of reserving it")

        # user should not be able to reserve a book he has already borrowed
        if any(book_status.book_id == book.id and book_status.status_borrowed for book_status in user.book_statuses):
            raise ValueError(f"User with id {user_id} has already borrowed book with id {book.id}")
        
        # find a book that is not reserved
        for book_status in book.book_statuses:
            if not book_status.status_reserved:
                return self.update_book_status(book.id, user.id, status_reserved=True)
        
        # if all copies are reserved, raise an error
        raise ValueError(f"All copies of book with isbn {book_isbn} are already reserved")
        
    @logger
    def return_book(self, book_id, user_id):

        # get list of book statuses with book_id
        book_statuses = self.session.query(db_class.BookStatus).filter_by(book_id = book_id).all()
        
        # check if book is already returned
        if all(not book_status.status_borrowed for book_status in book_statuses):
            raise ValueError(f"Book with id {book_id} is already returned by user with id {user_id}")
        
        return self.update_book_status(book_id, user_id, status_borrowed=False)
                
    @logger
    def borrow_book(self, book_isbn, user_id):
        books = self.session.query(db_class.Book).filter_by(isbn = book_isbn).all()
        user = self.session.query(db_class.User).filter_by(id = user_id).first()
        
        # Check if user has already borrowed a book with the same isbn
        if any(book_status.user_id == user.id and book_status.status_borrowed for book in books for book_status in book.book_statuses):
            raise ValueError(f"User with id {user_id} has already borrowed a book with isbn {book_isbn}")
        
        # Find a book that is not borrowed
        for book in books:
            if not any(book_status.status_borrowed for book_status in book.book_statuses):
                return self.update_book_status(book.id, user.id, status_borrowed=True)

        raise ValueError(f"All copies of book with isbn {book_isbn} are already borrowed")

    def get_user_by_id(self, user_id):
        users = self.lookup('user', 'id', user_id)
        if users:
            return users[0]
        else:
            return None

    def get_user_by_name(self, name):
        users = self.lookup('user', 'name', name)
        if users:
            return users[0]
        else:
            return None
    
    def get_all_users(self):
        users = self.lookup('user')
        if users:
            return users
        
    def get_book_by_id(self, book_id):
        books = self.lookup('book', 'id', book_id)
        if books:
            return books[0]
    
    def get_book_by_isbn(self, isbn):
        books = self.lookup('book', 'isbn', isbn)
        if books:
            return books[0]
        
    def get_book_by_title(self, title):
        books = self.lookup('book', 'title', title)
        if books:
            return books[0]
        
    def get_all_books(self):
        books = self.lookup('book')
        if books:
            return books
    
    def get_borrowed_books(self, user_id=None):
        if user_id is None:
            books = self.session.query(db_class.Book).join(db_class.BookStatus).filter(db_class.BookStatus.status_borrowed == True).all()
        else:
            books = self.session.query(db_class.Book).join(db_class.BookStatus).filter(and_(db_class.BookStatus.user_id == user_id, db_class.BookStatus.status_borrowed == True)).all()
        if books:
            return books

    def get_reserved_books(self, user_id=None):
        if user_id is None:
            books = self.session.query(db_class.Book).join(db_class.BookStatus).filter(db_class.BookStatus.status_reserved == True).all()
        else:
            books = self.session.query(db_class.Book).join(db_class.BookStatus).filter(and_(db_class.BookStatus.user_id == user_id, db_class.BookStatus.status_reserved == True)).all()
        if books:
            return books
        
# Lookup function to search and filter in the database.
    def lookup(self, db_search, filters = None, condition = None):
        db_search = db_search.lower().strip()
# First finds out which table to look at
        if db_search == 'book':
            table = db_class.Book

        elif db_search == 'user' or db_search == 'users':
            table = db_class.User
        elif db_search == 'status' or db_search == 'statuses':
            table = db_class.BookStatus
        else:
            raise ValueError(f'{db_search} table does not exist')

        data_list = []
        book_status_search = filters in ['timestamp', 'status_borrowed',
                'status_reserved','user_reserved', 'user_id', 'book_id']
# In cases conditions 
        if filters == None:
            data = self.session.query(table).all()
        elif book_status_search:
            bslist = self.session.query(db_class.BookStatus).filter(\
                getattr(db_class.BookStatus, filters) == condition).all()
            
            if db_search != 'status':
                for l in bslist:
                    v = dict(vars(getattr(l, db_search)))
                    del v[list(v)[0]]
                    data_list.append(v)
        else:
            data = self.session.query(table).filter(\
                      getattr(table, filters) == condition).all()
        if not book_status_search:
            for l in data:
                # creates a copy of the dictionary to not delete crucial data
                v = dict(vars(l))
                del v[list(v)[0]]
                data_list.append(v)
        pprint(data_list)
        return data_list
       
#   param for looking a either users or data
#   for finding books borrowed by user need to use bookstatus
#   lookup(user_id = 4, borrowed)
#
#
#
#
#
