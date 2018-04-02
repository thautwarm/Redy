try:
    import cytoolz as toolz
except ModuleNotFoundError:
    import toolz

curry = toolz.curry

doc_test_funcs = set()


def doc_test(func):
    if func not in doc_test_funcs:
        doc_test_funcs.add(func)
    return func


def doc_testable(func):
    return func in doc_test_funcs
