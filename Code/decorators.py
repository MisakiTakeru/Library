# -*- coding: utf-8 -*-
import functools
from factory import Factory
from singletonDatabaseConnect import SingletonDatabaseConnect as SDC
import db_class


#    kwargs = Column(String)
#    clas = Mapped['clas']
#    bid = Column(Integer)
#    uid = Column(Integer)

def logger(func):
    db_url = "sqlite:///:memory:"
    db = SDC(db_url)
    session = db.get_session()
    @functools.wraps(func)
    def wrapper_log(*args, **kwargs):
        args_repr = [repr(a) for a in args]
#        for i in args_repr:
#            print(i)
#            if i == '1':
#                book = session.query(db_class.Book).filter_by(id = i).first()
#                print(f'book is {book.title} by {book.author}')
        kwargs_repr = [f"{k}={repr(v)}" for k, v in kwargs.items()]
        print(kwargs_repr)
        signature = ", ".join(args_repr + kwargs_repr)
        print(f"Calling {func.__name__}({signature})")
        value = func(*args, **kwargs)
        print(f"{func.__name__}() returned {repr(value)}")
        
        if func.__name__ == 'borrow':
            log_data = {
                'kwargs' : args_repr[1:],
                'clas'}
        
        return value
    return wrapper_log