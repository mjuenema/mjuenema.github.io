# PyParsing and Cython

The other day I started writing a parser for the output of the ``show access-lists`` command on Cisco network devices.
I remembered the *Building Compilers* class back at [Uni](https://www.thm.de/site/) where I "fought" with
Lex/[Bison](https://www.gnu.org/software/bison/) and YACC. 

Fortunately, for many cases there are easier alternatives to Lex/Bison these days, 
[PyParsing](https://pypi.org/project/pyparsing/) for example which is a Python
>> module is an alternative approach to creating and executing simple grammars, vs. the traditional 
>> lex/yacc approach, or the use of regular expressions. The pyparsing module provides a library of classes that 
>> client code uses to construct the grammar directly in Python code.

So how hard could it be? The answer is hard and relatively easy at the same time. I did succeed in writing a grammar
that was able to parse the approximately 190.000(!) lines of output of the ``show access-lists`` comamnd from a
production Cisco ASA firewall. I would have never been able to do this without PyParsing. On the other hand
the [parser became pretty complex](cisco-acl-parser.py) and it took several minutes for my script to complete (on my 
rather old PC).

**Note**: I am unable to provide the `output_of_show_access.txt` file as it is from a production firewall.

```
$ pip install pyparsing
$ time python3 cisco-acl-parser.py output_of_show_access-lists.txt
real	6m39.401s
user	6m31.038s
sys	0m0.077s

```

The obvious question was how one can make this faster? 

* Option A: I am certain there are ways to make my PyParsing grammar more better or generally make my script 
  more efficient. I am happy for any suggestions.
* Option B: Make PyParsing faster through the [Cython](https://cython.org/) compiler for Python modules.

Given the title of this article the choice was clear. Can one make PyParsing faster by converting it into C code? 

## cPyparsing: PyParsing + Cython

As always I am not the first person to come up with this idea. The [cPyparsing](https://pypi.org/project/cPyparsing/)
package is a Cython implementation of PyParsing, so let's try that.

```
$ pip install cpyparsing
$ time python3 cisco-acl-parser.py output_of_show_access-lists.txt cpyparsing
real	4m29.411s
user	4m24.207s
sys	0m0.090s
```

The "PyParsing" version of my script took X:XX minutes to complete whereas the
"cPyparsing" version only took 4:24 minutes for the same task. That's a 20% improvement for no real effort
whatsoever. This is not meant as criticism of the PyParsing project. Keeping C code out of a Python project has
clear advantages and many parsers are probably less complex than mine anyway. Nevertheless it shows that
if needed a PyParsing application can possibly be made faster quite easily.

## Profiling PyParsing

So far, so good, but can one make it even faster. After all, making a script run 20% faster is nice but not a huge
improvement. What I should have done originally is to determine whether it is actually PyParsing that does most of 
the work or whether my script is inefficient. That's where the [profile](https://docs.python.org/3/library/profile.html)
module of the Python Standard Library comes into play. 

```
$ python3 -m profile -s tottime cisco-acl-parser.py output_of_show_access-lists.txt

```

