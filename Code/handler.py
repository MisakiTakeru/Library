# -*- coding: utf-8 -*-
from singletonDatabaseConnect import SingletonDatabaseConnect as SDC
import db_class
from factory import Factory
from sqlalchemy import update
from decorators import logger
import time

class Datahandler:

    def __init__(self, session, engine):
        self.session = session 
        self.engine = engine

    def update_book_status(self, book_id, user_id, status_borrowed, status_reserved, status_available):
        # Fetch the book and user
        book = self.session.query(db_class.Book).filter_by(id = book_id).first()
        user = self.session.query(db_class.User).filter_by(id = user_id).first()

        if book is None or user is None:
            raise ValueError("Invalid book_id or user_id")

        # Fetch the latest book status
        book_status = self.session.query(db_class.BookStatus).filter_by(book_id = book_id).order_by(db_class.BookStatus.timestamp.desc()).first()

        if book_status is None:
            # If no book status exists, create a new one
            book_status = db_class.BookStatus(int(time.time()), user_id, book_id, status_borrowed, status_reserved, status_available)
            self.session.add(book_status)
        else:
            # If a book status exists, update it
            book_status.timestamp = int(time.time())
            book_status.status_borrowed = status_borrowed
            book_status.status_reserved = status_reserved
            book_status.status_available = status_available

            # Update user_id based on status
            if status_borrowed or status_reserved:
                book_status.user_id = user_id
            elif status_available:
                book_status.user_id = 0

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
        book_status = Factory("book_status").create({"timestamp": time.time(), "book_id": book_id, "user_id": user_id, "status_borrowed": False, "status_reserved": False, "status_available": True})
        self.session.add(book_status)
        self.session.commit()
        return book_status.id

    @logger
    def reserve_book(self, book_isbn, user_id):
        book = self.session.query(db_class.Book).filter_by(isbn = book_isbn).first()
        user = self.session.query(db_class.User).filter_by(id = user_id).first()

        if user is None:
            raise ValueError(f"No user found with id {user_id}")

        if book is None:
            raise ValueError(f"No book found with isbn {book_isbn}")

        # check if book is already reserved by user
        if any(book_status.book_id == book.id and book_status.status_reserved for book_status in user.book_statuses):
            raise ValueError(f"Book with isbn {book_isbn} is already reserved by user with id {user_id}")

        # user should borrow instead of reserve if book is available
        if any(book_status.book_id == book.id and book_status.status_available for book_status in book.book_statuses):
            raise ValueError(f"User with id {user_id} should borrow book with id {book.id} instead of reserving it")

        # user should not be able to reserve a book he has already borrowed
        if any(book_status.book_id == book.id and book_status.status_borrowed for book_status in user.book_statuses):
            raise ValueError(f"User with id {user_id} has already borrowed book with id {book.id}")
        
        # find a book that is not reserved
        for book_status in book.book_statuses:
            if not book_status.status_reserved:
                return self.update_book_status(book.id, user.id, status_borrowed=True, status_reserved=True, status_available=False)

        # if all copies are reserved, raise an error
        raise ValueError(f"All copies of book with isbn {book_isbn} are already reserved")
        
    @logger
    def return_book(self, book_id, user_id):
        book = self.session.query(db_class.Book).filter_by(id = book_id).first()
        user = self.session.query(db_class.User).filter_by(id = user_id).first()

        if user is None:
            raise ValueError(f"No user found with id {user_id}")

        if book is None:
            raise ValueError(f"No book found with id {book_id}")

        # get list of book statuses with book_id
        book_statuses = self.session.query(db_class.BookStatus).filter_by(book_id = book_id).all()
        if not book_statuses:
            raise ValueError(f"No book status found with book_id {book_id}")
        
        # check if book is already returned
        if all(book_status.status_available for book_status in book_statuses):
            raise ValueError(f"Book with id {book_id} is already returned by user with id {user_id}")
        
        return self.update_book_status(book.id, user.id, status_borrowed=False, status_reserved=False, status_available=True)
                
    @logger
    def borrow_book(self, book_isbn, user_id):
        books = self.session.query(db_class.Book).filter_by(isbn = book_isbn).all()
        user = self.session.query(db_class.User).filter_by(id = user_id).first()

        if user is None:
            raise ValueError(f"No user found with id {user_id}")

        if not books:
            raise ValueError(f"No book found with isbn {book_isbn}")
        
        # Check if user has already borrowed a book with the same isbn
        if any(book_status.user_id == user.id and book_status.status_borrowed for book in books for book_status in book.book_statuses):
            raise ValueError(f"User with id {user_id} has already borrowed a book with isbn {book_isbn}")
        
        # Check if all copies are already borrowed
        if all(any(book_status.status_borrowed for book_status in book.book_statuses) for book in books):
            raise ValueError(f"All copies of book with isbn {book_isbn} are already borrowed")

        # Find a book that is not borrowed
        for book in books:
            if not any(book_status.user_id == user.id and book_status.status_borrowed for book_status in book.book_statuses):
                return self.update_book_status(book.id, user.id, status_borrowed=True, status_reserved=False, status_available=False)
            
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