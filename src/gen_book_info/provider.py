from abc import ABC, abstractmethod

from gen_book_info.bookdata import ISBN, BookData


class Provider(ABC):
    @abstractmethod
    def fetch(self, isbn: ISBN) -> BookData:
        """
        from an isbn, gets the book data
        """
        ...
