# -*- coding: utf-8 -*-
from singletonDatabaseConnect import SingletonDatabaseConnect as SDC
import db_class
from factory import Factory
from sqlalchemy import update
from sqlalchemy.orm.attributes import flag_modified
from datetime import datetime
from decorators import logger
import time

class Datahandler:

    def __init__(self, session, engine):
        self.session = session 
        self.engine = engine
    @logger
    def reserve_book(self, book_isbn, user_id):
        user = self.session.query(db_class.User).filter_by(id = user_id).first()
        if user is None:
            raise ValueError(f"No user found with id {user_id}")

        #get list of books with isbn
        books = self.session.query(db_class.Book).filter_by(isbn = book_isbn).all()
        if not books:
            raise ValueError(f"No book found with isbn {book_isbn}")
        
        #check if book is already reserved by user
        if any(reserved.isbn == book_isbn for reserved in user.reserved):
            raise ValueError(f"Book with isbn {book_isbn} is already reserved by user with id {user_id}")
        
        #user should borrow instead of reserve if book is available
        for book in books:
            if not book.borrowed:
                raise ValueError(f"Book with isbn {book_isbn} is available for borrowing")
        
        #user should not be able to reserve a book he has already borrowed
        for book in books:
            if any(borrowed.book_id == book.id for borrowed in user.borrowed):
                raise ValueError(f"User with id {user_id} has already borrowed book with id {book.id}")

        user.reserved.append(db_class.Reserved(user_id, book.id, book_isbn, int(time.time())))

        try:
            print(f"User {user.name} reserved book with isbn {book_isbn} successfully")
            self.session.commit()
            return True
        except Exception as e:
            print(f"An error occurred: {e}")
            self.session.rollback()
            return False
    @logger
    def return_book(self, book_id):
        book = self.session.query(db_class.Book).filter_by(id = book_id).first()
        if book is None:
            raise ValueError(f"No book found with id {book_id}")

        borrowed_book = self.session.query(db_class.Borrowed).filter_by(book_id = book_id).first()
        if borrowed_book is None:
            raise ValueError(f"Book with id {book_id} is not borrowed")

        user = self.session.query(db_class.User).filter_by(id = borrowed_book.user_id).first()
        if user is None:
            raise ValueError(f"No user found with id {borrowed_book.user_id}")

        # Remove the borrowed_book from the borrowed list of the user and the book
        user.borrowed.remove(borrowed_book)
        book.borrowed.remove(borrowed_book)

        self.session.delete(borrowed_book)

        try:
            print(f"User {user.name} returned book with id {book_id} and title {book.title} successfully")
            self.session.commit()
            return True  
        except Exception as e:
            print(f"An error occurred: {e}")
            self.session.rollback()
            return False
    
    @logger
    def borrow(self, name, uid):
        book = self.session.query(db_class.Book).filter_by(title = name).\
            filter(not db_class.Book.borrowed).first()
        if book == None:
            return f'all versions of the book {name} has been borrowed.'
        else:
            borrowed = db_class.Borrowed(user_id=uid, book_id=book.id)
            user = self.session.query(db_class.User).filter_by(id = uid).first()
            user.borrowed.append(borrowed)
            book.borrowed.append(borrowed)

            self.session.execute(
                update(db_class.Book).where(db_class.Book.id == book.id).values(borrowed=book.borrowed))
                        
            
            self.session.execute(
                update(db_class.User).where(db_class.User.id == uid).values(borrowed=user.borrowed))

            self.session.commit()
            return