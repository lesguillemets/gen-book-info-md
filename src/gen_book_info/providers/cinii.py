"""
cinii books
"""

import logging

import httpx

from gen_book_info.bookdata import BookData
from gen_book_info.isbn import ISBN
from gen_book_info.provider import Provider

logger = logging.getLogger(__name__)


class CiNiiProvider(Provider):
    def fetch(self, isbn: ISBN) -> BookData | None:
        logger.debug(f"Fetching {isbn} from CiNii")
        r = httpx.get(
            "https://ci.nii.ac.jp/books/opensearch/search",
            params={"format": "json", "isbn": isbn.isbn},
        )
        logger.info(f"Got response: {r.status_code}")
        data = r.json()
        resul = data["@graph"][0]
        total_results = int(resul["opensearch:totalResults"])
        if total_results == 0:
            logger.warning("No info")
            return None
        elif total_results > 1:
            logger.warning(
                f"More than 1 ({total_results}) results for {isbn}: \n{data}"
            )

        the_result = resul["items"][0]
        logger.debug(
            f"Parsed result: title={the_result['title']!r},"
            f" creator={the_result['dc:creator']!r},"
            f" publisher={the_result['dc:publisher'][0]!r}"
        )
        return BookData(
            isbn=isbn,
            title=the_result["title"],
            authors=[the_result["dc:creator"]],
            publisher=the_result["dc:publisher"][0],
            urls=[the_result["@id"]],
            year=the_result["dc:date"],
        )


# Copyright (c) 2026 lesguillemets
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
