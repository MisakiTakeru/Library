import unittest
from factory import Factory
from singletonDatabaseConnect import SingletonDatabaseConnect
from handler import Datahandler
import db_class
import time
from pprint import pprint
#python -m unittest newTest.py
#pprint(vars(session.query(db_class.BookStatus).all()[0]))

def cleanup(session):
        try:
            session.query(db_class.BookStatus).delete()
        except:
            pass
        try:
            session.query(db_class.Book).delete()
        except:
            pass
        try:
            session.query(db_class.User).delete()
        except:
            pass
        session.commit()    

class TestData(unittest.TestCase):
    def __init__(self):

        self.user_data = {
            "name": "John Doe",
            "address": "1234 Main St",
            "email": "john@doe.com",
            #"book_statuses": [db_class.BookStatus(**{"timestamp": 1633027442, "user_id": 1, "book_id": 1, "status_borrowed": False, "status_reserved": False, "status_available": True})]
        }
        self.other_user_data = {
            "name": "Jane Doe",
            "address": "1234 Main St",
            "email": "jane@doe.com",
            #"book_statuses": [db_class.BookStatus(**{"timestamp": 1633027442, "user_id": 2, "book_id": 1, "status_borrowed": False, "status_reserved": False, "status_available": True})]
        }

        self.book_data = {
            "isbn": "123",
            "title": "John Book",
            "author": "John Doe",
            "release_date": 1619827200,
            #"book_statuses": [db_class.BookStatus(**{"timestamp": 1633027442, "user_id": 0, "book_id": 0, "status_borrowed": False, "status_reserved": False, "status_available": True})]
        }

        self.other_book_data = {
            "isbn": "1234",
            "title": "Jane Book",
            "author": "Jane Doe",
            "release_date": 1619827200,
            #"book_statuses": [db_class.BookStatus(**{"timestamp": 1633027442, "user_id": 2, "book_id": 2, "status_borrowed": False, "status_reserved": False, "status_available": True})]
        }

class TestSingletonDatabaseConnect(unittest.TestCase):
    def setUp(self) -> None:
        self.db_url = "sqlite:///:memory:"
        self.db = SingletonDatabaseConnect(self.db_url)
        self.data = TestData()
        self.user_data = self.data.user_data
        self.other_user_data = self.data.other_user_data
        self.book_data = self.data.book_data
        self.other_book_data = self.data.other_book_data

    def test_singleton(self):
        db = SingletonDatabaseConnect(self.db_url)
        self.assertEqual(self.db, db)
    
    def test_get_session(self):
        session = self.db.get_session()
        self.assertIsNotNone(session)
    
    def test_engine_is_singleton(self):
        db1 = SingletonDatabaseConnect(self.db_url)
        db2 = SingletonDatabaseConnect(self.db_url)
        engine1 = db1.get_engine()
        engine2 = db2.get_engine()
        self.assertIs(engine1, engine2)

###########
# Test inserts
###########
    def test_insert_user(self):
        factory = Factory("user")
        user = factory.create(self.user_data)
        session = self.db.get_session()
        engine = self.db.get_engine()

        db_class.User.metadata.create_all(engine) #create table

        session.add(user)
        session.commit()

        self.assertTrue(user.id)

        #cleanup
        session.query(db_class.User).delete()
        session.commit()
    
    def test_insert_book(self):
        factory = Factory("book")
        book = factory.create(self.book_data)
        session = self.db.get_session()
        engine = self.db.get_engine()

        db_class.Book.metadata.create_all(engine)

        session.add(book)
        session.commit()

        self.assertTrue(book.id)

        #cleanup
        session.query(db_class.Book).delete()
        session.commit()

    def test_insert_book_with_status(self):
        factory = Factory("book")
        book = factory.create(self.book_data)
        session = self.db.get_session()
        cleanup(session)
        engine = self.db.get_engine()
        handler = Datahandler(session, engine)

        db_class.Book.metadata.create_all(engine)
        db_class.BookStatus.metadata.create_all(engine)

        book_id = handler.add_book(book.isbn, book.title, book.author, book.release_date)
        book_statuses = session.query(db_class.BookStatus).all()

        self.assertTrue(book_id == 1)
        self.assertEqual(book_statuses[0].book_id, book_id)
        self.assertFalse(book_statuses[0].status_borrowed)

        #cleanup
        session.query(db_class.BookStatus).delete()
        session.query(db_class.Book).delete()
        session.commit()
    
    def test_insert_user(self):
        factory = Factory("user")
        user = factory.create(self.user_data)
        session = self.db.get_session()
        cleanup(session)
        engine = self.db.get_engine()
        handler = Datahandler(session, engine)

        db_class.User.metadata.create_all(engine)

        user_id = handler.add_user(user.name, user.address, user.email)

        self.assertTrue(user_id == 1)

        #cleanup
        session.query(db_class.BookStatus).delete()
        session.query(db_class.User).delete()
        session.commit()
    
