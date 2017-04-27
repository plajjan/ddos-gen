#!/usr/bin/python

############################
# Author: christian graf   #
# cgraf@juniper.net        #
# use at own risk          #
############################
# the script is intended to test robustness of the DUT's controlplane
# ideally the script can be fired up and the DUT does not loose any of its protocol-adjcencies
# nor any ND6 process fails due to overloading the controlplane
# use at own risk

# install BGPOpen
# 1) download bgp.py from here: https://github.com/levigross/Scapy/blob/master/scapy/contrib/bgp.py
# 2) copy it here: ./usr/local/lib/python2.7/dist-packages/scapy/contrib/bgp.py


from scapy.all import *
from scapy.contrib.bgp import BGPOpen
import sys,getopt,argparse,os.path, math
from netaddr import *

# default pcap-file and arg-parse string
outfile='ddos.pcap'
my_description='creates DDOS packets and saves them into ' + outfile + ". Example: " + './ddos-gen.py --bgp --smac 00:0c:29:9e:c2:e0 --dmac 00:1d:b5:29:78:31 --subs 2000'

# sorting args to functionality
################################
# parser = argparse.ArgumentParser(description='creates DDOS packets and saves them into ', outfile )
parser = argparse.ArgumentParser(description=my_description)

# general
##################
parser.add_argument('-dmac','--dmac', help='defines destination mac , default 22:22:22:22:22:22', default='22:22:22:22:22:22', required=False)
parser.add_argument('-smac','--smac', help='defines initial source mac , default 23:22:22:22:22:22', default='23:22:22:22:22:22', required=False)
parser.add_argument('-dip','--dip', help='defines destination IPv6, default 2001:db8:100::1', default='2001:db8:100::1', required=False)
parser.add_argument('-sip','--sip', help='defines initial source IPv6, default 2003:1c08:20:0ff::1', default='2003:1c08:20:ff::1', required=False)
parser.add_argument('-subs','--subs', help='total amount of subscribers to use. For each subscriber the tool will create one packet per selected protocol', type=int, default=2, required=False)
parser.add_argument('-sps','--sources_per_subscriber', help='As the subscribers have a rather large cidr-block, this knob turns on multiple sources per subscriber. Default is 1', type=int, default=1, required=False)
parser.add_argument('-pcap_file','--pcap_file', help='if provided, the resulting pcap-file will be saved under provided name, default=ddos.pcap', default=outfile, required=False)

# vlans
parser.add_argument('-vid','--vid', help='omit this knob to generate untagged traffic. enter single VID for single-tagged traffic and enter komma-sperated (a,b) inner,outer (cVLAN,SVLAN) VID to generate double-tagged traffic', default='False', required=False)

# enabling the traffic patterns
parser.add_argument("--bfd", default=False, action="store_true" , help="uses same ports as BFD, but is not a real bfd-packet. bfd single and multihop are addressed")
parser.add_argument("--icmp_request", default=False, action="store_true" , help="enables icmp echo-requests to configured destination")
parser.add_argument("--bgp", default=False, action="store_true" , help="set --bgp to enable bgp traffic generation")
parser.add_argument("--dhcp_solicit", default=False, action="store_true" , help="set --dhcp-solicit to enable dhcp-solicit messages as seen from subscriber to R1")

# all-knob
parser.add_argument("--all", default=False, action="store_true" , help="set this knob to turn on all available tests (bfd,bgp,icmp,..)")

# offset / distributed or non-distributed
parser.add_argument("--offset", default=0x0, type=str, help="for terastream use 0x1000000000000000000 as offset between the vlans. SIP: default starting value could be 2003:1c08:20:0ff::/64 i.e. 0x20031c08002001ff0000000000000000 SIP prefix = start + (customer_id * 0x1000000000000000000) So the result would be that for the 1st customer you have: VLAN 2001 SIP prefix  2003:1c08:20:1ff::/64 2nd customer: VLAN 2002 SIP  prefix 2003:1c08:20:2ff::/64")


# last statement args
args = parser.parse_args()

##############
# main program
##############

## open the pcap-file for writing and optional delete old pcap
# always delete default file
if (os.path.isfile(outfile)):
        os.remove(outfile)

# check if file exists only if non-default name is provided
if (args.pcap_file<>outfile):
  if (os.path.isfile(args.pcap_file)):
    print "the output-file already exists"
    print "The file //", args.pcap_file, "// will be overwritten. Please enter \"yes\" if the file shall be overwritten or \"no\" to exit the prog"
    temp  = raw_input("enter [yes] / [no] : ")
    if (temp <> 'yes'):
        print "====== will exit now ========"
        exit()
    else:
        os.remove(args.pcap_file)
pktdump = PcapWriter(str(args.pcap_file), append=True, sync=False)


# checking keyword all
# if all is set, then any wanted argument needs to be enabled here
if args.all == True:
    args.bfd          = True
    args.bgp          = True
    args.dhcp_solicit = True
    args.icmp_request = True

offset = str(args.offset)
ip_increment= (args.subs-1) * int(offset,16)
end_ip=IPAddress(args.sip)
end_ip = end_ip + ip_increment

print "."
# print used values
print "used values"
print "==========="
print "dest mac         :", args.dmac
print "src mac          :", args.smac
print "dest. ip         :", args.dip
print "src ip - start   :", args.sip
print "src ip - end     :", end_ip
print "amount customers :", args.subs
print "pcap-file        :", args.pcap_file
print "vlan-id          :", args.vid
print "."

print "enabled protocols"
print "================="
if args.bfd == True:
   print "BFD"
