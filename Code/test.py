import unittest
from factory import Factory
from singletonDatabaseConnect import SingletonDatabaseConnect
from handler import Datahandler
#python -m unittest test.py

class TestData(unittest.TestCase):
    def __init__(self):
        self.user_data = {
            "name": "John Doe",
            "address": "1234 Main St",
            "email": "john@doe.com",
            "borrowed": [1], #list of borrowed book id
        }

        self.book_data = {
            "isbn": "1234567890",
            "title": "John Book",
            "author": "John Doe",
            "release_date": 1619827200,
            "borrow_by": 1,
            "borrow_status": True
        }

class TestSingletonDatabaseConnect(unittest.TestCase):
    def setUp(self) -> None:
        self.db_url = "sqlite:///:memory:"
        self.db = SingletonDatabaseConnect(self.db_url)
        self.data = TestData()
        self.user_data = self.data.user_data
        self.book_data = self.data.book_data

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

        type(user).metadata.create_all(engine) #create table

        session.add(user)
        session.commit()

        self.assertTrue(user.id)
    
    def test_insert_book(self):
        factory = Factory("book")
        book = factory.create(self.book_data)
        session = self.db.get_session()
        engine = self.db.get_engine()

        type(book).metadata.create_all(engine)

        session.add(book)
        session.commit()

        self.assertTrue(book.id)
    
    def test_return_book(self):
        book = Factory("book").create(self.book_data)
        user = Factory("user").create(self.user_data)
        session = self.db.get_session()
        engine = self.db.get_engine()
        handler = Datahandler(session, engine)

        #delete all books
        session.query(type(book)).delete()

        type(book).metadata.create_all(engine)
        session.add(book)
        session.commit()

        type(user).metadata.create_all(engine)
        session.add(user)
        session.commit()

        self.assertTrue(book.borrow_status)

        handler.return_book(book.id)   

        book = session.query(type(book)).filter_by(id = book.id).first()
        self.assertFalse(book.borrow_status)
        self.assertEqual(book.borrow_by, 0)

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