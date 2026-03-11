from abc import ABC, abstractmethod

from gen_book_info.bookdata import ISBN, BookData


class Provider(ABC):
    @abstractmethod
    def fetch(self, isbn: ISBN) -> BookData | None:
        """
        from an isbn, gets the book data.
        If the provider doesn't find the corresponding data,
        returns a None.
        """
        ...

    def fetch_from_string(self, isbn_str: str) -> BookData | None:
        """
        ISBN じゃなくて文字列として受け取ってそのパーズからやる
        """
        isbn = ISBN(isbn_str)
        return self.fetch(isbn)


# Copyright (c) 2026 lesguillemets
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
