import arcade as arc

TShape = arc.shape_list.TShape


class ShapeList(arc.shape_list.ShapeElementList):
    def extend(self, *items: TShape) -> None:
        for item in items:
            self.append(item)

    def remove_many(self, *items: TShape) -> None:
        for item in items:
            batch = self.batches[item.mode]
            if item not in batch.items:
                batch.update()
        for item in items:
            self.remove(item)
