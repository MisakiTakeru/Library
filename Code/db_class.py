# -*- coding: utf-8 -*-
import uuid
from sqlalchemy import Column, Integer, String, Float, JSON, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base() #Base class from sqlalchemy

class BookStatus(Base):
    __tablename__ = 'book_status'

    id = Column(Integer, primary_key=True)
    timestamp = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    book_id = Column(Integer, ForeignKey('books.id'))
    status_borrowed = Column(Boolean)
    status_reserved = Column(Boolean)
    status_available = Column(Boolean)

    user = relationship('User', back_populates='book_statuses')
    book = relationship('Book', back_populates='book_statuses')

    def __init__(self, timestamp, user_id, book_id, status_borrowed, status_reserved, status_available):
        self.timestamp = timestamp
        self.user_id = user_id
        self.book_id = book_id
        self.status_borrowed = status_borrowed
        self.status_reserved = status_reserved
        self.status_available = status_available

class Book(Base):
    __tablename__ = 'books'
    
    id = Column(Integer, primary_key = True)
    isbn = Column(String)
    title = Column(String)
    author = Column(String)
    release_date = Column(String)
    book_statuses = relationship('BookStatus', back_populates='book')

    def __init__(self, isbn, title, author, release_date, book_statuses=None):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.release_date = release_date
        self.book_statuses = book_statuses if book_statuses is not None else []

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key = True)
    name = Column(String)
    address = Column(String)
    email = Column(String)
    book_statuses = relationship('BookStatus', back_populates='user')

    def __init__(self, name, address, email, book_statuses=None):
        self.name = name
        self.address = address
        self.email = email
        self.book_statuses = book_statuses if book_statuses is not None else []

class Log(Base):
    __tablename__ = 'logs'
    
    id = Column(Integer, primary_key = True)
    kwargs = Column(String)
    func = Column(String)
    bid = Column(Integer)
    uid = Column(Integer)
    result = Column(Boolean)
    
    def __init__(self, kwargs, func, bid, uid, result):
        self.kwargs = kwargs
        self.func = func
        self.bid = bid
        self.uid = uid
        self.result = result

