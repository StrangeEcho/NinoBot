from datetime import timedelta
from typing import Iterable, Iterator, Sequence, TypeVar

import humanize

T = TypeVar("T")


def humanize_timedelta(td: timedelta, *, precise: bool = False) -> str:
    """Humanize a timedelta into human readable text"""
    if precise:
        return humanize.precisedelta(td, minimum_unit="seconds")
    return humanize.naturaldelta(td)


def chunk_iter(iterable: Iterable, chunk_size: int) -> Iterator[Sequence[T]]:
    """Chunk a list into smaller list by specified chunk size"""
    for i in range(0, len(iterable), chunk_size):
        yield iterable[i : i + chunk_size]
