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
            "isbn" : "12359",
            "title" : "A hitchhikers guide 2",
            "author" : "Space Traveler A",
            "release_date" : 27041100,
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
        session.add(book1)
        session.add(book2)
        session.add(book3)
        
        session.commit()

        type(user2).metadata.create_all(engine)
        session.add(user1)
        session.add(user2)
        session.commit()

        self.assertTrue(book1.borrow_status)

        handler.return_book(book1.id)   

        book1 = session.query(type(book1)).filter_by(id = book1.id).first()
        self.assertFalse(book1.borrow_status)
        self.assertEqual(book1.borrow_by, 0)

        #test return book of failing example
        #book should not be able to return a book that is not borrowed
        with self.assertRaises(ValueError) as context:
            handler.return_book(book1.id)  # try to return the same book again
        self.assertTrue(f"Book with id {book1.id} is not borrowed" in str(context.exception))

        #book should not be able to return a book that is not in user's borrowed list
        book1.borrow_status = True
        book1.borrow_by = 1
        user1.borrowed = []
        with self.assertRaises(ValueError) as context:
            handler.return_book(book1.id)  # try to return a book that is not in user1's borrowed list
        self.assertTrue(f"Book with id {book1.id} is not in user borrowed list" in str(context.exception))

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
        session.add(book1)
        session.add(book2)
        session.add(book3)
        
        session.commit()

        type(user2).metadata.create_all(engine)
        session.add(user1)
        session.add(user2)
        session.commit()

        #test reserve book of working example
        self.assertFalse(book3.isbn in user2.reserved)
        handler.reserve_book(book3.isbn, user2.id)
        user = session.query(db_class.User).filter_by(id = user2.id).first()
        self.assertTrue(book3.isbn in user.reserved)

        #test reserve book of failing example
        #user should not be able to reserve a book he has already reserved
        with self.assertRaises(ValueError) as context:
            handler.reserve_book(book3.isbn, user2.id)  
        self.assertTrue(f"Book with isbn {book3.isbn} is already reserved by user with id {user2.id}" in str(context.exception))

        #user should not be able to reserve a book thats alwayable for borrowing
        with self.assertRaises(ValueError) as context:
            handler.reserve_book(book2.isbn, user1.id)
        self.assertTrue(f"Book with isbn {book2.isbn} is available for borrowing" in str(context.exception))

        #user should not be able to reserve a book he has already borrowed
        with self.assertRaises(ValueError) as context:
            handler.reserve_book(book1.isbn, user1.id)
        self.assertTrue(f"User with id {user1.id} has already borrowed book with id {book1.id}" in str(context.exception))

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
