[![Build Status](https://travis-ci.org/mvcisback/DiscreteSignals.svg?branch=master)](https://travis-ci.org/mvcisback/DiscreteSignals)
[![codecov](https://codecov.io/gh/mvcisback/discrete-signals/branch/master/graph/badge.svg)](https://codecov.io/gh/mvcisback/discrete-signals)


[![PyPI version](https://badge.fury.io/py/discrete-signals.svg)](https://badge.fury.io/py/discrete-signals)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# Proposed API

```
import discrete_signals as ds

x = ds.DiscreteSignal([(0, 1), (1, 2), (2, 3)], tag='x')
y = ds.DiscreteSignal([(0.5, 'a'), (1, 'b'), (2, 'c')], tag='y')


```
