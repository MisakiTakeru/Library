import unittest
from factory import Factory
from singletonDatabaseConnect import SingletonDatabaseConnect
from handler import Datahandler
import db_class
import time
#python -m unittest test.py

class TestData(unittest.TestCase):
    def __init__(self):

        self.user_data = {
            "name": "John Doe",
            "address": "1234 Main St",
            "email": "john@doe.com",
            "book_statuses": [db_class.BookStatus(**{"timestamp": 1633027442, "user_id": 1, "book_id": 1, "status_borrowed": False, "status_reserved": False, "status_available": True})]
        }
        self.other_user_data = {
            "name": "Jane Doe",
            "address": "1234 Main St",
            "email": "jane@doe.com",
            "book_statuses": [db_class.BookStatus(**{"timestamp": 1633027442, "user_id": 2, "book_id": 1, "status_borrowed": False, "status_reserved": False, "status_available": True})]
        }

        self.book_data = {
            "isbn": "123",
            "title": "John Book",
            "author": "John Doe",
            "release_date": 1619827200,
            "book_statuses": [db_class.BookStatus(**{"timestamp": 1633027442, "user_id": 1, "book_id": 1, "status_borrowed": False, "status_reserved": False, "status_available": True})]
        }

        self.other_book_data = {
            "isbn": "1234",
            "title": "Jane Book",
            "author": "Jane Doe",
            "release_date": 1619827200,
            "book_statuses": [db_class.BookStatus(**{"timestamp": 1633027442, "user_id": 2, "book_id": 2, "status_borrowed": False, "status_reserved": False, "status_available": True})]
        }

        self.user_data_reserved = {
            "name": "John Doe reserved",
            "address": "1234 Main St",
            "email": "john@doe.com",
            "book_statuses": [db_class.BookStatus(**{"timestamp": 1633027442, "user_id": 1, "book_id": 1, "status_borrowed": True, "status_reserved": True, "status_available": False})]
        }

        self.book_data_reserved = {
            "isbn": "1234",
            "title": "John Book",
            "author": "John Doe",
            "release_date": 1619827200,
            "book_statuses": [db_class.BookStatus(**{"timestamp": 1633027442, "user_id": 1, "book_id": 1, "status_borrowed": True, "status_reserved": True, "status_available": False})]
        }

        self.user_data_borrowed = {
            "name": "John Doe",
            "address": "1234 Main St",
            "email": "john@doe.com",
            "book_statuses": [db_class.BookStatus(**{"timestamp": 1633027442, "user_id": 1, "book_id": 1, "status_borrowed": True, "status_reserved": False, "status_available": False})]
        }

        self.book_data_borrowed = {
            "isbn": "12345",
            "title": "John Book",
            "author": "John Doe",
            "release_date": 1619827200,
            "book_statuses": [db_class.BookStatus(**{"timestamp": 1633027442, "user_id": 1, "book_id": 1, "status_borrowed": True, "status_reserved": False, "status_available": False})]
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
        self.user_data_reserved = self.data.user_data_reserved
        self.book_data_reserved = self.data.book_data_reserved
        self.user_data_borrowed = self.data.user_data_borrowed
        self.book_data_borrowed = self.data.book_data_borrowed

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
    
    def test_insert_user(self):
        factory = Factory("user")
        user = factory.create(self.user_data)
        session = self.db.get_session()
        engine = self.db.get_engine()

        db_class.User.metadata.create_all(engine) #create table

        session.add(user)
        session.commit()

        self.assertTrue(user.id)
    
    def test_insert_book(self):
        factory = Factory("book")
        book = factory.create(self.book_data)
        session = self.db.get_session()
        engine = self.db.get_engine()

        db_class.Book.metadata.create_all(engine)

        session.add(book)
        session.commit()

        self.assertTrue(book.id)

    ###########
    # Test reserve_book
    ###########
    def test_reserve_book(self):
        book = Factory("book").create(self.book_data_borrowed)
        user = Factory("user").create(self.user_data_borrowed)
        other_user = Factory("user").create(self.other_user_data) 
        session = self.db.get_session()
        engine = self.db.get_engine()
        handler = Datahandler(session, engine)

        db_class.Book.metadata.create_all(engine)
        db_class.User.metadata.create_all(engine)
        session.add(book)
        session.add(user)
        session.add(other_user) 
        session.commit()
        book_status = db_class.BookStatus(timestamp=int(time.time()), user_id=other_user.id, book_id=book.id, status_borrowed=True, status_reserved=False, status_available=False)
        session.add(book_status)
        session.commit()

        self.assertTrue(book.id)
        self.assertTrue(user.id)

        handler.reserve_book(book.isbn, user.id)

        reserved_book_status = session.query(db_class.BookStatus).filter_by(book_id=book.id, user_id=user.id).first()
        self.assertEqual(reserved_book_status.status_borrowed, True)
        self.assertEqual(reserved_book_status.status_reserved, True)
        self.assertEqual(reserved_book_status.status_available, False)

        #cleanup
        session.query(db_class.BookStatus).delete()
        session.query(db_class.Book).delete()
        session.query(db_class.User).delete()
        session.commit()
    
    def test_reserve_book_not_available(self):
        book = Factory("book").create(self.book_data_reserved)
        user = Factory("user").create(self.user_data) 
        session = self.db.get_session()
        engine = self.db.get_engine()
        handler = Datahandler(session, engine)

        db_class.Book.metadata.create_all(engine)
        db_class.User.metadata.create_all(engine)
        session.add(book)
        session.add(user)
        session.commit()

        self.assertTrue(book.id)
        self.assertTrue(user.id)

        with self.assertRaises(ValueError):
            handler.reserve_book(book.isbn, user.id)

        #cleanup
        session.query(db_class.BookStatus).delete()
        session.query(db_class.Book).delete()
        session.query(db_class.User).delete()
        session.commit()
    
    def test_reserve_book_already_reserved(self):
        book = Factory("book").create(self.book_data_reserved)
        user = Factory("user").create(self.user_data_reserved) 
        session = self.db.get_session()
        engine = self.db.get_engine()
        handler = Datahandler(session, engine)

        db_class.Book.metadata.create_all(engine)
        db_class.User.metadata.create_all(engine)
        session.add(book)
        session.add(user)
        session.commit()

        self.assertTrue(book.id)
        self.assertTrue(user.id)

        with self.assertRaises(ValueError):
            handler.reserve_book(book.isbn, user.id)

        #cleanup
        session.query(db_class.BookStatus).delete()
        session.query(db_class.Book).delete()
        session.query(db_class.User).delete()
        session.commit()
        
    def test_reserve_book_available(self):
        book = Factory("book").create(self.book_data)
        user = Factory("user").create(self.user_data) 
        session = self.db.get_session()
        engine = self.db.get_engine()
        handler = Datahandler(session, engine)

        db_class.Book.metadata.create_all(engine)
        db_class.User.metadata.create_all(engine)
        session.add(book)
        session.add(user)
        session.commit()

        self.assertTrue(book.id)
        self.assertTrue(user.id)

        # make book available
        handler.update_book_status(book.id, user.id, status_borrowed=False, status_reserved=False, status_available=True)

        with self.assertRaises(ValueError):
            handler.reserve_book(book.isbn, user.id)

        #cleanup
        session.query(db_class.BookStatus).delete()
        session.query(db_class.Book).delete()
        session.query(db_class.User).delete()
        session.commit()

    
    #test_borrow_first_available_book_of_multiple_copies
    #test_borrow_book_all_copies_borrowed
        
    def test_borrow_fist_available_book_of_multiple_copies(self):
        book1 = Factory("book").create(self.book_data)
        book2 = Factory("book").create(self.book_data)
        user = Factory("user").create(self.user_data)
        session = self.db.get_session()
        engine = self.db.get_engine()
        handler = Datahandler(session, engine)

        db_class.Book.metadata.create_all(engine)
        db_class.User.metadata.create_all(engine)
        session.add(book1)
        session.add(book2)
        session.add(user)
        session.commit()
        
        handler.borrow_book(book1.isbn, user.id)

        borrowed_book_status = session.query(db_class.BookStatus).filter_by(book_id=book1.id, user_id=user.id).first()
        self.assertEqual(borrowed_book_status.status_borrowed, True)
        self.assertEqual(borrowed_book_status.status_reserved, False)
        self.assertEqual(borrowed_book_status.status_available, False)

        #cleanup
        session.query(db_class.BookStatus).delete()
        session.query(db_class.Book).delete()
        session.query(db_class.User).delete()
        session.commit()
    
    def test_reserve_book_all_copies_reserved(self):
        book1 = Factory("book").create(self.book_data_reserved)
        book2 = Factory("book").create(self.book_data_reserved)
        user = Factory("user").create(self.user_data_reserved) 
        session = self.db.get_session()
        engine = self.db.get_engine()
        handler = Datahandler(session, engine)

        db_class.Book.metadata.create_all(engine)
        db_class.User.metadata.create_all(engine)
        session.add(book1)
        session.add(book2)
        session.add(user)
        session.commit()

        self.assertTrue(book1.id)
        self.assertTrue(user.id)

        with self.assertRaises(ValueError):
            handler.reserve_book(book1.isbn, user.id)

        #cleanup
        session.query(db_class.BookStatus).delete()
        session.query(db_class.Book).delete()
        session.query(db_class.User).delete()
        session.commit()
    
    ###########
    # Test return_book
    ###########
    def test_return_book(self):
        book = Factory("book").create(self.book_data_borrowed)
        user = Factory("user").create(self.user_data_borrowed)
        session = self.db.get_session()
        engine = self.db.get_engine()
        handler = Datahandler(session, engine)

        db_class.Book.metadata.create_all(engine)
        db_class.User.metadata.create_all(engine)
        session.add(book)
        session.add(user)
        session.commit()

        self.assertTrue(book.id)
        self.assertTrue(user.id)

        borrowed_book_status_before = session.query(db_class.BookStatus).filter_by(book_id=book.id, user_id=user.id).first()
        self.assertEqual(borrowed_book_status_before.status_borrowed, True)
        self.assertEqual(borrowed_book_status_before.status_reserved, False)
        self.assertEqual(borrowed_book_status_before.status_available, False)

        handler.return_book(book.id, user.id)

        borrowed_book_status_after = session.query(db_class.BookStatus).filter_by(book_id=book.id, user_id=user.id).first()
        self.assertEqual(borrowed_book_status_after.status_borrowed, False)
        self.assertEqual(borrowed_book_status_after.status_reserved, False)
        self.assertEqual(borrowed_book_status_after.status_available, True)

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
        session.add(book)
        session.add(user)
        session.commit()

        self.assertTrue(book.id)
        self.assertTrue(user.id)

        with self.assertRaises(ValueError):
            handler.return_book(book.id, user.id)

        #cleanup
        session.query(db_class.BookStatus).delete()
        session.query(db_class.Book).delete()
        session.query(db_class.User).delete()
        session.commit()

    ###########
    # Test borrow_book
    ###########
    def test_borrow_book(self):
        book = Factory("book").create(self.book_data)
        user = Factory("user").create(self.user_data)
        session = self.db.get_session()
        engine = self.db.get_engine()
        handler = Datahandler(session, engine)

        db_class.Book.metadata.create_all(engine)
        db_class.User.metadata.create_all(engine)
        session.add(book)
        session.add(user)
        session.commit()

        self.assertTrue(book.id)
        self.assertTrue(user.id)

        borrowed_book_status_before = session.query(db_class.BookStatus).filter_by(book_id=book.id, user_id=user.id).first()
        self.assertEqual(borrowed_book_status_before.status_borrowed, False)
        self.assertEqual(borrowed_book_status_before.status_reserved, False)
        self.assertEqual(borrowed_book_status_before.status_available, True)

        handler.borrow_book(book.isbn, user.id)

        borrowed_book_status_after = session.query(db_class.BookStatus).filter_by(book_id=book.id, user_id=user.id).first()
        self.assertEqual(borrowed_book_status_after.status_borrowed, True)
        self.assertEqual(borrowed_book_status_after.status_reserved, False)
        self.assertEqual(borrowed_book_status_after.status_available, False)

        #cleanup
        session.query(db_class.BookStatus).delete()
        session.query(db_class.Book).delete()
        session.query(db_class.User).delete()
        session.commit()
    
    def test_borrow_book_not_available(self):
        book = Factory("book").create(self.book_data_reserved)
        user = Factory("user").create(self.user_data_reserved)
        session = self.db.get_session()
        engine = self.db.get_engine()
        handler = Datahandler(session, engine)

        db_class.Book.metadata.create_all(engine)
        db_class.User.metadata.create_all(engine)
        session.add(book)
        session.add(user)
        session.commit()

        self.assertTrue(book.id)
        self.assertTrue(user.id)

        with self.assertRaises(ValueError):
            handler.borrow_book(book.isbn, user.id)

        #cleanup
        session.query(db_class.BookStatus).delete()
        session.query(db_class.Book).delete()
        session.query(db_class.User).delete()
        session.commit()

    def test_borrow_first_available_book_of_multiple_copies(self):
        book1 = Factory("book").create(self.book_data)
        book2 = Factory("book").create(self.book_data)
        user = Factory("user").create(self.user_data)
        session = self.db.get_session()
        engine = self.db.get_engine()
        handler = Datahandler(session, engine)

        db_class.Book.metadata.create_all(engine)
        db_class.User.metadata.create_all(engine)
        session.add(book1)
        session.add(book2)
        session.add(user)
        session.commit()
        
        handler.borrow_book(book1.isbn, user.id)

        borrowed_book_status = session.query(db_class.BookStatus).filter_by(book_id=book1.id, user_id=user.id).first()
        self.assertEqual(borrowed_book_status.status_borrowed, True)
        self.assertEqual(borrowed_book_status.status_reserved, False)
        self.assertEqual(borrowed_book_status.status_available, False)

        #cleanup
        session.query(db_class.BookStatus).delete()
        session.query(db_class.Book).delete()
        session.query(db_class.User).delete()

    
    def test_borrow_book_already_borrowed_by_yourself(self):
        book = Factory("book").create(self.book_data)
        user = Factory("user").create(self.user_data)
        session = self.db.get_session()
        engine = self.db.get_engine()
        handler = Datahandler(session, engine)

        db_class.Book.metadata.create_all(engine)
        db_class.User.metadata.create_all(engine)
        session.add(book)
        session.add(user)
        session.commit()

        # Borrow the book once
        handler.borrow_book(book.isbn, user.id)

        # Try to borrow the book again and expect a ValueError
        with self.assertRaises(ValueError):
            handler.borrow_book(book.isbn, user.id)

        #cleanup
        session.query(db_class.BookStatus).delete()
        session.query(db_class.Book).delete()
        session.query(db_class.User).delete()
        session.commit()

    def test_borrow_book_all_copies_borrowed(self):
        book1 = Factory("book").create(self.book_data)
        book2 = Factory("book").create(self.book_data)  
        user1 = Factory("user").create(self.user_data)
        user2 = Factory("user").create(self.other_user_data)
        session = self.db.get_session()
        engine = self.db.get_engine()
        handler = Datahandler(session, engine)

        db_class.Book.metadata.create_all(engine)
        db_class.User.metadata.create_all(engine)
        session.add(book1)
        session.add(book2)
        session.add(user1)
        session.add(user2)
        session.commit()

        # Borrow both copies of the book
        handler.borrow_book(book1.isbn, user1.id)
        handler.borrow_book(book2.isbn, user2.id)

        # Try to borrow the book again and expect a ValueError
        with self.assertRaises(ValueError):
            handler.borrow_book(book1.isbn, user1.id)

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
