import json
from collections import Counter

class Book:
    def __init__(self, book_id, title, author, year, genre, pages):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.year = year
        self.genre = genre
        self.pages = pages
        self.status = "available"  

    def to_dict(self):
        return self.__dict__

    def __repr__(self):
        return f"Book(ID: {self.book_id}, Title: {self.title}, Author: {self.author})"

class Reader:
    def __init__(self, reader_id, name, surname):
        self.reader_id = reader_id
        self.name = name
        self.surname = surname
        self.current_books = []
        self.history = []
        self.penalty = 0

    def __str__(self):
        return f"{self.name} {self.surname}"

    def to_dict(self):
        return self.__dict__

class Library:
    def __init__(self):
        self.books = []
        self.readers = []
        self.penalty_limit = 10
    
    def register_reader(self, reader):
        self.readers.append(reader)
        print(f"Reader '{reader.name}' registered successfully.")

    def add_book(self, book):
        self.books.append(book)
        print(f"Book '{book.title}' added to the library.")

    def issue_book(self, reader_id, book_id):
        reader = next((r for r in self.readers if r.reader_id == reader_id), None)
        book = next((b for b in self.books if b.book_id == book_id), None)

        if not reader or not book:
            print("Error: Reader or Book not found.")
            return

        if len(reader.current_books) >= 3:
            print(f"Limit reached: {reader.name} already has 3 books.")
            return

        if reader.penalty >= self.penalty_limit:
            print(f"Access denied: {reader.name} has a penalty of {reader.penalty}.")
            return

        if book.status != "available":
            print(f"Error: '{book.title}' is currently not available.")
            return

        book.status = "issued"
        reader.current_books.append(book.book_id)
        print(f"Success: '{book.title}' issued to {reader.name}.")

    def return_book(self, reader_id, book_id, late_days=0):
        reader = next((r for r in self.readers if r.reader_id == reader_id), None)
        book = next((b for b in self.books if b.book_id == book_id), None)

        if reader and book and book.book_id in reader.current_books:
            book.status = "available"
            reader.current_books.remove(book.book_id)
            reader.history.append(book.book_id)
            
            if late_days > 0:
                fine = late_days * 2
                reader.penalty += fine
                print(f"Book returned late. Penalty added: ${fine}")
            else:
                print(f"Book '{book.title}' returned on time.")
        else:
            print("Error: Invalid return operation.")

    def search_books(self, query):
        query = query.lower()
        results = [b for b in self.books if query in b.author.lower() or query in b.title.lower()]
        
        if not results:
            print("No books found matching your query.")
        else:
            print(f"Search Results: {results}")
        return results

    def show_available_books(self):
        available = [b for b in self.books if b.status == "available"]
        print("\n--- Available Books ---")
        for b in available:
            print(b)

    def show_debtors(self):
        debtors = [r.name for r in self.readers if r.penalty > 0 or len(r.current_books) > 0]
        print(f"Debtors list: {debtors}")
    
    def save_to_json(self, filename):
        data = {
            "books": [b.to_dict() for b in self.books],
            "readers": [r.to_dict() for r in self.readers]
        }
        with open(filename, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"Data successfully saved to {filename}")

    def load_from_json(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.books = [Book(**b) for b in data['books']]
                # Reconstructing Readers
                self.readers = []
                for r_data in data['readers']:
                    r = Reader(r_data['reader_id'], r_data['name'], r_data['surname'])
                    r.current_books = r_data['current_books']
                    r.history = r_data['history']
                    r.penalty = r_data['penalty']
                    self.readers.append(r)
            print("Data successfully loaded from JSON.")
        except FileNotFoundError:
            print("JSON file not found.")

    def get_most_active_reader(self):
        if not self.readers: return "No readers registered."
        active_reader = max(self.readers, key=lambda r: len(r.history))
        return f"Most Active Reader: {active_reader.name} ({len(active_reader.history)} books read)"

    def get_most_popular_author(self):
        all_history = []
        for r in self.readers:
            all_history.extend(r.history)
        
        if not all_history: return "No reading history available."

        author_list = []
        for b_id in all_history:
            book = next((b for b in self.books if b.book_id == b_id), None)
            if book: author_list.append(book.author)
            
        most_common_author = Counter(author_list).most_common(1)
        return f"Most Popular Author: {most_common_author[0][0]}"

    def get_top_5_books(self):
        all_history = []
        for r in self.readers:
            all_history.extend(r.history)
        
        top_counts = Counter(all_history).most_common(5)
        print("\n--- Top 5 Most Read Books ---")
        for book_id, count in top_counts:
            book = next((b for b in self.books if b.book_id == book_id), None)
            if book:
                print(f"'{book.title}' — Read {count} times")

# --- Example Usage ---
if __name__ == "__main__":
    my_l = Library()
    my_l.add_book(Book(1, "1984", "George Orwell", 1949, "Dystopian", 328))
    my_l.add_book(Book(2, "The Great Gatsby", "F. Scott Fitzgerald", 1925, "Classic", 180))
    my_l.add_book(Book(3, "The Murder at the Vicarage", "Agatha Christie", 1930, "Detective", 304))
    
    my_l.register_reader(Reader(1, name, surname))
    
    my_l.issue_book(1, 1)
    my_l.return_book(1, 1, 0)
    
    print(my_l.get_most_active_reader())
    my_l.get_top_5_books()
