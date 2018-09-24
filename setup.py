from setuptools import find_packages, setup

DESC = 'A domain specific language for modeling and manipulating discrete time signals.'  # noqa

setup(
    name='discrete-signals',
    version='0.7.3',
    description=DESC,
    url='http://github.com/mvcisback/DiscreteSignals',
    author='Marcell Vazquez-Chanlatte',
    author_email='marcell.vc@eecs.berkeley.edu',
    license='MIT',
    install_requires=[
        'attrs>=18.1.0',
        'funcy',
        'sortedcontainers',
    ],
    packages=find_packages(),
)
