from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    "postgresql+psycopg2://postgres:devika@localhost:5432/company"
)

Base = declarative_base()

class Book(Base):

    __tablename__ = "books"

    book_id = Column(Integer, primary_key=True)

    title = Column(String(100))

    author = Column(String(100))

    count = Column(Integer)

    book_type = Column(String(30))

    issue_month = Column(String(30))

    subject = Column(String(30))

    section = Column(String(30))



class User(Base):

    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)

    name = Column(String(100))


class BorrowedBook(Base):

    __tablename__ = "borrowed_books"

    borrow_id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.user_id"))

    book_id = Column(Integer, ForeignKey("books.book_id"))


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

print("Connected to PostgreSQL using SQLAlchemy!")



#creating library


class Library:

    def __init__(self):
        self.session = session

    def add_book(self):
        book_id = int(input("Enter Book ID: "))
        title = input("Enter Title: ")
        author = input("Enter Author: ")
        count = int(input("Enter Count: "))

        print("\nBook Types:")
        print("1. Normal Book")
        print("2. Magazine")
        print("3. Text Book")
        print("4. Reference Book")

        choice = input("Enter Book Type: ")

        if choice == "2":
            issue_month = input("Enter Issue Month: ")
            book = Book(
                book_id=book_id,
                title=title,
                author=author,
                count=count,
                book_type="Magazine",
                issue_month=issue_month
            ) 

        elif choice == "3":
            subject = input("Enter Subject: ")
            book = Book(
                book_id=book_id,
                title=title,
                author=author,
                count=count,
                book_type="TextBook",
                subject=subject
            )

        elif choice == "4":
            section = input("Enter Section: ")
            book = Book(
                book_id=book_id,
                title=title,
                author=author,
                count=count,
                book_type="ReferenceBook",
                section=section
            )

        else:
            book = Book(
                book_id=book_id,
                title=title,
                author=author,
                count=count,
                book_type="Book"
            )

        self.session.add(book)
        self.session.commit()

        print("Book Added Successfully!")


    def add_user(self):
        user_id = int(input("Enter User ID: "))
        name = input("Enter User Name: ")

        existing_user = self.session.query(User).filter_by(user_id=user_id).first()

        if existing_user:
            print("User ID already exists!")
            return

        user = User(
            user_id=user_id,
            name=name
        )

        self.session.add(user)
        self.session.commit()

        print("User Added Successfully!")


    def view_books(self):
        books = self.session.query(Book).all()

        if not books:
            print("No Books Available!")
            return

        for book in books:
            print("-" * 50)
            print(f"Book ID   : {book.book_id}")
            print(f"Title     : {book.title}")
            print(f"Author    : {book.author}")
            print(f"Count     : {book.count}")
            print(f"Type      : {book.book_type}")

            if book.issue_month:
                print(f"Issue Month : {book.issue_month}")

            if book.subject:
                print(f"Subject     : {book.subject}")

            if book.section:
                print(f"Section     : {book.section}")



    def borrow_book(self):
        user_id = int(input("Enter User ID: "))
        book_id = int(input("Enter Book ID: "))

        user = self.session.query(User).filter_by(user_id=user_id).first()

        if not user:
            print("User Not Found!")
            return

        book = self.session.query(Book).filter_by(book_id=book_id).first()

        if not book:
            print("Book Not Found!")
            return

        if book.count <= 0:
            print("Book Not Available!")
            return

        borrow = BorrowedBook(
            user_id=user_id,
            book_id=book_id
        )

        book.count -= 1

        self.session.add(borrow)
        self.session.commit()

        print("Book Borrowed Successfully!")


    def return_book(self):
        user_id = int(input("Enter User ID: "))
        book_id = int(input("Enter Book ID: "))

        borrow = self.session.query(BorrowedBook).filter_by(
            user_id=user_id,
            book_id=book_id
        ).first()

        if not borrow:
            print("This User Didn't Borrow This Book!")
            return

        book = self.session.query(Book).filter_by(book_id=book_id).first()

        if book:
            book.count += 1

        self.session.delete(borrow)
        self.session.commit()

        print("Book Returned Successfully!")

        late_days = int(input("Enter Late Days (0 if returned on time): "))

        if book.book_type == "Magazine":
            fine_per_day = 1
        elif book.book_type == "TextBook":
            fine_per_day = 5
        elif book.book_type == "ReferenceBook":
            fine_per_day = 10
        else:
            fine_per_day = 2

        fine = late_days * fine_per_day

        print("Fine Amount =", fine)


    def search_book(self):
        keyword = input("Enter Book Title: ")

        books = self.session.query(Book).filter(
            Book.title.ilike(f"%{keyword}%")
        ).all()

        if not books:
            print("Book Not Found!")
            return

        for book in books:
            print("-" * 40)
            print("Book ID:", book.book_id)
            print("Title:", book.title)
            print("Author:", book.author)
            print("Count:", book.count)
            print("Type:", book.book_type)

            if book.issue_month:
                print("Issue Month:", book.issue_month)

            if book.subject:
                print("Subject:", book.subject)

            if book.section:
                print("Section:", book.section)

    def user_details(self):
        user_id = int(input("Enter User ID: "))

        user = self.session.query(User).filter_by(user_id=user_id).first()

        if not user:
            print("User Not Found!")
            return

        print("\n===== USER DETAILS =====")
        print("User ID:", user.user_id)
        print("User Name:", user.name)

        borrowed_books = self.session.query(BorrowedBook).filter_by(user_id=user_id).all()

        if not borrowed_books:
            print("No Books Borrowed")
            return

        print("Borrowed Books:")

        for borrow in borrowed_books:
            book = self.session.query(Book).filter_by(book_id=borrow.book_id).first()

            if book:
                print(f"{book.title} ({book.book_type})")     

    def library_statistics(self):
        total_books = self.session.query(Book).count()

        total_users = self.session.query(User).count()

        borrowed_books = self.session.query(BorrowedBook).count()

        books = self.session.query(Book).all()

        available_books = 0

        for book in books:
            available_books += book.count

        print("\n===== LIBRARY STATISTICS =====")
        print("Total Different Books:", total_books)
        print("Available Copies:", available_books)
        print("Borrowed Books:", borrowed_books)
        print("Total Users:", total_users)


library = Library()

while True:
    print("\n===== LIBRARY MANAGEMENT SYSTEM =====")
    print("1. Add Book")
    print("2. Add User")
    print("3. View Books")
    print("4. Borrow Book")
    print("5. Return Book")
    print("6. Search Book")
    print("7. User Details")
    print("8. Library Statistics")
    print("9. Exit")

    choice = input("Enter Your Choice: ")

    if choice == "1":
        library.add_book()

    elif choice == "2":
        library.add_user()

    elif choice == "3":
        library.view_books()

    elif choice == "4":
        library.borrow_book()

    elif choice == "5":
        library.return_book()

    elif choice == "6":
        library.search_book()

    elif choice == "7":
        library.user_details()

    elif choice == "8":
        library.library_statistics()

    elif choice == "9":
        session.close()
        print("Database connection closed.")
        print("Exiting Library System...")
        break

    else:
        print("Invalid Choice!")





            