if args.bgp == True:
   print "BGP"
if args.dhcp_solicit == True:
   print "dhcp solicit"
if args.icmp_request == True:
   print "icmp request"

print "."
print "distributed or non-distributed pattern"
print "--------------------------------------"
if args.offset <> 0:
  print "using distributed traffic pattern, based on offset given"
else:
  print "all generated traffic using static/single src-ip" 
print "."
print "."
print "."
print "starting populating the pcap-file"
print "================================="
 
## traffic generation
## this is the outer-loop, defined by the number of total subscribers
packet_count=0
for x in range(0,args.subs):

   # Variables
   ###########
   
   # multicast mac destination required for e.g. dhcpv6 solicit
   multicast_MAC     = '33:33:00:01:00:02'  

   # ip setting
   # modifier and variance is defined here
   dhcp_dst = "ff02::1:2"

   # udp/tcp
   src_port_static   = 1024
   src_port_variance = 1024+x
   dhcp_sport        = 546
   dhcp_dport        = 547
   bfd_multihop      = 4784
   bfd_control       = 3784
   bfd_echo          = 3785
   bfd_srcport       = random.randint(49152,65535)
   
   # this is the inner loop, reiterating through the sources_per_subscriber
   for y in range (0,args.sources_per_subscriber):
	   # l3 src address gets incremented with each outer and inner loop
	   ip_increment= x * int(offset,16) + y
	   src_ip=IPAddress(args.sip)
	   src_ip = src_ip + ip_increment
	   l3=IPv6(src=str(src_ip),dst=args.dip)
	   # l2 header
	   ## check if packets shall be untagged, single-tagged or double-tagged
	   ## with each subscriber (args.subs) the vlan-id is incremented
	   if args.vid <> 'False':
	       # packets are either tagged or double-tagged
	       help=args.vid.split(",")
	       # single tagged
	       if len(help) == 1:
		   # make sure with each run the svlan gets incremented
		   svlan=int(help[0])+x
		   print "single tagged"
		   l2=Ether(src=args.smac, dst=args.dmac)/Dot1Q(vlan=svlan)
		   l2_mcast=Ether(src=args.smac, dst=multicast_MAC)/Dot1Q(vlan=svlan)
		   l2.show()

	       if len(help) == 2:
		   # make sure with each run the svlan gets incremented
		   svlan=int(help[0])+x
		   cvlan=int(help[1])
		   print "double tagged"
		   l2=Ether(src=args.smac, dst=args.dmac)/Dot1Q(vlan=svlan)/Dot1Q(vlan=cvlan)
		   l2_mcast=Ether(src=args.smac, dst=multicast_MAC)/Dot1Q(vlan=svlan)/Dot1Q(vlan=cvlan)
	   else:
	       # args.vid is default False, hence untagged
	       # print "packet is untagged"
	       l2=Ether(src=args.smac, dst=args.dmac, type=0x86dd)
	       l2_mcast=Ether(src=args.smac, dst=multicast_MAC, type=0x86dd)

	   # bgp
	   # for bgp two different flavors are beeing launched
	   # first a single source is generating multiple sockets to same target
	   # second multiple sources are firing against same target

	   if args.bgp == True:
	       if x == 0:
		   print "starting: bgp traffic generation "
	       # launching multiple sockets from same src-IP
	       packet=l2/l3/TCP(sport=src_port_variance,dport=179)/BGPOpen()
	       packet_count += 1
	       pktdump.write(packet)

	   # dhcp solicit
	   if args.dhcp_solicit == True:
	       if x == 0:
		   print "starting: dhcp-solicit generation "
	       sol = DHCP6_Solicit()
	       iana = DHCP6OptIA_NA()
	       rc = DHCP6OptRapidCommit()
	       et= DHCP6OptElapsedTime()
	       cid = DHCP6OptClientId()
	       opreq = DHCP6OptOptReq()
	       packet = l2_mcast/IPv6(src=str(src_ip),dst=dhcp_dst)/UDP(sport=dhcp_sport,dport=dhcp_dport)/sol/iana/rc/et/cid/opreq
	       packet_count += 1
	       pktdump.write(packet)

	   # icmp_request
	   if args.icmp_request == True:
	       if x == 0:
		   print "starting: icmp echo-request"
	       packet=l2/l3/ICMPv6EchoRequest()
	       packet_count += 1
	       pktdump.write(packet)

	   # bfd
	   # note: its not a real bfd-packet, its just using the port-range for bfd
	   if args.bfd == True:
	       if x == 0:
		   print "starting: BFD"
	       # generating bfd_control packets
	       packet=l2/l3/UDP(sport=bfd_srcport, dport=bfd_control)
	       packet_count += 1
	       pktdump.write(packet)
	       # bfd_multihup 
	       packet=l2/l3/UDP(sport=bfd_srcport, dport=bfd_multihop)
	       packet_count += 1
	       pktdump.write(packet)
	       # bfd echo
	       packet=l2/l3/UDP(sport=bfd_srcport, dport=bfd_echo)
	       packet_count += 1
	       pktdump.write(packet)
print "===="
print "writing file ", args.pcap_file
pktdump.close()
print "Number of packets written into file ", args.pcap_file, " : ",packet_count
print "."
print "done"

# ddos commands MX
# #vty
# show ddos scfd asic-flows
# show ddos scfd asic-flow-rindex 0 2679
# show ddos policer bgp stats 
# show ddos policer bgp configuration  
# show ddos scfd asic-flows
# show ddos scfd global-info
# show ddos scfd asic-flows  
# show ddos scfd asic-flow-rindex 0 1439



