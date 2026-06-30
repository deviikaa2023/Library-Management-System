from python_conn import conn,cur

class Book:
    def __init__(self, book_id, title, author, count):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.count = count

    def borrow_duration(self):
        return 7

    def fine_per_day(self):
        return 2

    def get_details(self):
        return f"ID:{self.book_id} | Title:{self.title} | Author:{self.author}"


class Magazine(Book):
    def __init__(self, book_id, title, author, count, issue_month):
        super().__init__(book_id, title, author, count)
        self.issue_month = issue_month

    def borrow_duration(self):
        return 10

    def fine_per_day(self):
        return 1

    def get_details(self):
        return (f"ID:{self.book_id} | Title:{self.title} | "
                f"Author:{self.author} | Issue Month:{self.issue_month}")


class TextBook(Book):
    def __init__(self, book_id, title, author, count, subject):
        super().__init__(book_id, title, author, count)
        self.subject = subject

    def borrow_duration(self):
        return 30

    def fine_per_day(self):
        return 5

    def get_details(self):
        return (f"ID:{self.book_id} | Title:{self.title} | "
                f"Author:{self.author} | Subject:{self.subject}")


class ReferenceBook(Book):
    def __init__(self, book_id, title, author, count, section):
        super().__init__(book_id, title, author, count)
        self.section = section

    def borrow_duration(self):
        return 2

    def fine_per_day(self):
        return 10

    def get_details(self):
        return (f"ID:{self.book_id} | Title:{self.title} | "
                f"Author:{self.author} | Section:{self.section}")


class User:
    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name
        self.borrowed_books = []


