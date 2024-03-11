# -*- coding: utf-8 -*-
import uuid
from sqlalchemy import Column, Integer, String, Float, JSON
from sqlalchemy.orm import declarative_base, Mapped

Base = declarative_base() #Base class from sqlalchemy

class Book(Base):
    __tablename__ = 'books'
    
    id = Column(Integer, primary_key = True)
    isbn = Column(String)
    title = Column(String)
    author = Column(String)
    release_date = Column(String)
    borrow_status = Column(JSON)
    
    def __init__(self, isbn, title, author, release_date, borrow_status = {}):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.release_date = release_date
        self.borrow_status = borrow_status


class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key = True)
    name = Column(String)
    address = Column(String)
    email = Column(String)
    borrowed = Column(JSON)
    
    def __init__(self, name, address, email, borrowed = {}):
        self.name = name
        self.address = address
        self.email = email
        self.borrowed = borrowed


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

