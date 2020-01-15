# Basic IPv6 on Cisco IOS

## Global settings

There are a couple of global settings that enable IPv6 on a Cisco router. The example below also shows two host name to IPv6 address mappings.

```
ip routing
ipv6 unicast-routing

ip cef
ipv6 cef

ipv6 host R1 FDFC:38C4:F0BE:FFFF::1
ipv6 host R2 FDFC:38C4:F0BE:FFFF::2
```

## Interfaces

The example below shows a dual-stack configuration for an Ethernet interface. 
`FDFC:38C4:F0BE/48` is the unique-local address (ULA) prefix registered with 
the [IPv6 ULA (Unique Local Address) RFC4193 Registration List](https://www.sixxs.net/tools/grh/ula/list/).
The IPv6 subnet on this interface is `...:1::...` and the host address is `...::1`.

```
# sh run int e1/0
interface Ethernet1/0
 ip address 192.168.1.1 255.255.255.0
 ipv6 address FDFC:38C4:F0BE:1::1/64
 ipv6 enable
```

The loopback interface is on IPv6 subnet `FFFF`. Like its IPv4 address, 
its IPv6 address has a netmask with all bits set (/128).

```
# sh run int lo0
interface Loopback0
 ip address 192.168.255.1 255.255.255.255
 ipv6 address FDFC:38C4:F0BE:FFFF::1/128
 ipv6 enable
```

The show ipv6 interface command displays IPv6 information for that interface

```
# sh ipv6 interface e1/0
Ethernet1/0 is up, line protocol is up
  IPv6 is enabled, link-local address is FE80::C801:32FF:FE70:1C
  Global unicast address(es):
    FDFC:38C4:F0BE:1::1, subnet is FDFC:38C4:F0BE:1::/64
  Joined group address(es):
    FF02::1
    FF02::2
    FF02::1:FF00:1
    FF02::1:FF70:1C
  MTU is 1500 bytes
  ICMP error messages limited to one every 100 milliseconds
  ICMP redirects are enabled
  ND DAD is enabled, number of DAD attempts: 1
  ND reachable time is 30000 milliseconds
  ND advertised reachable time is 0 milliseconds
  ND advertised retransmit interval is 0 milliseconds
  ND router advertisements are sent every 200 seconds
  ND router advertisements live for 1800 seconds
  Hosts use stateless autoconfig for addresses.
192.168.1.1/24 (IPv4)
FDFC:38C4:F0BE:1::1/64 (IPv6 unique-local address; ULA)
FE80::... (IPv6 link local)
ff02::1 (All nodes on the local network segment)
FF02::2 (All routers on the local network segment)
FF02::1:FF00:1 (Solicited-node multicast address; used for Neighbour-Disovery)
FF02::1:FF70:1C (???)
```

## Show IPv6 ...

### Neighbor Cache

```
# sh ipv6 neighbors [e1/0]
IPv6 Address                              Age Link-layer Addr State Interface
FE80::C802:32FF:FE7F:1C                     0 ca02.327f.001c  REACH Et1/0
FDFC:38C4:F0BE:1::2                         0 ca02.327f.001c  STALE Et1/0
```

### Routes

```
# sh ipv6 route
IPv6 Routing Table - 6 entries
Codes: C - Connected, L - Local, S - Static, R - RIP, B - BGP
       U - Per-user Static route
       I1 - ISIS L1, I2 - ISIS L2, IA - ISIS interarea, IS - ISIS summary
       O - OSPF intra, OI - OSPF inter, OE1 - OSPF ext 1, OE2 - OSPF ext 2
       ON1 - OSPF NSSA ext 1, ON2 - OSPF NSSA ext 2
C   FDFC:38C4:F0BE:1::/64 [0/0]
     via ::, Ethernet1/0
L   FDFC:38C4:F0BE:1::1/128 [0/0]
     via ::, Ethernet1/0
C   FDFC:38C4:F0BE:4::/64 [0/0]
     via ::, Ethernet1/1
L   FDFC:38C4:F0BE:4::1/128 [0/0]
     via ::, Ethernet1/1
L   FE80::/10 [0/0]
     via ::, Null0
L   FF00::/8 [0/0]
     via ::, Null0
```

## OSPFv3

OSPFv3 expands on OSPF version 2 to provide support for IPv6 routing prefixes and
the larger size of IPv6 addresses. In regards to configuring OSPFv3 on Cisco IOS there
are two key differences to OSPFv2.

* In OSPFv3, a routing process does not need to be explicitly created. Enabling OSPFv3
  on an interface will cause a routing process, and its associated configuration,
  to be created. One may still want to customise OSPFv3 parameters that are not
  interface specific.
* In OSPFv3, each interface must be enabled using commands in interface configuration
  mode. This feature is different from OSPF version 2, in which interfaces are
  indirectly enabled using the device configuration mode.

OSPFv3 can be used for IPv6 and IPv4 as long as separate OSPF processes are used.
You may want to use OSPFv2 for IPv4 and OSPFv3 only for IPv6. The example below
configures a single OSPFv3 zone for IPv6 only.

Enabling OSPFv3 authentication is so simple that there is no reason for not doing so.

```
# sh run
interface Ethernet1/0
  ...
  ipv6 ospf 1 area 0

ipv6 router ospf 1
 log-adjacency-changes
 redistribute connected
 area 0 authentication ipsec spi 1000 md5 8B800BD784E62C8C8B0A8DEA3451A25E
```
