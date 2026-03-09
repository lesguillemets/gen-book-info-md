"""
retuned data
"""

# Copyright (c) 2026 lesguillemets
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from dataclasses import dataclass

from gen_book_info.isbn import ISBN


@dataclass
class BookData:
    """
    本のデータ
    """

    isbn: ISBN
    title: str = ""
    title_reading: str = ""
    authors: list[str] = []
    publisher: str = ""
    year: int | None = None
