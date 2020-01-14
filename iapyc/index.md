# Infrastructure as Python Code

>> This is an updated version of an article I 
>> [published on Linkedin](https://www.linkedin.com/pulse/infrastructure-python-code-iapyc-markus-juenemann/)
>> in July 2017.

[Terraform](https://www.terraform.io/) is a prominent example of the 
[Infrastructure as Code (IAC)](https://en.wikipedia.org/wiki/Infrastructure_as_Code) concept.
A configuration file in text format (either in [Hashicorp's HCL format](https://github.com/hashicorp/hcl)
or alternatively in JSON) describes an entire infrastructure that is to be managed.

HCL is a declarative language with only very limited support for control structures. This 
[blog entry](https://blog.gruntwork.io/terraform-tips-tricks-loops-if-statements-and-gotchas-f739bbae55f9)
by Yevgeniy Brikman (the author of the book ["Terraform: Up and Running"](http://www.terraformupandrunning.com/))
explains how to perform advanced tips & tricks, such as how to do loops and if-statements. While this is
certainly very clever it is also simply "too clever".

## Generating JSON programatically

JSON, of course, does not support any control-structures at all. Also JSON is cumbersome to write by hand.
Fortunately programming languages like Python, Ruby, Perl, etc. have modules that can easily generate
Terraform compliant JSON files, utilising all the loops, conditionals and data structures they provide.

```python
# Hard-coded here, but in a real scenario this could be a 
# command line argument.
PROD=True

# Python example to create Terraform JSON with one or two EC2 instances
# depending on whether PROD is True or False.
d = {'provider': {'aws': {'access_key': 'ACCESS_KEY_HERE',
                          'region': 'us-east-1',
                          'secret_key': 'SECRET_KEY_HERE'}},
    'resource': {'aws_instance': {}}}
						  
if PROD:
	# Add a two EC2 m4.large instance2
	d['resource']['aws_instance']['i1'] = {'ami': 'ami-2757f631', 
	                                       'instance_type': 'm4.large'}
	d['resource']['aws_instance']['i2'] = {'ami': 'ami-2757f631', 
	                                       'instance_type': 'm4.large'}
else:
	# Add a single EC2 t2.micro instance
    d['resource']['aws_instance']['i1'] = {'ami': 'ami-2757f631', 
                                           'instance_type': 't2.micro'}

print(json.dumps(d))
```

The Python script would produce the following output which is a valid Terraform configuration.

```
{
  "provider": {
    "aws": {
      "secret_key": "SECRET_KEY_HERE",
      "region": "us-east-1",
      "access_key": "ACCESS_KEY_HERE"
    }
  },
  "resource": {
    "aws_instance": {
      "i1": {
        "instance_type": "m4.large",
        "ami": "ami-2757f631"
      },
      "i2": {
        "instance_type": "m4.large",
        "ami": "ami-2757f631"
      }
    }
  }
}
```

Most people would agree that the script used to generate this JSON output doesn't look very pretty
at all. It contains lots of repeating code and the nested dictionary data structure is really only
a shallow abstraction from JSON.

## Introducing Python-Terrascript

A much higher level of abstraction would be nice and this is exactly what my
[Python-Terrascript](https://github.com/mjuenema/python-terrascript) package aims for.

>>> This example has been updated to reflect Python-Terrascript release 0.8.

```python
import terrascript
import terrascript.provider
import terrascript.resource

# Hard-coded here, but in a real scenario this could be a 
# command line argument.
PROD=True

# Start a Terrascript configuration.
config = terrascript.Terrascript()

# Add a provider
config += terrascript.provider.aws(access_key='ACCESS_KEY_HERE',
                                   secret_key='SECRET_KEY_HERE',
                                   region='us-east-1')

if PROD:
    config += terrascript.resource.aws_instance('i1', ami='ami-2757f631', instance_type='m4.large')
    config += terrascript.resource.aws_instance('i2', ami='ami-2757f631', instance_type='m4.large')
else:
    config += terrascript.resource.aws_instance('i1', ami='ami-2757f631', instance_type='t2.micro')

# Printing the configuration will output JSON.
print(config)
```

The script above looks a lot more like a proper program and will produce the same output as the previous example.

The Python-Terrascript [documentation](https://python-terrascript.readthedocs.io/en/develop/) contains many more
examples.
