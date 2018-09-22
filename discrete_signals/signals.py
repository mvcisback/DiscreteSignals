from collections import defaultdict
from typing import DefaultDict, FrozenSet, Mapping, TypeVar, Union

import attr
import funcy as fn
from sortedcontainers import SortedDict


Time, Value = TypeVar('Time'), TypeVar('Value')


def _name_converter(names):
    return names if isinstance(names, frozenset) else frozenset({names})


@attr.s(slots=True, repr=False)
class DiscreteSignal:
    data=attr.ib(
        converter=SortedDict,
        type=Mapping[Time, DefaultDict[str, Value]]
    )
    start=attr.ib(type=Time)
    end=attr.ib(type=Time)

    @property
    def values(self):
        return list(self.data.values())

    @property
    def times(self):
        return list(self.data.keys())

    def __repr__(self):
        return f"start, end: [{self.start}, {self.end})\n" \
            f"data: {[(t, dict(val)) for t, val in self.data.items()]}"

    def evolve(self, **kwargs):
        return attr.evolve(self, **kwargs)
    
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
            start, end = key.start, key.stop
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
            values = self[start + t: end + t].data.values()
            # Note: {} forces application of tuple.
            values = fn.merge_with(tuple, {}, *values)
            return (t, values)
        
        return self.evolve(
            data=fn.walk(apply_window, self.data),
            end=self.end - end
        )


def signal(data, start, end, tag=None):
    data = map(lambda x: (x[0], defaultdict(None, {tag: x[1]})), data)
    return DiscreteSignal(data=data, start=start, end=end)[start:end]