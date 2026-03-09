from abc import ABC, abstractmethod

from gen_book_info.bookdata import ISBN, BookData


class Provider(ABC):
    @abstractmethod
    def fetch(self, isbn: ISBN) -> BookData:
        """
        from an isbn, gets the book data
        """
        ...


# Copyright (c) 2026 lesguillemets
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
