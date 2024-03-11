# -*- coding: utf-8 -*-
import uuid
from sqlalchemy import Column, Integer, String, Float, JSON
from sqlalchemy.orm import declarative_base, Mapped

Base = declarative_base() #Base class from sqlalchemy

class book(Base):
    __tablename__ = 'books'
    
    id = Column(Integer, primary_key = True)
    isbn = Column(String)
    title = Column(String)
    author = Column(String)
    release_date = Column(String)
    
    def __init__(self, isbn, title, author, release_date):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.release_date = release_date


class user(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key = True)
    name = Column(String)
    address = Column(String)
    email = Column(String)
    borrowed = Column(JSON)
    
    def __init__(self, name, address, email):
        self.name = name
        self.address = address
        self.email = email
        self.borrowed = {}


class logging:
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

