import argparse
import logging
import sys
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)

from gen_book_info.exporter import export
from gen_book_info.isbn import ISBN
from gen_book_info.providers.cinii import CiNiiProvider


class OutputOption(Enum):
    STDOUT = "stdout"
    FILE = "file"
    DIR = "dir"


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
    parser.add_argument(
        "--output",
        "-o",
        type=OutputOption,
        choices=OutputOption,
        default=OutputOption.STDOUT,
        metavar=f"{{{','.join(oo.value for oo in OutputOption)}}}",
        help=(
            "output to:\n"
            "'stdout': print to stdout (default)\n"
            "'file': writes to file (requires --path)\n"
            "'dir': writes to a file named with isbn under dir"
            " (--path or as specified by $GEN_BOOK_INFO_DIR)"
        ),
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=None,
        help="write to this file (with --output file) or outdir (with --output dir)",
    )
    args = parser.parse_args()
    print(args.output)

    logging.basicConfig(
        level=logging.WARNING,
        format="%(levelname)s [%(name)s] %(message)s",
    )
    if args.verbose:
        logging.getLogger("gen_book_info").setLevel(logging.DEBUG)

    output_option = args.output
    if output_option == OutputOption.FILE:
        # requires file specification
        if args.path is None:
            raise RuntimeError("no output file is specified")
        else:
            if args.path.isfile():
                logger.warning(f"refraining from overriding {args.path}")
                sys.exit(1)
    elif output_option == OutputOption.DIR:
        if args.path is None:
            logger.info("defaulting")
            # pass

    try:
        isbn = ISBN(args.isbn)
    except ValueError as e:
        logger.error(e)
        sys.exit(str(e))
    logger.debug(f"Looking up ISBN {isbn} (type {isbn.type})")
    bd = CiNiiProvider().fetch(isbn)
    if bd is not None:
        logger.info(f"Found: {bd.title!r} ({bd.year})")
        export_result = export(bd)
        return bd
    else:
        logger.warning(f"No result found for {isbn}")
        sys.exit(1)


# Copyright (c) 2026 lesguillemets
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
