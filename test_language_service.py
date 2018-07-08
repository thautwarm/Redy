from Redy.Opt import feature, constexpr, const, macro, define


@feature(macro)
def g():
    with macro.setting:
        X = define(S(a, b), a)

    with macro[X]:
        print(S(1, 2))


print(g())
