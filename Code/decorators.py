# -*- coding: utf-8 -*-
import functools
from factory import Factory
from singletonDatabaseConnect import SingletonDatabaseConnect as SDC
import db_class


def logger(func):
    db_url = "sqlite:///:memory:"
    db = SDC(db_url)
    session = db.get_session()
    factory = Factory("log")
    engine = db.get_engine()
    @functools.wraps(func)
    def wrapper_log(*args, **kwargs):
        try:
            value = func(*args, **kwargs)
            result = True
        except ValueError as e:
            value = e
            result = False
        
        if func.__name__ == 'borrow_book':
            uid = int(args[2])
            if value == True:
                book = session.query(db_class.Book).filter_by(isbn = args[1]).first()
                bid = book.id
            else:
                bid = -1

        elif func.__name__ == 'return_book':
            bid = args[1]
            uid = args[2]

        elif func.__name__ == 'reserve_book':
            book = session.query(db_class.Book).filter_by(isbn = args[1]).all()[-1]
            bid = book.id
            uid = args[2]

        log_data = {
            'kwargs' : str(args[1:]),
            'func' : func.__name__,
            'bid' : bid, 
            'uid' : uid,
            'result' : result
            }
        log = factory.create(log_data)
        type(log).metadata.create_all(engine)
        session.add(log)
        session.commit()
        
        if isinstance(value, Exception):
            raise ValueError(value)
        else:
            return value
        
    return wrapper_log