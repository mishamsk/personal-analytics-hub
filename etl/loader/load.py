from __future__ import annotations

from collections import defaultdict

import typing as t

DEFAULT_PRIORITY = 0


class LoaderRegistry:
    def __init__(self) -> None:
        self.loaders: t.Dict[int, t.Dict[str, t.Callable[[], None]]] = defaultdict(dict)

    def get_loader_names(self) -> t.Set[str]:
        out: t.Set[str] = set()
        for prio in self.loaders.values():
            out.update(prio.keys())
        return out

    def load_one(self, name: str) -> None:
        if name not in self.get_loader_names():
            raise ValueError(f"Unknown loader: {name}")

        for prio in self.loaders.values():
            if name in prio:
                prio[name]()
                return

    def load_all(self) -> None:
        for prio, loaders in sorted(self.loaders.items(), key=lambda x: x[0]):
            for loader in loaders.values():
                loader()

    def register_loader(
        self,
        name: str,
        loader: t.Callable[[], None],
        prio: int = DEFAULT_PRIORITY,
    ) -> None:
        self.loaders[prio][name] = loader


loader_registry = LoaderRegistry()
