import unittest
from factory import Factory
from singletonDatabaseConnect import SingletonDatabaseConnect
from handler import Datahandler
import db_class
#python -m unittest test.py

class TestData(unittest.TestCase):
    def __init__(self):
        self.user_data = {
            "name": "John Doe",
            "address": "1234 Main St",
            "email": "john@doe.com",
            "borrowed": [1], #list of borrowed book id
        }
        
        self.user_data2 = {
            "name" : "The hitchhiker",
            "address" : "space station Omega 2",
            "email" : "plsaddme@spac.moon",
            "borrowed" : []}

        self.book_data = {
            "isbn": "1234567890",
            "title": "John Book",
            "author": "John Doe",
            "release_date": 1619827200,
            "borrow_by": 1,
            "borrow_status": True
        }
        
        self.book_data2 = {
            "isbn" : "12358",
            "title" : "A hitchhikers guide",
            "author" : "Space Traveler A",
            "release_date" : 27041995,
            "borrow_by" : 0,
            "borrow_status" : False
        }

        self.book_data3 = {
            "isbn" : "12358",
            "title" : "A hitchhikers guide",
            "author" : "Space Traveler A",
            "release_date" : 27041995,
            "borrow_by" : 10,
            "borrow_status" : True
        }

class TestSingletonDatabaseConnect(unittest.TestCase):
    def setUp(self) -> None:
        self.db_url = "sqlite:///:memory:"
        self.db = SingletonDatabaseConnect(self.db_url)
        self.data = TestData()
        self.user_data = self.data.user_data
        self.user_data2 = self.data.user_data2
        self.book_data = self.data.book_data
        self.book_data2 = self.data.book_data2
        self.book_data3 = self.data.book_data3

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

        #delete tables
        session.query(type(book)).delete()
        session.query(type(user)).delete()

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

    def test_borrow_book(self):
        book2 = Factory("book").create(self.book_data2)
        user2 = Factory("user").create(self.user_data2)
        borrow = "A hitchhikers guide"
        uid = 1
        session = self.db.get_session()
        engine = self.db.get_engine()
        handler = Datahandler(session, engine)


        type(book2).metadata.create_all(engine)
        session.add(book2)
        session.commit()

        book2 = Factory("book").create(self.book_data2)
        type(book2).metadata.create_all(engine)
        session.add(book2)
        session.commit()

        type(user2).metadata.create_all(engine)
        session.add(user2)
        session.commit()

        handler.borrow(borrow, uid)
       
        bookt = session.query(db_class.Book).filter_by(title = borrow).first()
        self.assertTrue(bookt.borrow_status)
       
        handler.borrow(borrow, uid)
       
        usert = session.query(db_class.User).first()
        self.assertEqual(usert.borrowed, [1,2])
       
        fail = handler.borrow(borrow, uid)
        self.assertEqual(fail, f'all versions of the book {borrow} has been borrowed.')

    def test_reserve_book(self):
        book3 = Factory("book").create(self.book_data3)
        book2 = Factory("book").create(self.book_data2)
        book1 = Factory("book").create(self.book_data)
        user1 = Factory("user").create(self.user_data)
        user2 = Factory("user").create(self.user_data2)
        session = self.db.get_session()
        engine = self.db.get_engine()
        handler = Datahandler(session, engine)

        #delete tables
        session.query(type(book3)).delete()
        session.query(type(user2)).delete()

        type(book3).metadata.create_all(engine)
        session.add(book3)
        session.commit()

        type(user2).metadata.create_all(engine)
        session.add(user2)
        session.commit()

        #test reserve book of working example
        self.assertFalse(book3.isbn in user2.reserved)
        handler.reserve_book(book3.isbn, user2.id)
        user = session.query(db_class.User).filter_by(id = user2.id).first()
        self.assertTrue(book3.isbn in user.reserved)


        
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
