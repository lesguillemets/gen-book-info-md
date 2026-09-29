"""
Google Books (API v1)
https://developers.google.com/books/docs/v1/using
"""

import logging
import os
from typing import TypedDict

import httpx

from gen_book_info.bookdata import BookData
from gen_book_info.isbn import ISBN
from gen_book_info.provider import Provider

logger = logging.getLogger(__name__)

API_URL = "https://www.googleapis.com/books/v1/volumes"
# API キーは任意．キーなしだと共有 IP などで quota に引っかかりやすい
API_KEY_ENV = "GEN_BOOK_INFO_GOOGLE_API_KEY"


class IndustryIdentifier(TypedDict):
    type: str  # "ISBN_10", "ISBN_13", "ISSN", "OTHER"
    identifier: str


class VolumeInfo(TypedDict, total=False):
    title: str
    subtitle: str
    authors: list[str]
    publisher: str
    publishedDate: str  # "2008", "2008-05", "2008-05-12" など
    industryIdentifiers: list[IndustryIdentifier]
    infoLink: str
    canonicalVolumeLink: str


class Volume(TypedDict, total=False):
    id: str
    selfLink: str
    volumeInfo: VolumeInfo


class VolumesResponse(TypedDict, total=False):
    totalItems: int
    items: list[Volume]


class GoogleBooksProvider(Provider):
    api_key: str | None

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key if api_key is not None else os.environ.get(API_KEY_ENV)

    def fetch(self, isbn: ISBN) -> BookData | None:
        logger.debug(f"Fetching {isbn} from Google Books")
        params = {"q": f"isbn:{isbn.isbn}"}
        if self.api_key:
            params["key"] = self.api_key
        r = httpx.get(API_URL, params=params)
        logger.info(f"Got response: {r.status_code}")
        if r.is_error:
            try:
                message = r.json()["error"]["message"]
            except ValueError, KeyError, TypeError:
                message = r.text
            logger.error(f"Google Books API error ({r.status_code}): {message}")
            if r.status_code == 429 and not self.api_key:
                logger.error(f"consider setting ${API_KEY_ENV}")
            return None
        data: VolumesResponse = r.json()
        return parse_response(isbn, data)


def parse_response(isbn: ISBN, data: VolumesResponse) -> BookData | None:
    """
    volumes 検索の JSON から BookData を作る
    """
    items = data.get("items", [])
    if not items:
        logger.warning("No info")
        return None
    if len(items) > 1:
        logger.warning(f"More than 1 ({len(items)}) results for {isbn}")

    # q=isbn: は時々関係ない本も返すので，ISBN が一致するものを優先する
    matching = [v for v in items if _has_isbn(v, isbn)]
    if matching:
        volume = matching[0]
    else:
        logger.warning(f"No result lists {isbn} explicitly; using the first one")
        volume = items[0]

    info = volume.get("volumeInfo", {})
    title = info.get("title", "")
    if subtitle := info.get("subtitle"):
        # CiNii の表記に合わせる
        title = f"{title} : {subtitle}"
    published = info.get("publishedDate", "")
    url = info.get("canonicalVolumeLink") or info.get("infoLink")
    logger.debug(
        f"Parsed result: title={title!r},"
        f" authors={info.get('authors')!r},"
        f" publisher={info.get('publisher')!r}"
    )
    return BookData(
        isbn=isbn,
        title=title,
        authors=info.get("authors", []),
        publisher=info.get("publisher", ""),
        urls=[url] if url else [],
        year=published.split("-")[0] or None,
    )


def _has_isbn(volume: Volume, isbn: ISBN) -> bool:
    identifiers = volume.get("volumeInfo", {}).get("industryIdentifiers", [])
    return any(i["identifier"] == isbn.isbn for i in identifiers)


# Copyright (c) 2026 lesguillemets
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
