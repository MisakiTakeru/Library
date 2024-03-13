# -*- coding: utf-8 -*-
import uuid
from sqlalchemy import Column, Integer, String, Float, JSON, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

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

class Reserved(Base):
    __tablename__ = 'reserved'

    id = Column(Integer, primary_key=True)
    isbn = Column(String)
    timestamp = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))

    def __init__(self, isbn, timestamp):
        self.isbn = isbn
        self.timestamp = timestamp

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key = True)
    name = Column(String)
    address = Column(String)
    email = Column(String)
    borrowed = Column(JSON)
    reserved = relationship('Reserved', backref='user')

    def __init__(self, name, address, email, borrowed = {}, reserved = None):
        self.name = name
        self.address = address
        self.email = email
        self.borrowed = borrowed #list of book id
        self.reserved = reserved if reserved is not None else []

class Log:
    __tablename__ = 'logs'
    
    id = Column(Integer, primary_key = True)
    kwargs = Column(String)
    func = Column(String)
    bid = Column(Integer)
    uid = Column(Integer)
    
    def __init__(self, kwargs, func, bid, uid):
        self.kwargs = kwargs
        self.func = func
        self.bid = bid
        self.uid = uid

