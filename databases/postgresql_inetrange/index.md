# `inetrange` type for PostgreSQL

One of my favourite things about PostgreSQL is that it provides the ``inet`` column type for storing 
[IP Addresses and Networks](https://www.postgresql.org/docs/10/datatype-net-types.html). The ``inet``
type coms with its own set of operators, like querying whether an IP Address is contained in a Network.

```sql
SELECT '192.168.1.1'::inet << '192.168.1.0/24'::inet;
 ?column? 
----------
 t
(1 row)
```

I am currently working on a Python script that is meant to parse the output from the ``show access-lists`` of Cisco
devices and store the parsed results in a PostgreSQL database for easier querying. The details of this are 
outside the scope of this article but the objective is to be able to answer questions like: "Is IP address 172.16.100.200
permitted to query 192.168.1.1 using the NTP protocol?" and similar. 

There is a little quirk when trying to implement this. Cisco allows the definition of IP Address ranges in their
configurations which don't have an equivalent type in PostgreSQL.

```
access-list MYACL line 3 extended permit tcp host 10.1.2.3 range 10.1.2.100 10.1.2.110 eq 123 (hitcnt=987) 0xaf8e0294
```

```
CREATE DATABASE example;
```

```
CREATE TYPE inetrange AS
(
    address1 inet,
    address2 inet
); 
```

```
SELECT ('192.168.1.10', '192.168.1.20')::inetrange;
             row             
-----------------------------
 (192.168.1.10,192.168.1.20)
(1 row)
```

```
CREATE TABLE address_ranges
(
  id serial,
  address_range inetrange
)
```

```
INSERT INTO address_ranges (address_range) VALUES (('192.168.1.10', '192.168.1.20'));
```

```
SELECT * FROM address_ranges;
 id |        address_range        
----+-----------------------------
  1 | (192.168.1.10,192.168.1.20)
(1 row)
```

```
SELECT (address_range).address1 FROM adress_ranges;
   address1   
--------------
 192.168.1.10
(1 row)
```

https://www.postgresql.org/docs/10/functions-net.html

```
CREATE FUNCTION inet_less_inetrange(inet, inetrange)
RETURNS boolean
AS 'SELECT $1 < ($2).address1'
LANGUAGE SQL
IMMUTABLE;
```

```
CREATE OPERATOR < 
(
  LEFTARG = inet,
  RIGHTARG = inetrange,
  PROCEDURE = inet_less_inetrange
);
```

```
SELECT '192.168.1.1'::inet < ('192.168.1.10', '192.168.1.20')::inetrange;
 ?column? 
----------
 t
(1 row)
```


```
SELECT '192.168.1.100'::inet < ('192.168.1.10', '192.168.1.20')::inetrange;
 ?column? 
----------
 f
(1 row)
```

```
SELECT '192.168.1.1'::inet > ('192.168.1.10', '192.168.1.20')::inetrange;
ERROR:  operator does not exist: inet > inetrange
LINE 1: SELECT '192.168.1.1'::inet > ('192.168.1.10', '192.168.1.20'...
                                   ^
HINT:  No operator matches the given name and argument types. You might need to add explicit type casts.
```


