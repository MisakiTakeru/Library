# -*- coding: utf-8 -*-
import uuid
from sqlalchemy import Column, Integer, String, Float, JSON, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base() #Base class from sqlalchemy

class Borrowed(Base):
    __tablename__ = 'borrowed'

    id = Column(Integer, primary_key=True)
    timestamp = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    book_id = Column(Integer, ForeignKey('books.id'))

    def __init__(self, timestamp, user_id, book_id):
        self.timestamp = timestamp
        self.user_id = user_id
        self.book_id = book_id

class Reserved(Base):
    __tablename__ = 'reserved'

    id = Column(Integer, primary_key=True)
    isbn = Column(String)
    timestamp = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    book_id = Column(Integer, ForeignKey('books.id'))

    def __init__(self, isbn, timestamp, user_id, book_id):
        self.isbn = isbn
        self.timestamp = timestamp
        self.user_id = user_id
        self.book_id = book_id

class Book(Base):
    __tablename__ = 'books'
    
    id = Column(Integer, primary_key = True)
    isbn = Column(String)
    title = Column(String)
    author = Column(String)
    release_date = Column(String)
    borrowed = relationship('Borrowed', backref='book')
    reserved = relationship('Reserved', backref='book')

    def __init__(self, isbn, title, author, release_date,  borrowed = None, reserved = None):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.release_date = release_date
        self.borrowed = borrowed if borrowed is not None else []
        self.reserved = reserved if reserved is not None else []

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key = True)
    name = Column(String)
    address = Column(String)
    email = Column(String)
    borrowed = relationship('Borrowed', backref='user')
    reserved = relationship('Reserved', backref='user')

    def __init__(self, name, address, email, borrowed = None, reserved = None):
        self.name = name
        self.address = address
        self.email = email
        self.borrowed = borrowed if borrowed is not None else []
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

