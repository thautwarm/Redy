ADT
=======================


Preview
-----------------

* Natural Number

.. code :: python

    from Redy.ADT.Core import data
    from Redy.ADT.traits import Ord, Discrete, ConsInd


    @data
    class Nat(Discrete, Ord, ConsInd):
        Zero: ...
        Succ: lambda o: ...

        def __eq__(self, other):
            assert isinstance(other, Nat)
            if self is Nat.Zero:
                return other is Nat.Zero
            if other is Nat.Zero:
                return False
            return other[1] == self[1]

        def __lt__(self, other):
            assert isinstance(other, Nat)
            if self is Nat.Zero:
                return other is not Nat.Zero
            elif other is Nat.Zero:
                return False
            else:
                return self[1] < other[1]


    assert isinstance(Nat.Zero, Nat)  # => True

    _1 = Nat.Succ(Nat.Zero)
    _2 = Nat.Succ(_1)
    _3 = Nat.Succ(_2)

    assert (_3 > _2 > _1)

    assert _3 == _3

    assert _3 != _2


* LinkedList


.. code :: python

    from Redy.ADT.Core import data
    from Redy.ADT import traits

    @data
    class List(traits.ConsInd, traits.Dense, traits.Im):
        Nil : ...
        Cons: lambda head, tail: ...

        def __lshift__(self, value):
            return List.Cons(value, self)

    print(List.Nil)
    print(isinstance(List.Nil, List))
    print(List.Nil << 1 << 2 << 3)

Output:

.. code :: shell


    Nil
    True
    Cons(3, Cons(2, Cons(1, Nil)))


Traits
--------------

You might notice that :code:`traits` here are unfamiliar and kind of strange, however it's significant for designing datatypes with detailed features and descriptions.


- :code:`ConsInd` 

For example, :code:`traits.ConsInd` means you can access any component of instances in the way they're constructed.

.. code :: python


    lst = List.Cons(1, (List.Cons(2, List.Nil)))
    assert lst[0] is List.Cons  # pass
    assert lst[1] is 1  # pass
    assert lst[2] == List.Cons(2, List.Nil)  # pass


- :code:`Im` 

Trait :code:`Im` is short for "Immutable", just as this trait suggested,
the immutable data could not be updated in place,
on the other hand, immutable data is hashable and could be used as the key of hashdict.

.. code :: python


    @data
    class User(traits.Im):
        Student: lambda name, sex, age, sno, class_id, grade: ...
        Teacher: lambda name, sex, sno: ...

    student1 = User.Student("Sam", 1, 18, 0x42, 0x99, 2333)
    teacher1 = User.Teacher("Bili", 1, 0x565656)

    payments = {student1: 20, teacher1: 50}


- :code:`Eq` 

indicates that a instance of the datatype is able to applied equivalence comparisons with other objects.

You should implement an :code:`__eq__(self, other)`  method for yourself.

- :code:`Hash` 

indicates that a instance of the datatype is hashable and you should implement :code:`__hash__(self)`  for yourself.

- :code:`Ord` 

indicates the instance is ordered and obviously an :code:`Ord`  is an :code:`Eq` . You should implement an :code:`__eq__`  method, and either an :code:`__lt__`  or an :code:`__gt__` .

- :code:`Dense` 

a :code:`Dense`  object is also an :code:`Eq` , which implements a default :code:`__eq__`  method. A :code:`Dense`  object equals to some other if and only if the other is also a :code:`Dense` 
, and the components that respectively construct them sequentially equal the other side.

An example of :code:`Dense`  object is an element of any given set in mathematics which could be distinguished from other elements, and once its components
mutate slightly there could be a brand-new :code:`Dense`  object.


- :code:`Discrete` 

a :code:`Discrete`  object is both an :code:`Eq`  and an :code:`Im` . A :code:`Discrete`  object equals to some other if and only if they are just the same object.

If you construct two :code:`Discrete`  objects with the same components, actually they're the same one.

An example of :code:`Discrete`  object is a natural number.





