import argparse
import logging
import sys

logger = logging.getLogger(__name__)

from gen_book_info.exporter import export
from gen_book_info.isbn import ISBN
from gen_book_info.providers.cinii import CiNiiProvider


def main():
    parser = argparse.ArgumentParser(
        description="fetch book info from ISBN and fills the template"
    )

    parser.add_argument(
        "isbn",
        help="ISBN of the book. You may include hyphen, or strip them.",
        type=str,
    )
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.WARNING,
        format="%(levelname)s [%(name)s] %(message)s",
    )
    if args.verbose:
        logging.getLogger("gen_book_info").setLevel(logging.DEBUG)

    try:
        isbn = ISBN(args.isbn)
    except ValueError as e:
        logger.error(e)
        sys.exit(str(e))
    bd = CiNiiProvider().fetch(isbn)
    if bd is not None:
        print(export(bd))
        return bd
    else:
        logger.debug(f"Not a result for {isbn}")


# Copyright (c) 2026 lesguillemets
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
