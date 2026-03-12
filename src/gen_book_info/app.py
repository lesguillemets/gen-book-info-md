import argparse
import logging
import os
import sys
from dataclasses import dataclass
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


@dataclass
class OutputConfig:
    """
    出力先どこにどうするか
    """

    option: OutputOption
    path: Path | None = None

    @staticmethod
    def from_args(args: argparse.Namespace) -> OutputConfig:
        """
        ArgumentParser から
        """
        output_option = args.output
        match output_option:
            case OutputOption.FILE:
                # 関連するオプション (file なら --path とか) の設定をチェック
                # requires file specification
                out_path = args.path
                if out_path is None:
                    raise ValueError("no output file is specified")
                else:
                    if out_path.is_file():
                        # すでにあるファイルは上書きしない
                        logger.warning(f"refraining from overriding {out_path}")
                        raise ValueError(f"refraining from overriding {out_path}")
                return OutputConfig(option=output_option, path=out_path.resolve())
            case OutputOption.DIR:
                # specified, or reads from environmental variable
                if (out_dir := args.path) is None:
                    # if not specified in the command line arugment, use environmental variable
                    out_dir = os.environ.get("GEN_BOOK_INFO_DIR")
                    if out_dir is None:
                        # not specified, either by command line argument or $GEN_BOOK_INFO_DIR
                        raise ValueError("output dir is unspecified")
                    else:
                        out_dir = Path(out_dir)
                        logger.info(
                            f"directory set by environmental variable: {out_dir}"
                        )
                else:
                    logger.info(f"directory set by  command line argument: {out_dir}")
                return OutputConfig(option=output_option, path=out_dir.resolve())
            case OutputOption.STDOUT:
                return OutputConfig(option=output_option, path=None)

    def handle(self, *, isbn: ISBN, result: str):
        """
        設定に基づいて処理する
        """
        # todo: export もここでしたらよいのかも
        match self.option:
            case OutputOption.FILE:
                assert isinstance(self.path, Path)
                with self.path.open("w") as f:
                    f.write(result)
                logger.info(f"wrote to {self.path}")
            case OutputOption.DIR:
                assert isinstance(self.path, Path)
                if not self.path.exists():
                    logger.warning(f"Creating dir: {self.path}")
                    self.path.mkdir(parents=True)
                out_file = self.path / f"{isbn.isbn}.md"
                if out_file.is_file():
                    # すでにあるときは触らないでおく
                    logger.warning(f"not overriding {out_file}")
                    sys.exit(1)
                with out_file.open("w") as f:
                    f.write(result)
                logger.info(f"wrote to {out_file}")
            case OutputOption.STDOUT:
                print(result)


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

    # 出力先設定の読み込み
    try:
        output_config = OutputConfig.from_args(args)
    except ValueError as e:
        logger.error(e)
        sys.exit(1)
    # ISBN 読み取り
    try:
        isbn = ISBN(args.isbn)
    except ValueError as e:
        logger.error(e)
        sys.exit(1)
    logger.debug(f"Looking up ISBN {isbn} (type {isbn.type})")
    # 書籍のデータ取得
    bd = CiNiiProvider().fetch(isbn)
    if bd is not None:
        # 成功！
        logger.info(f"Found: {bd.title!r} ({bd.year})")
        output_config.handle(isbn=isbn, result=export(bd))
        return bd
    else:
        logger.warning(f"No result found for {isbn}")
        sys.exit(1)


# Copyright (c) 2026 lesguillemets
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