class Library:
    def __init__(self):
        self.books = []
        self.users = []

    # Add Book
    def add_book(self):
        book_id = int(input("Enter Book ID: "))

        for book in self.books:
            if book.book_id == book_id:
                print("Book ID already exists!")
                return

        title = input("Enter Book Title: ")
        author = input("Enter Author Name: ")
        count = int(input("Enter Number of Copies: "))

        print("\nBook Types")
        print("1. Normal Book")
        print("2. Magazine")
        print("3. TextBook")
        print("4. Reference Book")

        choice = input("Enter Book Type: ")

        # Parent reference pointing to derived object
        book: Book

        if choice == "2":
            issue_month = input("Enter Issue Month: ")
            book = Magazine(book_id, title, author, count, issue_month)

        elif choice == "3":
            subject = input("Enter Subject: ")
            book = TextBook(book_id, title, author, count, subject)

        elif choice == "4":
            section = input("Enter Section: ")
            book = ReferenceBook(book_id, title, author, count, section)

        else:
            book = Book(book_id, title, author, count)

        #self.books.append(book)

        cur.execute("""
        INSERT INTO books
        (book_id,title,author,count,book_type,issue_month,subject,section)
        VALUES(%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (book.book_id,
        book.title,
        book.author,
        book.count,
        type(book).__name__,
        getattr(book,"issue_month",None),
        getattr(book,"subject",None),
        getattr(book,"section",None)))

        conn.commit()

        print("Book Added Successfully")



    
    
    # Add User
    def add_user(self):
        user_id = int(input("Enter User ID: "))

        cur.execute("SELECT * FROM users WHERE user_id=%s", (user_id,))
        if cur.fetchone():
            print("User ID already exists!")
            return

        name = input("Enter User Name: ")

        cur.execute("""
        INSERT INTO users(user_id, name)
        VALUES(%s, %s)
        """, (user_id, name))

        conn.commit()
        print("User Added Successfully!")

        # View Books
    # View Books
    def view_books(self):

        cur.execute("SELECT * FROM books")
        books = cur.fetchall()

        if not books:
            print("No Books Available!")
            return

        print("\n===== BOOK LIST =====")

        for book in books:
            print("Book ID:", book[0])
            print("Title:", book[1])
            print("Author:", book[2])
            print("Available Copies:", book[3])
            print("Book Type:", book[4])

            if book[5]:
                print("Issue Month:", book[5])

            if book[6]:
                print("Subject:", book[6])

            if book[7]:
                print("Section:", book[7])

            print("-" * 50)

    # Borrow Book
    def borrow_book(self):
        user_id = int(input("Enter User ID: "))
        book_id = int(input("Enter Book ID: "))

        cur.execute("SELECT * FROM users WHERE user_id=%s", (user_id,))
        user = cur.fetchone()

        if not user:
            print("User Not Found!")
            return

        cur.execute("SELECT * FROM books WHERE book_id=%s", (book_id,))
        book = cur.fetchone()

        if not book:
            print("Book Not Found!")
            return

        if book[3] > 0:
            cur.execute(
                "UPDATE books SET count=count-1 WHERE book_id=%s",
                (book_id,)
            )

            cur.execute(
                "INSERT INTO borrowed_books(user_id, book_id) VALUES(%s,%s)",
                (user_id, book_id)
            )

            conn.commit()

            print("Book Borrowed Successfully!")

        else:
            print("Book Not Available!")

    
    
    # Return Book
    def return_book(self):
        user_id = int(input("Enter User ID: "))
        book_id = int(input("Enter Book ID: "))

        # Check if the user has borrowed this book
        cur.execute("""
        SELECT * FROM borrowed_books
        WHERE user_id=%s AND book_id=%s
        """, (user_id, book_id))

        borrow = cur.fetchone()

        if not borrow:
            print("This User Didn't Borrow This Book!")
            return

        # Increase the available book count
        cur.execute("""
        UPDATE books
        SET count = count + 1
        WHERE book_id=%s
        """, (book_id,))

        # Delete the borrow record
        cur.execute("""
        DELETE FROM borrowed_books
        WHERE user_id=%s AND book_id=%s
        """, (user_id, book_id))

        conn.commit()

        print("Book Returned Successfully!")

        late_days = int(input("Enter Late Days (0 if returned on time): "))

        # Get fine per day from book type
        cur.execute("""
        SELECT book_type
        FROM books
        WHERE book_id=%s
        """, (book_id,))

        book_type = cur.fetchone()[0]

        if book_type == "Magazine":
            fine_per_day = 1
        elif book_type == "TextBook":
            fine_per_day = 5
        elif book_type == "ReferenceBook":
            fine_per_day = 10
        else:
            fine_per_day = 2

        fine = late_days * fine_per_day

        print("Fine Amount =", fine)


    # Search Book
    # Search Book
    def search_book(self):  
        keyword = input("Enter Book Title: ")

        cur.execute("""
        SELECT * FROM books
        WHERE LOWER(title) LIKE LOWER(%s)
        """, ('%' + keyword + '%',))

        books = cur.fetchall()

        if not books:
            print("Book Not Found!")
            return

        print("\n===== SEARCH RESULTS =====")

        for book in books:
            print("Book ID:", book[0])
            print("Title:", book[1])
            print("Author:", book[2])
            print("Available Copies:", book[3])
            print("Book Type:", book[4])

            if book[5]:
                print("Issue Month:", book[5])

            if book[6]:
                print("Subject:", book[6])

            if book[7]:
                print("Section:", book[7])

            print("-" * 50)

    # User Details
    # User Details
    def user_details(self):
        user_id = int(input("Enter User ID: "))

        # Check if user exists
        cur.execute("SELECT * FROM users WHERE user_id=%s", (user_id,))
        user = cur.fetchone()

        if not user:
            print("User Not Found!")
            return

        print("\n===== USER DETAILS =====")
        print("User ID:", user[0])
        print("User Name:", user[1])

        # Display borrowed books
        cur.execute("""
        SELECT books.title, books.book_type
        FROM borrowed_books
        JOIN books
        ON borrowed_books.book_id = books.book_id
        WHERE borrowed_books.user_id=%s
        """, (user_id,))

        books = cur.fetchall()

        if books:
            print("\nBorrowed Books:")
            for book in books:
                print("Title:", book[0])
                print("Type:", book[1])
                print("-" * 30)
        else:
            print("No Books Borrowed")

    # Library Statistics
    # Library Statistics
    def library_statistics(self):

        # Total different books
        cur.execute("SELECT COUNT(*) FROM books")
        total_books = cur.fetchone()[0]

        # Total available copies
        cur.execute("SELECT SUM(count) FROM books")
        available_books = cur.fetchone()[0]

        if available_books is None:
            available_books = 0

        # Total borrowed books
        cur.execute("SELECT COUNT(*) FROM borrowed_books")
        borrowed_books = cur.fetchone()[0]

        # Total users
        cur.execute("SELECT COUNT(*) FROM users")
        total_users = cur.fetchone()[0]

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
        print("Exiting Library System...")
        break

    else:
        print("Invalid Choice!")

        cur.close()
        conn.close()
        print("Database connection closed....")
        print("Exiting library system....")

        break


