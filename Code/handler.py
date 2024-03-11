# -*- coding: utf-8 -*-
from singletonDatabaseConnect import SingletonDatabaseConnect as SDC
import db_class
from factory import Factory
from sqlalchemy import update


class Datahandler:
    
    
    def return_book():
        pass    
        
    
    
    
    def borrow(name, uid):
        book = self.session.query(db_class.Book).filter_by(title = name).\
            filter_by(borrowed = False).first()
        if book == None:
            print(f'all versions of the book {name} has been borrowed.')
            return
        else:
# Executes an update command that finds the book with the id found, and sets
# it's borrowed status to true
            self.session.execute(
                update(db_class.Book),
                [ {'id' : book.id, 'borrowed' : True}])
            
            
            bb = self.session.query(db_class.User).filter_by(id = uid).first().borrowed
            self.session.execute(
                update(db_class.User),
                [ {'id' : uid, 'borrowed' : bb + [book.id]}])
            self.session.commit()
            return
            

    def reserve():
        pass    
        