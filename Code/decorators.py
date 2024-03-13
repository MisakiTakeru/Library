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
#        bid = 0
#        uid = 0
#        result = False
        if func.__name__ == 'return_book':
            book = session.query(db_class.Book).filter_by(id = args[1]).first()
            uid = book.borrow_by
        value = func(*args, **kwargs)
        
        if func.__name__ == 'borrow':
            uid = int(args[2])
            if value == f'all versions of the book {args[1]} has been borrowed.':
                result = False
                bid = -1
            else:
                result = True
                user = session.query(db_class.User).filter_by(id = int(args[2])).first()
                bid = user.borrowed[-1]
            
        elif func.__name__ == 'return_book':
            bid = args[1]
            result = value

        elif func.__name__ == 'reserve_book':
            book = session.query(db_class.Book).filter_by(isbn = args[1]).first()
            bid = book.id
            uid = args[2]
            result = value
#            isbn userid

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
        
        return value
    return wrapper_log