###########
# Test borrow_book
###########
    def test_borrow_book(self):
        book = Factory("book").create(self.book_data)
        user = Factory("user").create(self.user_data)
        session = self.db.get_session()
        cleanup(session)
        engine = self.db.get_engine()
        handler = Datahandler(session, engine)

        db_class.Book.metadata.create_all(engine)
        db_class.User.metadata.create_all(engine)
        db_class.BookStatus.metadata.create_all(engine)

        book_id = handler.add_book(book.isbn, book.title, book.author, book.release_date)
        user_id = handler.add_user(user.name, user.address, user.email)
        book = session.query(db_class.Book).filter_by(id = book_id).first()
        user = session.query(db_class.User).filter_by(id = user_id).first()

        handler.borrow_book(book.isbn, user.id)

        book_status = session.query(db_class.BookStatus).filter_by(book_id=book_id).first()
        self.assertTrue(book_status.status_borrowed)
        self.assertFalse(book_status.status_reserved)

        #cleanup
        session.query(db_class.BookStatus).delete()
        session.query(db_class.Book).delete()
        session.query(db_class.User).delete()
        session.commit()
    
    def test_borrow_book_already_borrowed_by_yourself(self):
        book = Factory("book").create(self.book_data)
        user = Factory("user").create(self.user_data)
        session = self.db.get_session()
        cleanup(session)
        engine = self.db.get_engine()
        handler = Datahandler(session, engine)

        db_class.Book.metadata.create_all(engine)
        db_class.User.metadata.create_all(engine)
        db_class.BookStatus.metadata.create_all(engine)

        book_id = handler.add_book(book.isbn, book.title, book.author, book.release_date)
        book2_id = handler.add_book(book.isbn, book.title, book.author, book.release_date)
        user_id = handler.add_user(user.name, user.address, user.email)
        book = session.query(db_class.Book).filter_by(id = book_id).first()
        user = session.query(db_class.User).filter_by(id = user_id).first()

        # Borrow the book once
        handler.borrow_book(book.isbn, user.id)

        #ValueError(f"User with id {user_id} has already borrowed a book with isbn {book_isbn}")
        with self.assertRaisesRegex(ValueError, f"User with id {user.id} has already borrowed a book with isbn {book.isbn}"):
            handler.borrow_book(book.isbn, user.id)

        #cleanup
        session.query(db_class.BookStatus).delete()
        session.query(db_class.Book).delete()
        session.query(db_class.User).delete()
        session.commit()

    def test_borrow_book_all_copies_borrowed(self):
        book = Factory("book").create(self.book_data)
        user = Factory("user").create(self.user_data)
        other_user = Factory("user").create(self.other_user_data)
        session = self.db.get_session()
        cleanup(session)
        engine = self.db.get_engine()
        handler = Datahandler(session, engine)

        db_class.Book.metadata.create_all(engine)
        db_class.User.metadata.create_all(engine)
        db_class.BookStatus.metadata.create_all(engine)

        book_id = handler.add_book(book.isbn, book.title, book.author, book.release_date)
        user_id = handler.add_user(user.name, user.address, user.email)
        other_user_id = handler.add_user(other_user.name, other_user.address, other_user.email)
        book = session.query(db_class.Book).filter_by(id = book_id).first()
        user = session.query(db_class.User).filter_by(id = user_id).first()
        other_user = session.query(db_class.User).filter_by(id = other_user_id).first()


        handler.borrow_book(book.isbn, user.id)



        # ValueError(f"All copies of book with isbn {book_isbn} are already borrowed")
        with self.assertRaisesRegex(ValueError, f"All copies of book with isbn {book.isbn} are already borrowed"):
            handler.borrow_book(book.isbn, other_user.id)

        #cleanup
        session.query(db_class.BookStatus).delete()
        session.query(db_class.Book).delete()
        session.query(db_class.User).delete()
        session.commit()

