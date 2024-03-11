# -*- coding: utf-8 -*-
from singletonDatabaseConnect import SingletonDatabaseConnect as SDC
import db_class
from factory import Factory
from sqlalchemy import update


class Datahandler:

    def __init__(self, session, engine):
        self.session = session 
        self.engine = engine

    
    def return_book(self, book_id):
        book = self.session.query(db_class.Book).filter_by(id = book_id).first()
        if book is None:
            raise ValueError(f"No book found with id {book_id}")

        user = self.session.query(db_class.User).filter_by(id = book.borrow_by).first()
        if user is None:
            raise ValueError(f"No user found with id {book.borrow_by}")

        if book.borrow_status == False:
            raise ValueError(f"Book with id {book_id} is not borrowed")
        
        if book_id not in user.borrowed:
            raise ValueError(f"Book with id {book_id} is not in user borrowed list")

        user.borrowed.remove(book_id)
        book.borrow_status = False 
        book.borrow_by = 0         

        try:
            print(f"User {user.name} returned book with id {book_id} and title {book.title} successfully")
            self.session.commit()
            return True  # Return True if commit is successful
        except Exception as e:
            print(f"An error occurred: {e}")
            return False  # Return False if an error occurred
        
    
    
    
    def borrow():
        pass
        


    def reserve():
        pass    
        