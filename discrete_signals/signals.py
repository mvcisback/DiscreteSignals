from collections import defaultdict
from typing import DefaultDict, Mapping, TypeVar

import attr
import funcy as fn
from sortedcontainers import SortedDict


Time, Value = TypeVar('Time'), TypeVar('Value')


def _name_converter(names):
    return names if isinstance(names, frozenset) else frozenset({names})


@attr.s(slots=True, repr=False)
class DiscreteSignal:
    data = attr.ib(
        converter=SortedDict,
        type=Mapping[Time, DefaultDict[str, Value]]
    )
    start = attr.ib(type=Time)
    end = attr.ib(type=Time)

    def values(self):
        return self.data.values()

    def times(self):
        return self.data.keys()

    def items(self):
        return self.data.items()

    @property
    def tags(self):
        return set(fn.cat(self.values()))

    def evolve(self, **kwargs):
        return attr.evolve(self, **kwargs)

    def __repr__(self):
        return f"start, end: [{self.start}, {self.end})\n" \
            f"data: {[(t, dict(val)) for t, val in self.items()]}"

    def __rshift__(self, delta):
        return self.evolve(
            data=fn.walk_keys(lambda t: t + delta, self.data),
            start=self.start + delta,
            end=self.end + delta,
        )

    def __lshift__(self, delta):
        return self >> -delta

    def __matmul__(self, other):
        return self.evolve(
            data=fn.merge(
                self.data,
                fn.walk_keys(lambda t: t + self.end, other.data)
            ),
            end=self.end + (other.end - other.start)
        )

    def __or__(self, other):
        return self.evolve(
            data=fn.merge_with(lambda x: fn.merge(*x), self.data, other.data),
            start=min(self.start, other.start),
            end=max(self.end, other.end),
        )

    def __getitem__(self, key):
        if isinstance(key, slice):
            assert key.step is None
            start = self.start if key.start is None else key.start
            end = self.end if key.stop is None else key.stop

            return self.evolve(
                data=fn.select_keys(lambda t: start <= t < end, self.data),
                start=start, end=end,
            )
        return self.data[key]

    def rolling(self, start, end):
        if start != 0:
            return self.rolling(0, end-start) << start

        def apply_window(time_val):
            t, _ = time_val
            values = self[start + t: end + t].values()
            # Note: {} forces application of tuple.
            values = fn.merge_with(tuple, {}, *values)
            return (t, values)

        return self.evolve(
            data=fn.walk(apply_window, self.data),
            end=self.end - end
        )

    def map(self, func, tag=None):
        data = fn.walk_values(func, list(self.items()))
        return signal(data, self.start, self.end, tag)

    def retag(self, mapping):
        def _retag(val):
            return fn.walk_keys(lambda k: mapping.get(k, k), val)

        return self.evolve(data=fn.walk_values(_retag, self.data))


def signal(data, start, end, tag=None):
    data = map(lambda x: (x[0], defaultdict(None, {tag: x[1]})), data)
    return DiscreteSignal(data=data, start=start, end=end)[start:end]
