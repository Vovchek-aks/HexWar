from typing import Iterator, Sequence

from attrs import frozen

from core.protocols import Cell
from mathematics.path_searcers.path_searcher import PathSearcher, Path


@frozen
class SequencePathSearcher(PathSearcher):
    _searchers: Sequence[PathSearcher]

    def search_from(self, start_cell: Cell) -> Path:
        for path in self.search_process_from(start_cell):
            if path is not None:
                return path

    def search_process_from(self, start_cell: Cell) -> Iterator[Path | None]:
        path = Path()
        for searcher in self._searchers:
            for path in searcher.search_process_from(start_cell):
                yield
                if path is not None:
                    break

            if path:
                yield path
                return

        yield []
