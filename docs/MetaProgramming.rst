Meta Programming
============================




Feature Service System
----------------------------------




Examples
-----------------------

* Macro System

.. code :: python

    from Redy.Opt import Macro, feature

    macro = Macro()

    @macro.expr
    def plus(x):
        return x + y

    @feature(macro)
    def do():
        y = 1
        return plus(1)

    assert do() == 2

    @feature(macro)
    def do(inp):

        @macro.stmt  # define macro in some function is okay
        def target(threshold, title):
            if inp > threshold:
                return title

        target(100, "so big")
        target(50,  "kind of big")
        target(20,  "not that big")
        target(10,  "small")
        target(0,   "too young")
        return "unexpected"

    assert do(110) == 'so big'
    assert do(19) == 'small'
    assert do(-1) == "unexpected"


Tips:

1. You can create multiple :code:`Macro` object to implement **macro on macro**.
2. The implementation of Python Macro is trivial under Redy's Feature Service System, you can
   play with it to try something really crazy.



* Constant link, code:`constexpr`

.. code :: python



    from Redy.Opt import feature, const, constexpr

    def make_func(x):

        staging = (const, constexpr)
        @feature(staging)
        def ret(y):

            # object print will be loaded as a constant which is very very fast
            print: const = print

            # for constexpr could be calculated before really invoking function :code:`ret`,
            # we could optimize the code here to remove redundant branches.
            if constexpr[x > 10]:
                print(x + y)
            else:
                print(return x - y)

        return ret


* The most effective, elegant and robust :code:`goto` in Python


.. code :: python



    from Redy.Opt import feature, goto, label

    @feature(goto)
    def f():
        l1: label
        l2: label
        l3: label
        end: label

        with l1:
            # using syntax like context manager is for clarifying the logistics.
            # if you don't like creating a `with-block, you could use `label.mark()` instead.
            print(1)
            l3.jump()

        with l2:
            print(2)
            end.jump()

        with l3:
            l2.jump()

        with end:
            print("done")



This :code:`goto` is quite fast and safe, but you should only perform it somewhere actually matches the use case of :code:`goto` .