###########
# Test reserve_book
###########
    def test_reserve_book(self):
        book = Factory("book").create(self.book_data)
        user = Factory("user").create(self.user_data)
        other_user = Factory("user").create(self.other_user_data) 
        session = self.db.get_session()
        cleanup(session)
        engine = self.db.get_engine()
        handler = Datahandler(session, engine)

        db_class.Book.metadata.create_all(engine)
        db_class.User.metadata.create_all(engine)
        db_class.BookStatus.metadata.create_all(engine)

        book_id = handler.add_book(book.isbn, book.title, book.author, book.release_date)
        user_id = handler.add_user(user.name, user.address, user.email)
        other_user_id = handler.add_user(other_user.name, other_user.address, other_user.email)

        handler.borrow_book(book.isbn, user_id)

        handler.reserve_book(book.isbn, other_user_id)

        book_status = session.query(db_class.BookStatus).filter_by(book_id=book_id).first()
        self.assertTrue(book_status.status_borrowed)
        self.assertTrue(book_status.status_reserved)
        self.assertEqual(book_status.user_id, user_id)
        self.assertEqual(book_status.user_reserved, other_user_id)

        #cleanup
        session.query(db_class.BookStatus).delete()
        session.query(db_class.Book).delete()
        session.query(db_class.User).delete()
        session.commit()
    
    def test_reserve_book_already_reserved_by_user(self):
        book = Factory("book").create(self.book_data)
        user = Factory("user").create(self.user_data)
        other_user = Factory("user").create(self.other_user_data) 
        session = self.db.get_session()
        cleanup(session)
        engine = self.db.get_engine()
        handler = Datahandler(session, engine)

        db_class.Book.metadata.create_all(engine)
        db_class.User.metadata.create_all(engine)
        db_class.BookStatus.metadata.create_all(engine)

        book_id = handler.add_book(book.isbn, book.title, book.author, book.release_date)
        user_id = handler.add_user(user.name, user.address, user.email)
        other_user_id = handler.add_user(other_user.name, other_user.address, other_user.email)
        book = session.query(db_class.Book).filter_by(id = book_id).first()
        user = session.query(db_class.User).filter_by(id = user_id).first()
        other_user = session.query(db_class.User).filter_by(id = other_user_id).first()


        handler.borrow_book(book.isbn, user_id)

        
        handler.reserve_book(book.isbn, other_user_id)
        

        with self.assertRaisesRegex(ValueError, f"Book with isbn {book.isbn} is already reserved by user with id {other_user.id}"):
            handler.reserve_book(book.isbn, other_user_id)

        #cleanup
        session.query(db_class.BookStatus).delete()
        session.query(db_class.Book).delete()
        session.query(db_class.User).delete()
        session.commit()

    def test_reserve_book_ask_to_borrow_instead_of_reserve(self):
        book = Factory("book").create(self.book_data)
        user = Factory("user").create(self.user_data) 
        session = self.db.get_session()
        cleanup(session)
        engine = self.db.get_engine()
        handler = Datahandler(session, engine)

        db_class.Book.metadata.create_all(engine)
        db_class.User.metadata.create_all(engine)
        db_class.BookStatus.metadata.create_all(engine)

        book_id = handler.add_book(book.isbn, book.title, book.author, book.release_date)
        user_id = handler.add_user(user.name, user.address, user.email)
        book = session.query(db_class.Book).filter_by(id = book_id).first()
        user = session.query(db_class.User).filter_by(id = user_id).first()
        
        #raise ValueError(f"User with id {user_id} should borrow book with id {book.id} instead of reserving it")
        with self.assertRaisesRegex(ValueError, f"User with id {user.id} should borrow book with id {book.id} instead of reserving it"):
            handler.reserve_book(book.isbn, user.id)

        #cleanup
        session.query(db_class.BookStatus).delete()
        session.query(db_class.Book).delete()
        session.query(db_class.User).delete()
        session.commit()

    def test_reserve_book_all_copies_reserved(self):
        book = Factory("book").create(self.book_data)
        user = Factory("user").create(self.user_data)
        other_user = Factory("user").create(self.other_user_data)
        other_user2 = Factory("user").create(self.other_user_data)
        session = self.db.get_session()
        cleanup(session)
        engine = self.db.get_engine()
        handler = Datahandler(session, engine)

        db_class.Book.metadata.create_all(engine)
        db_class.User.metadata.create_all(engine)
        db_class.BookStatus.metadata.create_all(engine)

        book_id = handler.add_book(book.isbn, book.title, book.author, book.release_date)
        user_id = handler.add_user(user.name, user.address, user.email)
        other_user_id = handler.add_user(other_user.name, other_user.address, other_user.email)
        other_user2_id = handler.add_user(other_user2.name, other_user2.address, other_user2.email)
        book = session.query(db_class.Book).filter_by(id = book_id).first()
        user = session.query(db_class.User).filter_by(id = user_id).first()
        other_user = session.query(db_class.User).filter_by(id = other_user_id).first()
        other_user2 = session.query(db_class.User).filter_by(id = other_user2_id).first()

        handler.borrow_book(book.isbn, other_user.id)
        handler.reserve_book(book.isbn, user.id)

        #raise ValueError(f"All copies of book with isbn {book_isbn} are already reserved")
        with self.assertRaisesRegex(ValueError, f"All copies of book with isbn {book.isbn} are already reserved"):
            handler.reserve_book(book.isbn, other_user2.id)

