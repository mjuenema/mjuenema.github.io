
Testing Python code with Hypothesis

According to its web page "Hypothesis is a new generation of tools for automating your testing process. It combines human understanding of your problem domain with machine intelligence to improve the quality of your testing process while spendingless time writing tests." That sounds all nice and fancy but what does this in mean in practice? This article provides a quick introduction to Hypothesis, just to whet your appetite. The official documentation provides a more extensive tutorial.

Hypothesis is available on PyPi and can be easily installed through pip. Hypothesis works in conjunction with a Python test suite. My personal preference is Nose but others are supported, too.

$ pip install hypothesis nose
Collecting hypothesis
Collecting nose
  Using cached nose-1.3.7-py2-none-any.whl
Collecting enum34 (from hypothesis)
  Using cached enum34-1.1.6-py2-none-any.whl
Installing collected packages: enum34, hypothesis, nose
Successfully installed enum34-1.1.6 hypothesis-3.6.1 nose-1.3.7

For the purpose of this article I am going to explain how Hypothesis works with a simple custom division() function that accepts numbers or strings containing numbers. I admit that this example is rather contrived but it serves the purpose of this article really well. The first listing implements the test functions with some assistance of Nose.

# example1.py
from nose.tools import raises

def division(x, y):
    return float(x) / float(y)

def test_div():
    """Test numbers and strings."""
    assert division(4, 2.0) == division('4', '2.0')

@raises(ZeroDivisionError)
def test_divzero():
    """Test division by zero."""
    division('4', 0)

What is immediately obvious is that only a very limited set of possible arguments to division() is tested. Most people can immediately think of additional combinations of integers, floats and string representations worth testing.

$ nosetests example1.py 
..
----------------------------------------------------------------------
Ran 2 tests in 0.000s

OK

The second example adds tests for numbers from 1 to 10, also as floats and strings.

# example2.py

from nose.tools import raises

def division(x, y):
    return float(x) / float(y)

def check_division(x, y):
    assert division(x, y) == 2.0

def test_div():
    """Test numbers and strings."""
    for i in range(1, 10):
        yield division, i*2, i
        yield division, float(i*2), i
        yield division, i*2, float(i)
        yield division, float(i*2), float(i)
        yield division, i*2, str(i)
        yield division, str(i*2), i
        # and so forth...

@raises(ZeroDivisionError)
def test_divzero():
    """Test division by zero."""﻿﻿
    division('4', 0)

It covers many more combinations, but is still limited to a tiny subset of possible numbers. It also doesn't look very elegant?

$ nosetests example2.py 
.......................................................
----------------------------------------------------------------------
Ran 55 tests in 0.005s
OK

Like the first example it provides a specific test case for the ZeroDivisionError exception. But are there any other special cases? Maybe Hypothesis can find one.

The key objective of Hypothesis is to generate input data for test functions. And it does so very cleverly. Let's rewrite the test and use Hypothesis. Through the @given decorator Hypothesis will create a series of integers to the test.

# example3.py

from nose.tools import raises
from hypothesis import given
from hypothesis.strategies import integers

def division(x, y):
    return float(x) / float(y)

@given(x=integers())
def test_div(x):
    """Test integers."""
    print x               # show value of x, normally not done!
    assert division(x*2, x) == 2.0

@raises(ZeroDivisionError)
def test_divzero():
    """Test division by zero."""﻿﻿
    division('4', 0)

Unfortunately the @given(x=integers()) line introduces the ZeroDivisionError into the test. This was bound to happen as 0 is a valid integer. Note that the output clearly shows what input caused the test to fail (Falsifying example: ...) and because of the print statement in the code it also shows the different other integer values Hypothesis tried.

$ nosetests example3.py 
E.
======================================================================
ERROR: example3.test_div
----------------------------------------------------------------------
Traceback (most recent call last):
[...]
ZeroDivisionError: float division by zero
-------------------- >> begin captured stdout << ---------------------
-86
38698778983165550746815151433416776989
130775184150007723213375339326718763618
-149
-60717049783932157206209978973119425965
0
0
0
Falsifying example: test_div(x=0)
0
--------------------- >> end captured stdout << ----------------------
----------------------------------------------------------------------
Ran 2 tests in 0.011s
FAILED (errors=1)

Quite clearly we have to amend the code to prevent Hypothesis causing the ZeroDivisionError exception. The assume function serves this purpose.

# example4.py

from nose.tools import raises
from hypothesis import given, assume
from hypothesis.strategies import integers

def division(x, y):
    return float(x) / float(y)

@given(x=integers())
def test_div(x):
    """Test non-zero integers."""
    assume(x <> 0)                      # <-----------

    print x    # show value of x, normally not done!
    assert division(x*2, x) == 2.0

@raises(ZeroDivisionError)
def test_divzero():
    """Test division by zero."""
    division('4', 0)
Now the tests pass.

$ nosetests example4.py 
..
----------------------------------------------------------------------
Ran 2 tests in 0.045s
OK

But what about other numbers than integers? The next example adds floats to the mix.

# example5.py

﻿from nose.tools import raises
from hypothesis import given, assume
from hypothesis.strategies import integers, floats, one_of

def division(x, y):
    return float(x) / float(y)

@given(one_of(integers(), floats()))       # <-----------
def test_div(x):
    """Test integers and floats."""﻿
    assume(x <> 0)
    print x
    assert division(x*2, x) == 2.0

@raises(ZeroDivisionError)
def test_divzero():
    """Test division by zero."""﻿﻿﻿
    division('4', 0)

Interestingly adding floats causes some trouble with really large values like 8.98846567431158e+307 in this example.

$ nosetests example5.py
F.
======================================================================
FAIL: example5.test_div
----------------------------------------------------------------------
Traceback (most recent call last):
[...]
    assert division(x*2, x) == 2.0
AssertionError: 
-------------------- >> begin captured stdout << ---------------------
[...]
2.38756119474e+307
8.9873684495e+307
8.98846567431e+307
Falsifying example: test_div(x=8.98846567431158e+307)
8.98846567431e+307
--------------------- >> end captured stdout << ----------------------
----------------------------------------------------------------------
Ran 2 tests in 0.500s
FAILED (failures=1)

The cause of the failure becomes obvious when one executes the mathematical operation in the Python shell.

>>> 8.98846567431158e+307*2/8.98846567431158e+307 == 2.0
False

>>> 8.98846567431158e+307*2/8.98846567431158e+307
inf

>>> 8.98846567431158e+307*2
inf

Hypothesis is really good at finding such corner-cases. Although in this example it does not actually break the division() function, few people would have thought of this case without the help of Hypothesis. I certainly hadn't.

I hope this article provided a very brief introduction to Hypothesis and what value it adds to testing Python code. Check out the Hypothesis documentation as there are many more features.

I plan to add Hypothesis based testing to my Python projects soon but I somehow fear the outcome ;-)
