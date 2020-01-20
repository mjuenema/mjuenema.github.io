#!/usr/bin/env python

import sys
import ipaddress


# Import different versions on PyParsing depending
# on the second command line argument.
try:
    if sys.argv[2] == 'cpyparsing':
        import cPyparsing as pp
except IndexError:
    import pyparsing as pp

pp.ParserElement.enablePackrat()


# Keywords
#
k_access_list = pp.Keyword('access-list')
k_any4 = pp.Keyword('any4')
k_any6 = pp.Keyword('any6')
k_any = pp.Keyword('any')
k_deny = pp.Keyword('deny')
k_eq = pp.Keyword('eq')
k_extended = pp.Keyword('extended')
k_gt = pp.Keyword('gt')
k_hitcnt = pp.Keyword('hitcnt')
k_host = pp.Keyword('host')
k_icmp = pp.Keyword('icmp')
k_interval = pp.Keyword('interval')
k_ip = pp.Keyword('ip')
k_line = pp.Keyword('line')
k_log = pp.Keyword('log')
k_lt = pp.Keyword('lt')
k_permit= pp.Keyword('permit')
k_range = pp.Keyword('range')
k_standard = pp.Keyword('standard')
k_tcp = pp.Keyword('tcp')
k_udp = pp.Keyword('udp')
k_inactive = pp.Keyword('inactive')
k_disable = pp.Keyword('disable')
k_default = pp.Keyword('default')
k_object = pp.Keyword('object')
k_object_group = pp.Keyword('object-group')
k_time_range = pp.Keyword('time-range')


# Literals
#
l_close_bracket = pp.Literal(')')
l_open_bracket = pp.Literal('(')
l_dot = pp.Literal('.')
l_equal = pp.Literal('=')


# Tokens
#
t_access_list_name = pp.Word(pp.alphanums+'-'+'_').setResultsName('aclname')
t_access_list_type = (k_standard|k_extended).setResultsName('type')
t_action = (k_permit|k_deny).setResultsName('action')
t_comparison = (k_eq|k_gt|k_lt)
t_hash = pp.Word(pp.alphanums).setResultsName('hash')
t_hitcnt_count = pp.Word(pp.nums).setResultsName('hitcnt')
t_octet = pp.Word(pp.nums, max=3)
t_ipaddress = pp.Combine(t_octet + l_dot + t_octet + l_dot + t_octet + l_dot + t_octet)
t_line_number = pp.Word(pp.nums).setResultsName('linenumber')
t_loginterval = pp.Word(pp.nums).setResultsName('loginterval')
t_loglevel = pp.Word(pp.alphas).setResultsName('loglevel')
t_port = pp.Word(pp.alphanums + '-')
# Dynamically generate all possible IPv4 netmasks
t_netmask = pp.Or([str(ipaddress.IPv4Network('10.0.0.0/{}'.format(m), strict=False).netmask) for m in range(0, 33)])
t_inactive = l_open_bracket + k_inactive + l_close_bracket
t_object_name = pp.Word(pp.alphanums + '_')
t_time_range_name = pp.Word(pp.alphanums)


# Objects and object groups
#
c_object = k_object + t_object_name
c_object_group = k_object_group + t_object_name

# Protocol
#
c_proto = (k_ip | k_icmp | k_tcp | k_udp | c_object | c_object_group).setResultsName('protocol')

# Addresses
#
c_address_host = k_host + t_ipaddress
c_address_ipv4 = t_ipaddress + t_netmask
c_address_any = k_any | k_any4 | k_any6
c_address_range = k_range + t_ipaddress + t_ipaddress
c_address_object = k_object + t_object_name

# Source and Destination Address
#
c_source = (c_address_host | c_address_ipv4 | c_address_any | c_address_range | c_address_object).setResultsName('src')
c_destination = (c_address_host | c_address_ipv4 | c_address_any | c_address_range | c_address_object).setResultsName('dest')

# Ports
#
c_port_comparison = t_comparison + t_port
c_port_object = k_object + t_object_name

# Source and Destination Ports
#
c_source_port = c_port_comparison | c_port_object
c_destination_port = c_port_comparison | c_port_object


# Logging
#
c_logging = k_log + pp.Optional(t_loglevel) + (pp.Optional(k_interval + t_loginterval) | k_disable | k_default)

# Activation
#
c_activation = k_inactive | (k_time_range + t_time_range_name)


# access-list alternative-ftp-ports line 1 extended permit tcp any any eq 10021 (hitcnt=9) 0x4933c22f

# Parser
#
parser = k_access_list + \
         t_access_list_name.setResultsName('name') + \
         k_line + \
         t_line_number.setResultsName('line') + \
         t_access_list_type.setResultsName('type') + \
         t_action.setResultsName('action') + \
         c_proto.setResultsName('protocol') + \
         c_source.setResultsName('source') + \
         pp.Optional(c_source_port.setResultsName('source_port')) + \
         pp.Optional(c_destination.setResultsName('destination')) + \
         pp.Optional(c_destination.setResultsName('destination_port')) + \
         pp.Optional(c_logging.setResultsName('logging')) + \
         pp.Optional(c_activation.setResultsName('activation'))

with open(sys.argv[1], 'rt') as fp:

    for line in fp:
        line = line.strip()

        # Skip some lines 
        if ';' in line:
            # access-list Other-RP-Groups; 2 elements; name hash: 0x937d0a07
            continue
        elif 'object-group' in line:
            # object groups appear expanded
            continue
        elif 'remark' in line:
            # Don't bother about remarks
            # access-list acl-in-fms line 34 remark HTTP Access to Transurban PC for view of TU LUMS
            continue
        elif 'standard' in line:
            # Later
            continue

        # Parse the input line but ignore the return value.
        parser.parseString(line)