###########
# Test return_book
###########
    def test_return_book(self):
        book = Factory("book").create(self.book_data)
        user = Factory("user").create(self.user_data)
        session = self.db.get_session()
        cleanup(session)
        engine = self.db.get_engine()
        handler = Datahandler(session, engine)

        db_class.Book.metadata.create_all(engine)
        db_class.User.metadata.create_all(engine)
        db_class.BookStatus.metadata.create_all(engine)

        book_id = handler.add_book(book.isbn, book.title, book.author, book.release_date)
        user_id = handler.add_user(user.name, user.address, user.email)
        book = session.query(db_class.Book).filter_by(id = book_id).first()
        user = session.query(db_class.User).filter_by(id = user_id).first()

        handler.borrow_book(book.isbn, user.id)

        handler.return_book(book.id, user.id)

        book_status = session.query(db_class.BookStatus).filter_by(book_id=book_id).first()
        self.assertFalse(book_status.status_borrowed)
        self.assertFalse(book_status.status_reserved)

        #cleanup
        session.query(db_class.BookStatus).delete()
        session.query(db_class.Book).delete()
        session.query(db_class.User).delete()
        session.commit()

    def test_return_book_not_borrowed(self):
        book = Factory("book").create(self.book_data)
        user = Factory("user").create(self.user_data)
        session = self.db.get_session()
        engine = self.db.get_engine()
        handler = Datahandler(session, engine)

        db_class.Book.metadata.create_all(engine)
        db_class.User.metadata.create_all(engine)
        db_class.BookStatus.metadata.create_all(engine)

        book_id = handler.add_book(book.isbn, book.title, book.author, book.release_date)
        user_id = handler.add_user(user.name, user.address, user.email)
        book = session.query(db_class.Book).filter_by(id = book_id).first()
        user = session.query(db_class.User).filter_by(id = user_id).first()

        #ValueError(f"Book with id {book_id} is already returned by user with id {user_id}")
        with self.assertRaisesRegex(ValueError, f"Book with id {book.id} is already returned by user with id {user.id}"):
            handler.return_book(book.id, user.id)

        #cleanup
        session.query(db_class.BookStatus).delete()
        session.query(db_class.Book).delete()
        session.query(db_class.User).delete()
        session.commit()
    
class CustomTestResult(unittest.TextTestResult):
    def printErrors(self):
        self.stream.writeln("Passed: {}".format(self.testsRun - len(self.failures) - len(self.errors)))
        self.stream.writeln("Failed: {}".format(len(self.failures)))
        self.stream.writeln("Errors: {}".format(len(self.errors)))
        super().printErrors()

class CustomTestRunner(unittest.TextTestRunner):
    resultclass = CustomTestResult

if __name__ == '__main__':
    unittest.main(testRunner=CustomTestRunner())
