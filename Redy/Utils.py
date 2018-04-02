try:
    import cytoolz as toolz
except ModuleNotFoundError:
    import warnings
    import toolz

curry = toolz.curry
