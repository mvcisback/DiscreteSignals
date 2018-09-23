import funcy as fn

from discrete_signals import signal


DATA1 = [(0, 1), (1, 1.1), (2, 3)]


def test_make_signal():
    sig1 = signal(DATA1, start=0, end=4, tag='x')
    sig2 = signal(DATA1, start=1, end=2, tag='x')
    assert sig1 | sig2 == sig1

    assert set(fn.pluck(0, DATA1)) == set(sig1.times())
    assert set(fn.pluck(0, DATA1)) > set(sig2.times())
    assert len(sig2.times()) == 1
    assert set(fn.pluck(1, DATA1)) == {v['x'] for v in sig1.values()}


def test_repr():
    out = repr(signal(DATA1, start=0, end=4, tag='x'))
    assert out == "start, end: [0, 4)\n" \
        "data: [(0, {'x': 1}), (1, {'x': 1.1}), (2, {'x': 3})]"


def test_slice():
    sig1 = signal(DATA1, start=0, end=4, tag='x')
    sig2 = sig1[-float('inf'):float('inf')][0:4]
    assert sig1 == sig2

    assert sig1[1:2] == signal(DATA1, start=1, end=2, tag='x')
    assert len(sig1[1:2].values()) == 1


def test_time_shifts():
    sig1 = signal(DATA1, start=0, end=4, tag='x')
    assert (sig1 << 2) == (sig1 >> -2)
    assert (sig1 << 2) >> 2 == sig1


def test_append():
    sig1 = signal(DATA1, start=0, end=4, tag='x')
    sig2 = sig1 @ sig1
    assert len(sig2.values()) == 2*len(sig1.values())
    assert sig1.start == sig2.start
    assert sig2.end == 2*sig1.end


def test_par_compose():
    sig1 = signal(DATA1, start=0, end=4, tag='x')
    assert sig1 | sig1 == sig1

    sig2 = sig1 | sig1 >> 0.5
    assert len(sig2.values()) == 2*len(sig1.values())

    sig3 = sig1 | sig1 >> 1
    assert len(sig3.values()) == len(sig1.values())+1

    sig4 = sig1.map(lambda v: -v['x'], tag='y')
    sig5 = (sig1 | sig4).map(lambda v: sum(v.values()), tag='z')
    assert len(sig5.times()) == len(sig1.times())
    assert all(v['z'] == 0 for v in sig5.values())


def test_retag():
    sig1 = signal(DATA1, start=0, end=4, tag='x')
    assert sig1 == sig1.retag({'w': 'n'})

    sig2 = sig1.retag({'x': 'y'})
    assert sig2.tags == {'y'}

    assert sig2.retag({'y': 'x'}) == sig1


def test_rolling():
    sig1 = signal(DATA1, start=0, end=4, tag='x')
    sig2 = sig1.rolling(0, 3)
    assert {v['x'] for v in sig1.values()} == set(sig2[0]['x'])

    sig3 = sig1.rolling(0, 2)
    assert {v['x'] for v in sig1[:2].values()} == set(sig3[0]['x'])

    sig4 = sig1.rolling(0, 1)
    assert {v['x'] for v in sig1[:1].values()} == set(sig4[0]['x'])

    sig5 = sig1.rolling(-1.1, 1.1)
    assert {v['x'] for v in sig1.values()} == set(sig5[1.1]['x'])
    assert {v['x'] for v in sig1[2:].values()} == set(sig5[3.1]['x'])


def test_interp():
    sig1 = signal(DATA1, start=0, end=4, tag='x')
    for i in range(3):
        assert sig1[0] == sig1.interp(i/3)


def test_filter():
    sig1 = signal(DATA1, start=0, end=4, tag='x')
    sig2 = sig1.filter(lambda v: v['x'] > 2)
    assert len(sig2.items()) == 1
    assert sig2[2]['x'] == 3


def test_project():
    sig1 = signal(DATA1, start=0, end=4, tag='x')
    sig2 = signal(DATA1, start=0, end=4, tag='y')
    assert (sig1 | sig2).project('x') == sig1


def test_transform():
    sig1 = signal(DATA1, start=0, end=4, tag='x')
    assert sig1.transform(lambda v: v) == sig1
    assert sig1.transform(lambda v: {'y': v['x']}) \
        == sig1.retag({'x': 'y'})
