"""
cinii books
"""

import logging

logger = logging.getLogger(__name__)

import httpx

from gen_book_info.bookdata import BookData
from gen_book_info.isbn import ISBN
from gen_book_info.provider import Provider


class CiNiiProvider(Provider):
    def fetch(self, isbn: ISBN) -> BookData | None:
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
        return BookData(
            isbn=isbn,
            title=the_result["title"],
            authors=[the_result["dc:creator"]],
            publisher=the_result["dc:publisher"][0],
            urls=[the_result["@id"]],
            year=the_result["dc:date"],
        )
