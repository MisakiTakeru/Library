# -*- coding: utf-8 -*-
from singletonDatabaseConnect import SingletonDatabaseConnect as SDC
import db_class
from factory import Factory
from sqlalchemy import update
from datetime import datetime


class Datahandler:

    def __init__(self, session, engine):
        self.session = session 
        self.engine = engine

    def reserve_book(self, book_isbn, user_id):
        user = self.session.query(db_class.User).filter_by(id = user_id).first()
        if user is None:
            raise ValueError(f"No user found with id {user_id}")

        #get listof books with isbn
        books = self.session.query(db_class.Book).filter_by(isbn = book_isbn).all()
        if books is None:
            raise ValueError(f"No book found with isbn {book_isbn}")
        
        #check if book is already reserved by user
        if book_isbn in user.reserved:
            raise ValueError(f"Book with isbn {book_isbn} is already reserved by user with id {user_id}")
        
        #user should borrow instead of reserve if book is available
        for book in books:
            if book.borrow_status == False:
                raise ValueError(f"Book with isbn {book_isbn} is available for borrowing")
        
            user.reserved[book_isbn] = datetime.now()

        try:
            print(f"User {user.name} reserved book with isbn {book_isbn} successfully")
            # Print user in a loop with all components
            for component in user.__dict__.items():
                print(component)
            self.session.commit()
            return True  
        except Exception as e:
            print(f"An error occurred: {e}")
            self.session.rollback()
            return False 

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
            return True  
        except Exception as e:
            print(f"An error occurred: {e}")
            self.session.rollback()
            return False  
        
    
    
    
    def borrow(self, name, uid):
        book = self.session.query(db_class.Book).filter_by(title = name).\
            filter_by(borrow_status = False).first()
        if book == None:
#            print(f'all versions of the book {name} has been borrowed.')
            return f'all versions of the book {name} has been borrowed.'
        else:
# Executes an update command that finds the book with the id found, and sets
# it's borrowed status to true
            self.session.execute(
                update(db_class.Book),
                [ {'id' : book.id, 'borrow_status' : True}])
            
            
            bb = self.session.query(db_class.User).filter_by(id = uid).first().borrowed
            self.session.execute(
                update(db_class.User),
                [ {'id' : uid, 'borrowed' : bb + [book.id]}])
            self.session.commit()
            return
            

    def reserve():
        pass    
        