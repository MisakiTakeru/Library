# -*- coding: utf-8 -*-
import uuid
from sqlalchemy import Column, Integer, String, Float, JSON, Boolean
from sqlalchemy.orm import declarative_base, Mapped

Base = declarative_base() #Base class from sqlalchemy

class Book(Base):
    __tablename__ = 'books'
    
    id = Column(Integer, primary_key = True)
    isbn = Column(String)
    title = Column(String)
    author = Column(String)
    release_date = Column(String)
    borrow_by = Column(Integer) #user id
    borrow_status = Column(Boolean)
    
    def __init__(self, isbn, title, author, release_date, borrow_by = 0, borrow_status = False):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.release_date = release_date
        self.borrow_by = borrow_by
        self.borrow_status = borrow_status


class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key = True)
    name = Column(String)
    address = Column(String)
    email = Column(String)
    borrowed = Column(JSON)
    reserved = Column(JSON)
    
    def __init__(self, name, address, email, borrowed = {}, reserved = {}):
        self.name = name
        self.address = address
        self.email = email
        self.borrowed = borrowed #list of book id
        self.reserved = reserved #list of book isbns and timestamp (so we can sort by date and notify first user by time)


class Log:
    __tablename__ = 'logs'
    
    id = Column(Integer, primary_key = True)
    kwargs = Column(String)
    clas = Mapped['clas']
    bid = Column(Integer)
    uid = Column(Integer)
    
    def __init__(self, kwargs, clas, bid, uid):
        self.kwargs = kwargs
        self.clas = clas
        self.bid = bid
        self.uid = uid

