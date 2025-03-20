# pyright: basic


from typing import Any, Callable

def overload(f: Callable[..., Any], overloads: dict[str, Callable[..., Any]] = dict()):

    tp_names = [tp.__name__ for tp in list(f.__annotations__.values())[:-1]]
    overloads['_'.join([f.__name__, *tp_names])] = f

    def indirect_f(*args, **kwargs):

        arg_tp_names = [type(arg).__name__ for arg in [*args, *kwargs.values()]]
        if specific_f := overloads.get('_'.join([f.__name__, *arg_tp_names])):
            return specific_f(*args, **kwargs)

        raise TypeError(f'No overload found for {f.__name__}({', '.join(arg_tp_names)})')

    indirect_f.__name__ = f.__name__

    return indirect_f

@overload
def a(a: int, b: float) -> str:
    return 'a(int float string)'

@overload
def a(a: float, b: int) -> str:
    return 'a(float int string)'

@overload
def b(a: float, b: float) -> str:
    return 'b(float float string)'


# Tests
assert a(4, 8.0) == 'a(int float string)'
assert a(4.0, 8) == 'a(float int string)'

try:
    a(4.0, 8.0)
except TypeError:
    pass
else:
    raise AssertionError('Invalid implementation found for a(float float)')

assert b(4.0, 8.0) == 'b(float float string)'

print('All tests passed')
