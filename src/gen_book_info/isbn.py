# SPDX-License-Identifier: MPL-2.0
import itertools as it


class ISBN:
    isbn: str
    type: str

    def __init__(self, number: str):

        if isinstance(number, int):
            number = str(number)
        # - を飛ばして
        number = number.replace("-", "")

        if len(number) == 13:
            if not check_digit_13(number):
                raise ValueError(f"Check Digit mismatch: {number}")
            else:
                self.isbn = number
                self.type = "13"
        elif len(number) == 10:
            if not check_digit_10(number):
                raise ValueError(f"Check Digit mismatch: {number}")
            else:
                self.isbn = number
                self.type = "10"
        else:
            raise ValueError(f"wrong length: {number}")

    def __str__(self):
        return self.isbn


def check_digit_13(number: str) -> bool:
    """
    checkdigit-13 とみなしたときの checksum

    """
    # remove hyphens
    number = number.replace("-", "")
    if len(number) != 13:
        raise ValueError(f"wrong length {len(number)} of string: {number}")
    if any(not c.isdigit() for c in number):
        # everything left should be number
        raise ValueError(f"unsupported format: {number}")
    checksum = sum(int(c) * p for (c, p) in zip(number, it.cycle([1, 3])))
    return (checksum % 10) == 0


def check_digit_10(number: str) -> bool:

    # remove hyphens and 'x' shall be 'X'
    number = number.replace("-", "").upper()
    if len(number) != 10:
        raise ValueError(f"wrong length {len(number)} of string: {number}")

    # last character to be parsed
    if (checked_sum := number[-1]) == "X":
        checked_sum = 10
    else:
        checked_sum = int(checked_sum)
    # others to be calculated
    numbers_to_calc = number[:-1]
    if any(not c.isdigit() for c in numbers_to_calc):
        # everything left should be number
        raise ValueError(f"unsupported format: {number}")

    checksum = sum(int(c) * p for (c, p) in zip(numbers_to_calc, range(10, 1, -1)))
    return (checksum + checked_sum) % 11 == 0
