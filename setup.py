from setuptools import find_packages, setup

setup(
    name='discrete-signals',
    version='0.0.1',
    description='TODO',
    url='http://github.com/mvcisback/DiscreteSignals',
    author='Marcell Vazquez-Chanlatte',
    author_email='marcell.vc@eecs.berkeley.edu',
    license='MIT',
    install_requires=[
        'attrs',
        'funcy',
        'sortedcontainers',
    ],
    packages=find_packages(),
)
