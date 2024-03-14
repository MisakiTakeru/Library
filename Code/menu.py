from faker import Faker as fk
from handler import Datahandler
from singletonDatabaseConnect import SingletonDatabaseConnect
import db_class

class Menu:
    def __init__(self):
        self.db_url = "sqlite:///:memory:"
        self.db = SingletonDatabaseConnect(self.db_url)
        self.session = self.db.get_session()
        self.engine = self.db.get_engine()
        self.handler = Datahandler(self.session, self.engine)
        # Create tables
        db_class.Book.metadata.create_all(self.engine)
        db_class.User.metadata.create_all(self.engine)
        db_class.BookStatus.metadata.create_all(self.engine)

    def print_menu(self):
        print("1. Select Book by ID")
        print("2. Select Book by Title")
        print("3. Borrow Book")
        print("4. Return Book")
        print("5. Reserve Book")
        print("6. Add user")
        print("7. Add book")
        print("8. Generate Fake Users")
        print("9. Generate Fake Books")
        print("0. Exit")
    
    def print_login_menu(self):
        print("1. Select User by ID")
        print("2. Select User by Name")
        print("3. Add and use user")

    def generate_fake_users(self, amount):
        try:
            amount = int(amount)
        except ValueError:
            return "Invalid input. Please enter a valid integer."
        
        fake = fk()
        for _ in range(amount):
            name = fake.name()
            address = fake.address()
            email = fake.email()
            self.handler.add_user(name, address, email)
        return f"{amount} users added"

    def generate_fake_books(self, amount):
        try:
            amount = int(amount)
        except ValueError:
            return "Invalid input. Please enter a valid integer."
        
        fake = fk()
        for _ in range(amount):
            isbn = fake.isbn13()
            title = fake.sentence()
            author = fake.name()
            release_date = fake.date()
            self.handler.add_book(isbn, title, author, release_date)
        return f"{amount} books added"

menu_options = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9" "x"]
login_menu_options = ["0", "1", "2", "3"]

while True:
    m = Menu()
    user = None
    if user is not None:
        m.print_menu()
    else:
        m.print_login_menu()
    choice = input("Enter choice: ")

    if user is None: # User is not logged in
        if choice not in login_menu_options:
            print("Invalid choice")
            continue
        if choice == "0": # Exit
            break

        if choice == "1": # Select user by ID
            user_id = input("Enter user ID: ")
            user = m.handler.get_user_by_id(user_id)
            print(f"Welcome {user.name}")

        if choice == "2": # Select user by name
            name = input("Enter user name: ")
            user = m.handler.get_user_by_name(name)
            print(f"Welcome {user.name}")

        if choice == "3": # Add and use user
            name = input("Enter user name: ")
            address = input("Enter user address: ")
            email = input("Enter user email: ")
            m.handler.add_user(name, address, email)
            user = m.handler.get_user_by_name(name)
            print(f"Welcome {user.name}")
    else: # User is logged in
        if choice not in menu_options:
            print("Invalid choice")
            continue
        if choice == "0": # Exit
            break
        if choice == "x": # Logout
            print(f"Logged out of {user.name}")
            user = None
            continue

        if choice == "1": # Select book by ID
            book_id = input("Enter book ID: ")
            book = m.handler.get_book_by_id(book_id)
            print(f"Book title: {book.title}")
            print(f"Book author: {book.author}")
            print(f"Book release date: {book.release_date}")
            print(f"Book status: {m.handler.get_book_status(book_id)}")
        
        if choice == "2": # Select book by title
            book_title = input("Enter book title: ")
            books = m.handler.get_book_by_title(book_title)
            for book in books:
                print(f"Book title: {book.title}")
                print(f"Book author: {book.author}")
                print(f"Book release date: {book.release_date}")
                print(f"Book status: {m.handler.get_book_status(book.id)}")

        if choice == "3": # Borrow book
            user_id = user.id
            book_isbn = input("Enter book ISBN: ")
            m.handler.borrow_book(book_isbn, user_id)

        if choice == "4": # Return book
            user_id = user.id
            book_id = input("Enter book ID: ")
            m.handler.return_book(book_id, user_id)

        if choice == "5": # Reserve book
            user_id = user.id
            book_isbn = input("Enter book ISBN: ")
            m.handler.reserve_book(book_isbn, user_id)
        
        if choice == "6": # Add user
            name = input("Enter user name: ")
            address = input("Enter user address: ")
            email = input("Enter user email: ")
            m.handler.add_user(name, address, email)
        
        if choice == "7": # Add book
            isbn = input("Enter book ISBN: ")
            title = input("Enter book title: ")
            author = input("Enter book author: ")
            release_date = input("Enter book release date: ")
            m.handler.add_book(isbn, title, author, release_date)

        if choice == "8": # Generate fake users
            amount = input("Enter amount of users to generate: ")
            print(m.generate_fake_users(amount))

        if choice == "9": # Generate fake books
            amount = input("Enter amount of books to generate: ")
            print(m.generate_fake_books(amount))