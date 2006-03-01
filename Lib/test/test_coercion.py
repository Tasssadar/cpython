import copy
import sys
import warnings

# Fake a number that implements numeric methods through __coerce__
class CoerceNumber:
    def __init__(self, arg):
        self.arg = arg

    def __repr__(self):
        return '<CoerceNumber %s>' % repr(self.arg)

    def __coerce__(self, other):
        if isinstance(other, CoerceNumber):
            return self.arg, other.arg
        else:
            return (self.arg, other)


# Fake a number that implements numeric ops through methods.
class MethodNumber:

    def __init__(self,arg):
        self.arg = arg

    def __repr__(self):
        return '<MethodNumber %s>' % repr(self.arg)

    def __add__(self,other):
        return self.arg + other

    def __radd__(self,other):
        return other + self.arg

    def __sub__(self,other):
        return self.arg - other

    def __rsub__(self,other):
        return other - self.arg

    def __mul__(self,other):
        return self.arg * other

    def __rmul__(self,other):
        return other * self.arg

    def __div__(self,other):
        return self.arg / other

    def __rdiv__(self,other):
        return other / self.arg

    def __pow__(self,other):
        return self.arg ** other

    def __rpow__(self,other):
        return other ** self.arg

    def __mod__(self,other):
        return self.arg % other

    def __rmod__(self,other):
        return other % self.arg

    def __cmp__(self, other):
        return cmp(self.arg, other)


candidates = [ 2, 4.0, 2L, 2+0j, [1], (2,), None,
               MethodNumber(2), CoerceNumber(2)]

infix_binops = [ '+', '-', '*', '/', '**', '%' ]
prefix_binops = [ 'divmod' ]

def format_float(value):
    if abs(value) < 0.01:
        return '0.0'
    else:
        return '%.1f' % value

# avoid testing platform fp quirks
def format_result(value):
    if isinstance(value, complex):
        return '(%s + %sj)' % (format_float(value.real),
                               format_float(value.imag))
    elif isinstance(value, float):
        return format_float(value)
    return str(value)

def do_infix_binops():
    for a in candidates:
        for b in candidates:
            for op in infix_binops:
                print '%s %s %s' % (a, op, b),
                try:
                    x = eval('a %s b' % op)
                except:
                    error = sys.exc_info()[:2]
                    print '... %s.%s' % (error[0].__module__, error[0].__name__)
                else:
                    print '=', format_result(x)
                try:
                    z = copy.copy(a)
                except copy.Error:
                    z = a # assume it has no inplace ops
                print '%s %s= %s' % (a, op, b),
                try:
                    exec('z %s= b' % op)
                except:
                    error = sys.exc_info()[:2]
                    print '... %s.%s' % (error[0].__module__, error[0].__name__)
                else:
                    print '=>', format_result(z)

def do_prefix_binops():
    for a in candidates:
        for b in candidates:
            for op in prefix_binops:
                print '%s(%s, %s)' % (op, a, b),
                try:
                    x = eval('%s(a, b)' % op)
                except:
                    error = sys.exc_info()[:2]
                    print '... %s.%s' % (error[0].__module__, error[0].__name__)
                else:
                    print '=', format_result(x)

# New-style class version of CoerceNumber
class CoerceTo(object):
    def __init__(self, arg):
        self.arg = arg
    def __coerce__(self, other):
        if isinstance(other, CoerceTo):
            return self.arg, other.arg
        else:
            return self.arg, other

def assert_(expr, msg=None):
    if not expr:
        raise AssertionError, msg

def do_cmptypes():
    # Built-in tp_compare slots expect their arguments to have the
    # same type, but a user-defined __coerce__ doesn't have to obey.
    # SF #980352
    evil_coercer = CoerceTo(42)
    # Make sure these don't crash any more
    assert_(cmp(u'fish', evil_coercer) != 0)
    assert_(cmp(slice(1), evil_coercer) != 0)
    # ...but that this still works
    class WackyComparer(object):
        def __cmp__(self, other):
            assert_(other == 42, 'expected evil_coercer, got %r' % other)
            return 0
    assert_(cmp(WackyComparer(), evil_coercer) == 0)
    # ...and classic classes too, since that code path is a little different
    class ClassicWackyComparer:
        def __cmp__(self, other):
            assert_(other == 42, 'expected evil_coercer, got %r' % other)
            return 0
    assert_(cmp(ClassicWackyComparer(), evil_coercer) == 0)

warnings.filterwarnings("ignore",
                        r'complex divmod\(\), // and % are deprecated',
                        DeprecationWarning,
                        r'test.test_coercion$')
do_infix_binops()
do_prefix_binops()
do_cmptypes()
