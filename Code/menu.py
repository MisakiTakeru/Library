from faker import Faker as fk
from handler import Datahandler
from singletonDatabaseConnect import SingletonDatabaseConnect
import db_class
import os

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
        print("10. Get all my borrowed books")
        print("11. Get all my reserved books")
        print("12. Get all books")
        print("13. Get all users")
        print("x. Logout")
        print("0. Exit")
    
    def print_login_menu(self):
        print("1. Select User by ID")
        print("2. Select User by Name")
        print("3. Add and use user")
        print("4. Get all users")
        print("8. Generate Fake Users")
        print("9. Generate Fake Books")
        print("0. Exit")

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

menu_options = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "x"]
login_menu_options = ["0", "1", "2", "3", "4", "8", "9"]

m = Menu()
user = None

print_result = []

while True:
    os.system("cls")
    try:
        for result in print_result:
            print(result)
            print_result=[]
        print("\n")
        if user is not None:
            m.print_menu()
        else:
            m.print_login_menu()

        choice = input("Enter choice: ")

        if user is None: # User is not logged in
            if choice not in login_menu_options:
                print_result.append("Invalid choice")
                continue
            if choice == "0": # Exit
                break

            if choice == "1": # Select user by ID
                user_id = input("Enter user ID: ")
                user = m.handler.get_user_by_id(user_id)
                if user is not None:
                    print_result.append(f"Welcome {user['name']}")
                else:
                    print_result.append("User not found")

            if choice == "2": # Select user by name
                name = input("Enter user name: ")
                user = m.handler.get_user_by_name(name)
                if user is not None:
                    print_result.append(f"Welcome {user['name']}")
                else:
                    print_result.append("User not found")

            if choice == "3": # Add and use user
                name = input("Enter user name: ")
                address = input("Enter user address: ")
                email = input("Enter user email: ")
                m.handler.add_user(name, address, email)
                user = m.handler.get_user_by_name(name)
                print_result.append(f"Welcome {user['name']}")
            
            if choice == "4": # Get all users
                users = m.handler.get_all_users()
                if users is not None:
                    for u in users:
                        print_result.append(f"User ID: {u['id']}")
                        print_result.append(f"User name: {u['name']}")
                        print_result.append(f"User address: {u['address']}")
                        print_result.append(f"User email: {u['email']}")
                        print_result.append("\n")
                else:
                    print_result.append("No users found.")

            if choice == "8": # Generate fake users
                amount = input("Enter amount of users to generate: ")
                print_result.append(m.generate_fake_users(amount))

            if choice == "9": # Generate fake books
                amount = input("Enter amount of books to generate: ")
                print_result.append(m.generate_fake_books(amount))

        else: # User is logged in
            if choice not in menu_options:
                print_result.append("Invalid choice")
                continue
            if choice == "0": # Exit
                break
            if choice == "x": # Logout
                print_result.append(f"Logged out of {user['name']}")
                user = None
                continue

            if choice == "1": # Select book by ID
                book_id = input("Enter book ID: ")
                book = m.handler.get_book_by_id(book_id)
                book_status = m.handler.get_book_status_by_id(book_id)
                print_result.append(f"Book title: {book['title']}")
                print_result.append(f"Book author: {book['author']}")
                print_result.append(f"Book release date: {book['release_date']}")
                print_result.append(f"Book ISBN: {book['isbn']}")
                print_result.append(f"Book borrowed: {book_status['status_borrowed']}")
                print_result.append(f"Book reserved: {book_status['status_reserved']}")

            if choice == "2": # Select book by title
                book_title = input("Enter book title: ")
                books = m.handler.get_book_by_title(book_title)
                book_id = books[0]['id']
                books_status = m.handler.get_book_status_by_id(book_id)
                for book in books:
                    print_result.append(f"Book title: {book['title']}")
                    print_result.append(f"Book author: {book['author']}")
                    print_result.append(f"Book release date: {book['release_date']}")
                    print_result.append(f"Book ISBN: {book['isbn']}")
                    
            if choice == "3": # Borrow book
                user_id = user['id']
                book_isbn = input("Enter book ISBN: ")
                m.handler.borrow_book(book_isbn, user_id)
                #print book name and who borrowed it
                print_result.append(f"Book with: {book_isbn} borrowed by {user['name']}")

            if choice == "4": # Return book
                user_id = user['id']
                book_id = input("Enter book ID: ")
                m.handler.return_book(book_id, user_id)
                print_result.append(f"Book with ID: {book_id} returned by {user['name']}")

            if choice == "5": # Reserve book
                user_id = user['id']
                book_isbn = input("Enter book ISBN: ")
                m.handler.reserve_book(book_isbn, user_id)
                print_result.append(f"Book with: {book_isbn} reserved by {user['name']}")
            
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
                print_result.append(m.generate_fake_users(amount))

            if choice == "9": # Generate fake books
                amount = input("Enter amount of books to generate: ")
                print_result.append(m.generate_fake_books(amount))
            
            if choice == "10": #Get all borrowed books
                user_id = user['id']
                borrowed_books = m.handler.get_borrowed_books(user_id)
                if borrowed_books is None:
                    print_result.append("No borrowed books.")
                else:
                    for book in borrowed_books:
                        print_result.append(f"Borrowed Book")
                        print_result.append(f"Book ID: {book.id}")
                        print_result.append(f"Book title: {book.title}")
                        print_result.append(f"Book author: {book.author}")
                        print_result.append(f"Book release date: {book.release_date}")
                        print_result.append(f"Book ISBN: {book.isbn}")
                        #print_result.append(f"Borrowed: {book.status_borrowed}")
                        print_result.append("\n")

            if choice == "11": #Get all reserved books
                user_id = user['id']
                reserved_books = m.handler.get_reserved_books(user_id)
                if reserved_books is None:
                    print_result.append("No reserved books.")
                else:
                    for book in reserved_books:
                        print_result.append(f"Reserved Book")
                        print_result.append(f"Book ID: {book.id}")
                        print_result.append(f"Book title: {book.title}")
                        print_result.append(f"Book author: {book.author}")
                        print_result.append(f"Book release date: {book.release_date}")
                        print_result.append(f"Book ISBN: {book.isbn}")
                        #print_result.append(f"Reserved: {book.status_reserved}")
                        print_result.append("\n")

            if choice == "12": # Get all books
                books = m.handler.get_all_books()
                if books is not None:
                    for book in books:
                        print_result.append(f"Book ID: {book['id']}")
                        print_result.append(f"Book title: {book['title']}")
                        print_result.append(f"Book author: {book['author']}")
                        print_result.append(f"Book release date: {book['release_date']}")
                        print_result.append(f"Book ISBN: {book['isbn']}")
                        #status
                        book_status = m.handler.get_book_status_by_id(book['id'])
                        print_result.append(f"Book borrowed: {book_status['status_borrowed']}")
                        print_result.append(f"Book reserved: {book_status['status_reserved']}")
                        print_result.append("\n")
                else:
                    print_result.append("No books found.")
            
            if choice == "13":
                #get all users
                users = m.handler.get_all_users()
                if users is not None:
                    for user in users:
                        print_result.append(f"User ID: {user['id']}")
                        print_result.append(f"User name: {user['name']}")
                        print_result.append(f"User address: {user['address']}")
                        print_result.append(f"User email: {user['email']}")
                        print_result.append("\n")
                else:
                    print_result.append("No users found.")
    except ValueError as e:
        print_result.append(f"{e}")