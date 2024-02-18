class Library:
    def __init__(self):
        self.file = open("books.txt", "a+")
        self.history_file = open("history.txt", "a+")
        self.transactions_file = open("transactions.txt", "a+")
        self.logged_in_user = None
        self.admin_users = self.load_admin_users()
        self.normal_users = self.load_normal_users()

    def __del__(self):
        self.file.close()
        self.history_file.close()
        self.transactions_file.close()

    def get_average_ratings(self):
        with open("ratings.txt", "r") as f:
            ratings = f.readlines()

        if not ratings:
            print("There is no rated book yet.")
            return {}

        book_ratings = {}
        for rating in ratings:
            user, title, score = rating.strip().split(',')
            score = int(score)
            if title not in book_ratings:
                book_ratings[title] = [score]
            else:
                book_ratings[title].append(score)

        average_ratings = {}
        for title, scores in book_ratings.items():
            average_rating = sum(scores) / len(scores)
            average_ratings[title] = average_rating

        return average_ratings

    def rate_book(self):
        self.list_borrowed_books()
        title = input("Enter the title of the book to rate: ")
        rating = input("Enter your rating (1-5): ")
        if not rating.isdigit() or int(rating) not in range(1, 6):
            print("Invalid rating. Please enter a number between 1 and 5.")
            return
        rating = int(rating)
        with open("transactions.txt", "r") as f:
            transactions = f.readlines()
        borrowed_by = [transaction.strip().split(',')[1] for transaction in transactions if
                       transaction.strip().split(',')[0] == title]
        if self.logged_in_user in borrowed_by:
            with open("ratings.txt", "r") as f:
                ratings = f.readlines()
            user_ratings = [r.strip().split(',')[1] for r in ratings if r.strip().split(',')[0] == self.logged_in_user]
            if title in user_ratings:
                print("You have already rated this book.")
            else:
                with open("ratings.txt", "a") as f:
                    f.write(f"{self.logged_in_user},{title},{rating}\n")
                print("Thank you for your rating!")
        else:
            print("You can only rate books that you have borrowed.")

    def search_books(self):
        search_term = input("Enter search term (title or author): ").lower()
        found_books = []
        self.file.seek(0)
        for book in self.file:
            name, author, *_ = book.strip().split(',')
            if search_term == name.lower() or search_term == author.lower():
                found_books.append(book.strip())
        if not found_books:
            print("No matching books found.")
        else:
            print("*************************************************************************************")
            for i, book in enumerate(found_books, start=1):
                name, author, release_date, pages, username = book.split(',')
                print(
                    f"{i}) Title: {name}, Author: {author}, Release Date: {release_date}, Pages: {pages}, Borrowed by: {username}")
            print("*************************************************************************************")

    def sort_books(self):
        while True:
            print("*** SORT BOOKS ***")
            print("1) Sort by Title")
            print("2) Sort by Author")
            print("q) Quit")
            choice = input("Enter your choice (1/2/q): ")
            if choice == "1":
                self.sort_books_by("title")
            elif choice == "2":
                self.sort_books_by("author")
            elif choice.lower() == "q":
                break
            else:
                print("Invalid choice. Please enter a valid option.")

    def sort_books_by(self, key):
        self.file.seek(0)
        books = self.file.readlines()
        books.sort(key=lambda x: x.split(',')[0 if key == 'title' else 1])
        self.file.seek(0)
        self.file.truncate()
        for book in books:
            self.file.write(book)
        print("Books sorted successfully.")

    def load_admin_users(self):
        admin_users = {}
        with open("admin.txt", "r") as f:
            for line in f:
                username, password = line.strip().split(",")
                admin_users[username] = password
        return admin_users

    def load_normal_users(self):
        normal_users = {}
        with open("users.txt", "r") as f:
            for line in f:
                username, password = line.strip().split(",")
                normal_users[username] = password
        return normal_users

    def list_books(self):
        self.file.seek(0)
        books = self.file.read().splitlines()
        if not books:
            print("*******There is no book here.*******")
            return
        for i, book in enumerate(books, start=1):
            book_info = book.split(',')
            if len(book_info) == 5:
                name, author, release_date, pages, username = book_info
                print("*************************************************************************************")
                print(
                    f"{i}) Title: {name}, Author: {author}, Release Date: {release_date}, Pages: {pages}, Borrowed by: {username}")
                print("*************************************************************************************")
            else:
                print(f"Error: Malformed book entry: {book}")

    def add_book(self):
        name = input("Enter book title: ")
        author = ""
        release_date = ""
        pages = ""

        while not author.replace(" ", "").isalpha():
            author = input("Enter book author: ")
            if not author.replace(" ", "").isalpha():
                print("Error: Author name cannot contain numbers. Please enter a valid author name.")

        while True:
            release_date = input("Enter release year: ")
            if release_date.isdigit():
                break
            else:
                print("Error: Release year must be an integer. Please enter a valid year.")

        while True:
            try:
                pages = int(input("Enter number of pages: "))
                break
            except ValueError:
                print("Error: Number of pages must be an integer. Please enter a valid number.")

        self.file.write(f"{name},{author},{release_date},{pages},\n")
        print("Book added successfully.")

    def remove_book(self):
        self.list_books()
        book_number = input("Enter the number of the book to remove: ")
        self.file.seek(0)
        books = self.file.readlines()
        self.file.seek(0)
        self.file.truncate()
        book_removed = False
        for i, book in enumerate(books, start=1):
            if i != int(book_number):
                self.file.write(book)
            else:
                book_info = book.split(',')
                if len(book_info) == 5 and book_info[-1].strip() != "":
                    print("Cannot remove borrowed book.")
                else:
                    book_removed = True
        if book_removed:
            print("Book removed successfully.")
        else:
            print(f"There is no book with number {book_number} in the library.")

    def is_book_borrowed(self, title):
        self.transactions_file.seek(0)
        transactions = self.transactions_file.readlines()
        for transaction in transactions:
            book_title, user = transaction.strip().split(',')
            if title.lower() == book_title.lower():
                return True
        return False

    def delete_user(self):
        username = input("Enter username of the user to delete: ")
        if username in self.normal_users:
            del self.normal_users[username]
            print(f"User '{username}' deleted successfully.")
            with open("users.txt", "w") as f:
                for u, p in self.normal_users.items():
                    f.write(f"{u},{p}\n")
        else:
            print(f"User '{username}' not found.")

    def list_users(self):
        print("*** USERS ***")
        for username in self.normal_users:
            print(username)

    def signup(self):
        username = input("Enter username: ")
        password = input("Enter password: ")
        with open("users.txt", "a") as f:
            f.write(f"{username},{password}\n")
        print("Signup successful.")

    def login(self):
        while True:
            self.print_login_menu()
            choice = input("Enter your choice (1/2/q): ")
            if choice == "1":
                username = input("Enter username: ")
                password = input("Enter password: ")
                if username in self.admin_users and self.admin_users[username] == password:
                    self.logged_in_user = username
                    print(f"Login successful. Welcome {username}!")
                    return True, "admin"
                elif username in self.normal_users and self.normal_users[username] == password:
                    self.logged_in_user = username
                    print(f"Login successful. Welcome {username}!")
                    return True, "user"
                else:
                    print("Invalid username or password. Please try again.")
            elif choice == "2":
                self.signup()
                self.admin_users = self.load_admin_users()
                self.normal_users = self.load_normal_users()

            elif choice.lower() == "q":
                print("Exiting the program...")
                exit()
            else:
                print("Invalid choice. Please enter a valid option.")

    def print_login_menu(self):
        print("*** LOGIN MENU ***")
        print("1) Login")
        print("2) Signup")
        print("q) Quit")

    def print_admin_menu(self):
        print("*** ADMIN MENU ***")
        print("1) List Books")
        print("2) Add Book")
        print("3) Remove Book")
        print("4) Delete User")
        print("5) List Users")
        print("6) List Borrowed Books")
        print("7) Search Books")
        print("8) Sort Books")
        print("9) See Average Ratings")
        print("q) Quit")

    def print_user_menu(self):
        print("*** USER MENU ***")
        print("1) List Books")
        print("2) Borrow Book")
        print("3) Return Book")
        print("4) Update Password")
        print("5) List Borrowed Books")
        print("6) Search Books")
        print("7) Sort Books")
        print("8) Rate Book")
        print("9) See Average Ratings")
        print("q) Quit")

    def borrow_book(self):
        self.list_books()
        book_number = input("Enter the number of the book to borrow: ")
        if not book_number.isdigit():
            print("Invalid input. Please enter a valid number.")
            return
        book_number = int(book_number)
        self.file.seek(0)
        books = self.file.readlines()
        self.file.seek(0)
        self.file.truncate()
        book_borrowed = False
        for i, book in enumerate(books, start=1):
            if i == book_number:
                book_info = book.split(',')
                if len(book_info) == 5 and book_info[-1].strip() == "":
                    book_info[-1] = self.logged_in_user
                    book = ','.join(book_info) + '\n'
                    book_borrowed = True
                    self.history_file.write(f"{self.logged_in_user},{book_info[0]},Borrowed\n")
            self.file.write(book)
        if book_borrowed:
            self.transactions_file.write(f"{book_info[0]},{self.logged_in_user}\n")
            print("Book borrowed successfully.")
        else:
            print(f"Book with number {book_number} is not available for borrowing.")

    def list_borrowed_books(self):
        print("*** BORROWED BOOKS ***")
        self.transactions_file.seek(0)
        transactions = self.transactions_file.readlines()
        borrowed_books = [transaction.strip().split(',')[0] for transaction in transactions if
                          transaction.strip().split(',')[1] == self.logged_in_user]
        if borrowed_books:
            for book in borrowed_books:
                print(f"Title: {book}")
        else:
            print("There is no book borrowed by you.")

    def return_book(self):
        self.list_borrowed_books()
        title = input("Enter the title of the book to return: ")
        self.transactions_file.seek(0)
        transactions = self.transactions_file.readlines()
        self.transactions_file.seek(0)
        self.transactions_file.truncate()
        book_returned = False
        for transaction in transactions:
            transaction_info = transaction.split(',')
            if title.lower() in transaction_info[0].lower() and self.logged_in_user in transaction_info[1]:
                book_returned = True
                self.history_file.write(f"{self.logged_in_user},{title},Returned\n")
            else:
                self.transactions_file.write(transaction)
        if book_returned:
            self.file.seek(0)
            books = self.file.readlines()
            self.file.seek(0)
            self.file.truncate()
            for book in books:
                if title.lower() in book.lower():
                    book_info = book.split(',')
                    book_info[-1] = ""
                    book = ','.join(book_info) + '\n'
                self.file.write(book)
            print("Book returned successfully.")
        else:
            print(f"Book '{title.capitalize()}' is not currently borrowed by you.")

    def update_password(self):
        new_password = input("Enter your new password: ")
        self.normal_users[self.logged_in_user] = new_password
        with open("users.txt", "w") as f:
            for u, p in self.normal_users.items():
                f.write(f"{u},{p}\n")
        print("Password updated successfully.")

    def list_borrowed_books(self):
        print("*** BORROWED BOOKS ***")
        self.transactions_file.seek(0)
        transactions = self.transactions_file.readlines()
        for transaction in transactions:
            title, user = transaction.strip().split(',')
            print(f"Title: {title}, Borrowed by: {user}")

    def main(self):
        while True:
            success, user_type = self.login()
            if success:
                if user_type == "admin":
                    while True:
                        self.print_admin_menu()
                        choice = input("Enter your choice (1/2/3/4/5/6/7/8/q): ")
                        if choice == "1":
                            self.list_books()
                        elif choice == "2":
                            self.add_book()
                        elif choice == "3":
                            self.remove_book()
                        elif choice == "4":
                            self.delete_user()
                        elif choice == "5":
                            self.list_users()
                        elif choice == "6":
                            self.list_borrowed_books()
                        elif choice == "7":
                            self.search_books()
                        elif choice == "8":
                            self.sort_books()
                        elif choice == "9":
                            average_ratings = self.get_average_ratings()
                            for title, rating in average_ratings.items():
                                print(f"Title: {title}, Average Rating: {rating}")

                        elif choice.lower() == "q":
                            break
                        else:
                            print("Invalid choice. Please enter a valid option.")
                    print("You have signed out successfully.")
                elif user_type == "user":
                    while True:
                        self.print_user_menu()
                        choice = input("Enter your choice (1/2/3/4/5/q): ")
                        if choice == "1":
                            self.list_books()
                        elif choice == "2":
                            self.borrow_book()
                        elif choice == "3":
                            self.return_book()
                        elif choice == "4":
                            self.update_password()
                        elif choice == "5":
                            self.list_borrowed_books()
                        elif choice == "6":
                            self.search_books()
                        elif choice == "7":
                            self.sort_books()
                        elif choice == "8":
                            self.rate_book()
                        elif choice == "9":
                            average_ratings = self.get_average_ratings()
                            for title, rating in average_ratings.items():
                                print(f"Title: {title}, Average Rating: {rating}")

                        elif choice.lower() == "q":
                            break
                        else:
                            print("Invalid choice. Please enter a valid option.")
                    print("You have signed out successfully.")

if __name__ == "__main__":
    lib = Library()
    try:
        lib.main()
    except KeyboardInterrupt:
        print("\nExiting the program...")
