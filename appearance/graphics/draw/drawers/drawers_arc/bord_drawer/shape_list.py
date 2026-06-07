import arcade as arc

TShape = arc.shape_list.TShape


class _Batch(arc.shape_list._Batch):
    def extend(self, *items: TShape) -> None:
        if not items:
            return

        self.new_items.extend(items)
        self.FLAGS |= self.ADD

    def remove_many(self, *items: TShape) -> None:
        if not items:
            return

        for item in items:
            self.items.remove(item)
        self.FLAGS |= self.REMOVE


class ShapeList(arc.shape_list.ShapeElementList):
    def append(self, item: TShape) -> None:
        self.shape_list.append(item)
        batch = self.batches.get(item.mode, None)
        if batch is None:
            batch = _Batch(
                self.ctx,
                self.program,
                item.mode,
            )
            self.batches[item.mode] = batch

        batch.append(item)
        self.dirties.add(batch)

    def extend(self, *items: TShape) -> None:
        if not items:
            return

        self.shape_list.extend(items)
        mode = items[0].mode
        batch = self.batches.get(mode, None)
        if batch is None:
            batch = _Batch(
                self.ctx,
                self.program,
                mode,
            )
            self.batches[mode] = batch

        batch.extend(*items)
        self.dirties.add(batch)

    def remove_many(self, *items: TShape) -> None:
        if not items:
            return

        for item in items:
            self.shape_list.remove(item)
        batch = self.batches[items[0].mode]
        batch.remove_many(*items)
        self.dirties.add(batch)
