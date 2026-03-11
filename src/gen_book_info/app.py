import argparse
import logging
import os
import sys
from enum import Enum
from pathlib import Path

from gen_book_info.exporter import export
from gen_book_info.isbn import ISBN
from gen_book_info.providers.cinii import CiNiiProvider

logger = logging.getLogger(__name__)


class OutputOption(Enum):
    """
    出力先の設定
    """

    STDOUT = "stdout"  # 標準出力
    FILE = "file"  # ファイル名を指定
    DIR = "dir"  # あるディレクトリで，ファイル名は ISBN から決める


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

    # log の設定 (--verbose)
    logging.basicConfig(
        level=logging.WARNING,
        format="%(levelname)s [%(name)s] %(message)s",
    )
    if args.verbose:
        logging.getLogger("gen_book_info").setLevel(logging.DEBUG)

    output_option = args.output
    # 関連するオプション (file なら --path とか) の設定をチェック
    if output_option == OutputOption.FILE:
        # requires file specification
        if args.path is None:
            logger.error("no output file is specified")
            sys.exit(1)
        else:
            if args.path.is_file():
                # すでにあるファイルは上書きしない
                logger.warning(f"refraining from overriding {args.path}")
                sys.exit(1)
    elif output_option == OutputOption.DIR:
        # reads from environmental variable
        if (out_dir := args.path) is None:
            # if not specified in the command line arugment, use environmental variable
            out_dir = os.environ.get("GEN_BOOK_INFO_DIR")
            if out_dir is None:
                # not specified, either by command line argument or $GEN_BOOK_INFO_DIR
                logger.error("output dir is unspecified")
                sys.exit(1)
            else:
                out_dir = Path(out_dir)
                logger.info(f"directory set by environmental variable: {out_dir}")

    try:
        isbn = ISBN(args.isbn)
    except ValueError as e:
        logger.error(e)
        sys.exit(1)
    logger.debug(f"Looking up ISBN {isbn} (type {isbn.type})")
    bd = CiNiiProvider().fetch(isbn)
    if bd is not None:
        logger.info(f"Found: {bd.title!r} ({bd.year})")
        export_result = export(bd)
        match output_option:
            case OutputOption.FILE:
                # ファイルに書き込み
                with args.path.open("w") as f:
                    f.write(export_result)
            case OutputOption.DIR:
                # ディレクトリ下に ISBN.md を作成
                assert isinstance(out_dir, Path)
                out_file = out_dir / f"{isbn.isbn}.md"
                if out_file.is_file():
                    # すでにあるときは触らないでおく
                    logger.warning(f"not overriding {out_file}")
                    sys.exit(1)
                with out_file.open("w") as f:
                    f.write(export_result)
            case OutputOption.STDOUT:
                print(export_result)
        return bd
    else:
        logger.warning(f"No result found for {isbn}")
        sys.exit(1)


# Copyright (c) 2026 lesguillemets
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
