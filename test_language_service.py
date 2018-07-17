from Redy.Opt import *
from dis import dis


@feature(goto)
def loop1():
    task1: label
    task2: label
    end: label

    with task1:
        print('task1')
        x = input('where do you want to goto?[1, 2, end]')
        if x == 'end':
            print('jump to end')

            end.jump()
        elif x == '1':
            print('jump to task1')

            task1.jump()
        elif x == '2':
            print('jump to task2')

            task2.jump()

        raise ValueError

    task2.mark()
    print('task2| then turn to task1.')
    task1.jump()

    end.mark()
    print('good bye')


macro = Macro()


@feature(macro)
def macro_example(x):
    @macro.stmt
    def just_return(v):
        return v

    just_return(1)


@macro.stmt
def print_some_and_return_1(s):
    print(s)
    return 1


@feature(macro)
def macro_example2():
    print_some_and_return_1("abcdefg")


dis(macro_example)
print(macro_example(1))
macro_example2()

# dis(loop1)
# loop1()


macro.stmt('def m(): print("string macro")')


#
@feature(macro)
def test_string_macro():
    m()


test_string_macro()
