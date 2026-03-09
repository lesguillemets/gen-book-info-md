import importlib.resources
from string import Template

import gen_book_info.templates
from gen_book_info.bookdata import BookData


def export(bd: BookData) -> str:
    template = Template(
        importlib.resources.read_text(gen_book_info.templates, "template.md")
    )
    return template.safe_substitute(bd.to_substitute_mapping())


# Copyright (c) 2026 lesguillemets
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
