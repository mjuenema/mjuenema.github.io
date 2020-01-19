#!/usr/bin/env python


DEBUG = False

import sys
import ipaddress

import pyparsing as pp
pp.ParserElement.enablePackrat()


class Parser():

    def __init__(self):

        # Keywords
        #
        k_access_list = pp.Keyword('access-list').setDebug(DEBUG)
        k_any4 = pp.Keyword('any4').setDebug(DEBUG)
        k_any6 = pp.Keyword('any6').setDebug(DEBUG)
        k_any = pp.Keyword('any').setDebug(DEBUG)
        k_deny = pp.Keyword('deny').setDebug(DEBUG)
        k_eq = pp.Keyword('eq').setDebug(DEBUG)
        k_extended = pp.Keyword('extended').setDebug(DEBUG)
        k_gt = pp.Keyword('gt').setDebug(DEBUG)
        k_hitcnt = pp.Keyword('hitcnt').setDebug(DEBUG)
        k_host = pp.Keyword('host').setDebug(DEBUG)
        k_icmp = pp.Keyword('icmp').setDebug(DEBUG)
        k_interval = pp.Keyword('interval').setDebug(DEBUG)
        k_ip = pp.Keyword('ip').setDebug(DEBUG)
        k_line = pp.Keyword('line').setDebug(DEBUG)
        k_log = pp.Keyword('log').setDebug(DEBUG)
        k_lt = pp.Keyword('lt').setDebug(DEBUG)
        k_permit= pp.Keyword('permit').setDebug(DEBUG)
        k_range = pp.Keyword('range').setDebug(DEBUG)
        k_standard = pp.Keyword('standard').setDebug(DEBUG)
        k_tcp = pp.Keyword('tcp').setDebug(DEBUG)
        k_udp = pp.Keyword('udp').setDebug(DEBUG)
        k_inactive = pp.Keyword('inactive').setDebug(DEBUG)
        k_disable = pp.Keyword('disable').setDebug(DEBUG)
        k_default = pp.Keyword('default').setDebug(DEBUG)
        k_object = pp.Keyword('object').setDebug(DEBUG)
        k_object_group = pp.Keyword('object-group').setDebug(DEBUG)
        k_time_range = pp.Keyword('time-range').setDebug(DEBUG)


        # Literals
        #
        l_close_bracket = pp.Literal(')').setDebug(DEBUG)
        l_open_bracket = pp.Literal('(').setDebug(DEBUG)
        l_dot = pp.Literal('.').setDebug(DEBUG)
        l_equal = pp.Literal('=').setDebug(DEBUG)

    
        # Tokens
        #
        t_access_list_name = pp.Word(pp.alphanums+'-'+'_').setResultsName('aclname').setDebug(DEBUG)
        t_access_list_type = (k_standard|k_extended).setResultsName('type').setDebug(DEBUG)
        t_action = (k_permit|k_deny).setResultsName('action').setDebug(DEBUG)
        t_comparison = (k_eq|k_gt|k_lt).setDebug(DEBUG)
        t_hash = pp.Word(pp.alphanums).setResultsName('hash').setDebug(DEBUG)
        t_hitcnt_count = pp.Word(pp.nums).setResultsName('hitcnt').setDebug(DEBUG)
        t_octet = pp.Word(pp.nums, max=3).setDebug(DEBUG)
        t_ipaddress = pp.Combine(t_octet + l_dot + t_octet + l_dot + t_octet + l_dot + t_octet)
        t_line_number = pp.Word(pp.nums).setResultsName('linenumber').setDebug(DEBUG)
        t_loginterval = pp.Word(pp.nums).setResultsName('loginterval').setDebug(DEBUG)
        t_loglevel = pp.Word(pp.alphas).setResultsName('loglevel').setDebug(DEBUG)
        t_port = pp.Word(pp.alphanums + '-').setDebug(DEBUG)
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

        # Parser
        #
        self.parser = k_access_list + \
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


    def parse(self, config):

        lines = [line.strip() for line in config.split('\n')]
        data = []

        for line in lines:

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

            try:
                m = self.parser.parseString(line)
                data.append(m.asDict())
            except pp.ParseException:
                print(line)
                raise

        return data


def main():

    parser = Parser()

    with open(sys.argv[1], 'rt') as fp:
        config = fp.read()
    data = parser.parse(config)

    import pprint
    pprint.pprint(data)


if __name__ == '__main__':
    main()
        
