#!/usr/bin/python

# version_2017_09_25

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

'''
changes 
2017_09_07  - adding random src-mac
2017_09_07  - adding spanning-tree conf and tcn attack
2017_09_07  - added lacp. note lacp=trace required
2017_09_07  - added snmpget
2017_09_25  - correcting random_src mac
2017_09_25  - added wire (replay) capability

'''

'''
some scapy general stuff
>>> ls (Ether)
dst        : DestMACField              = (None)
src        : SourceMACField            = (None)
type       : XShortEnumField           = (36864)

>>> b = ICMPv6ND_RA()
>>> b.display()
###[ ICMPv6 Neighbor Discovery - Router Advertisement ]###
  type= Router Advertisement
  code= 0
  cksum= None
  chlim= 0
  M= 0
  O= 0
  H= 0
  prf= High
  P= 0
  res= 0
  routerlifetime= 1800
  reachabletime= 0
  retranstimer= 0

>>> b.show()
###[ ICMPv6 Neighbor Discovery - Router Advertisement ]###
  type= Router Advertisement
  code= 0
  cksum= None
  chlim= 0
  M= 0
  O= 0
  H= 0
  prf= High
  P= 0
  res= 0
  routerlifetime= 1800
  reachabletime= 0
  retranstimer= 0
'''

###########
# usage
###########
# generate Router-advertisements for VID 2000
#./ddos-gen.py --RA --subs 1 -vid 2000
#

'''

###########
The most important:
###########
The target-host will only look at the packets if both the dst-ip and dst-mac is its own or a valid multicast-address.
So make sure whenever using this tool to have at least both the dmac and src-mac defined:

sudo ./ddos-gen.py --all  -subs 1 -sps 1  --wire p9p3 -RA_prefix 2a00:c37:428:22ff:: -RA_prefix_len 64 -llc fe80::2200:ff:fe00:1 -smac 23:22:22:22:22:22 -dmac 4c:96:14:e5:b6:21 -dip 2003:1a39:47:2::2 -vid 2000 -sip 2003:1a39:47:2::100


HOWTO REPLAY
============
use the tcpreplay tool. use either with pps to define pps or -t to run with topspeed
sudo tcpreplay --preload-pcap -i p9p3 -l 1000 --pps 15000  ddos.pcap

###########
# some words about the parameters offset, subscribers, Sources_per_subscriber

assume "--subs 4" knob is set. This means that the tool mimics 4 subscriber-lines. By default all subscribers would use same src-address:.
As the vlan was given, VID is beeing incremented with each subscriber.
Note that the src-ip stays constant, becasue per default the offset=0

./ddos-gen.py --bgp --subs 4 -sps 1 -vid 2000
20:01:39.616604 23:22:22:22:22:22 > 22:22:22:22:22:22, ethertype 802.1Q (0x8100), length 88: vlan 2000, p 0, ethertype IPv6, 2003:1c08:20:ff::1.1024 > 2001:db8:100::1.179: Flags [S], seq 0:10, win 8192, length 10: BGP, length: 10
20:01:39.619856 23:22:22:22:22:22 > 22:22:22:22:22:22, ethertype 802.1Q (0x8100), length 88: vlan 2001, p 0, ethertype IPv6, 2003:1c08:20:ff::1.1025 > 2001:db8:100::1.179: Flags [S], seq 0:10, win 8192, length 10: BGP, length: 10
20:01:39.622803 23:22:22:22:22:22 > 22:22:22:22:22:22, ethertype 802.1Q (0x8100), length 88: vlan 2002, p 0, ethertype IPv6, 2003:1c08:20:ff::1.1026 > 2001:db8:100::1.179: Flags [S], seq 0:10, win 8192, length 10: BGP, length: 10
20:01:39.625717 23:22:22:22:22:22 > 22:22:22:22:22:22, ethertype 802.1Q (0x8100), length 88: vlan 2003, p 0, ethertype IPv6, 2003:1c08:20:ff::1.1027 > 2001:db8:100::1.179: Flags [S], seq 0:10, win 8192, length 10: BGP, length: 10

Now lets add an offset. This shall change the src-ip for each subscriber
./ddos-gen.py --bgp --subs 4 -sps 1 -vid 2000 --offset 0x1000000000000000000
20:06:44.511854 23:22:22:22:22:22 > 22:22:22:22:22:22, ethertype 802.1Q (0x8100), length 88: vlan 2000, p 0, ethertype IPv6, 2003:1c08:20:ff::1.1024 > 2001:db8:100::1.179: Flags [S], seq 0:10, win 8192, length 10: BGP, length: 10
20:06:44.514946 23:22:22:22:22:22 > 22:22:22:22:22:22, ethertype 802.1Q (0x8100), length 88: vlan 2001, p 0, ethertype IPv6, 2003:1c08:20:1ff::1.1025 > 2001:db8:100::1.179: Flags [S], seq 0:10, win 8192, length 10: BGP, length: 10
20:06:44.517910 23:22:22:22:22:22 > 22:22:22:22:22:22, ethertype 802.1Q (0x8100), length 88: vlan 2002, p 0, ethertype IPv6, 2003:1c08:20:2ff::1.1026 > 2001:db8:100::1.179: Flags [S], seq 0:10, win 8192, length 10: BGP, length: 10
20:06:44.520950 23:22:22:22:22:22 > 22:22:22:22:22:22, ethertype 802.1Q (0x8100), length 88: vlan 2003, p 0, ethertype IPv6, 2003:1c08:20:3ff::1.1027 > 2001:db8:100::1.179: Flags [S], seq 0:10, win 8192, length 10: BGP, length: 10


to allow multiple src to be used by an subscriber, the -sps knob can be used. lets assume 2 sources per subscriber. for each range (defined by the offset) multiple src-ip's are generated
./ddos-gen.py --bgp --subs 4 -sps 2 -vid 2000 --offset 0x1000000000000000000
20:09:20.561390 23:22:22:22:22:22 > 22:22:22:22:22:22, ethertype 802.1Q (0x8100), length 88: vlan 2000, p 0, ethertype IPv6, 2003:1c08:20:ff::1.1024 > 2001:db8:100::1.179: Flags [S], seq 0:10, win 8192, length 10: BGP, length: 10
20:09:20.564388 23:22:22:22:22:22 > 22:22:22:22:22:22, ethertype 802.1Q (0x8100), length 88: vlan 2000, p 0, ethertype IPv6, 2003:1c08:20:ff::2.1024 > 2001:db8:100::1.179: Flags [S], seq 0:10, win 8192, length 10: BGP, length: 10
20:09:20.567197 23:22:22:22:22:22 > 22:22:22:22:22:22, ethertype 802.1Q (0x8100), length 88: vlan 2001, p 0, ethertype IPv6, 2003:1c08:20:1ff::1.1025 > 2001:db8:100::1.179: Flags [S], seq 0:10, win 8192, length 10: BGP, length: 10
20:09:20.570079 23:22:22:22:22:22 > 22:22:22:22:22:22, ethertype 802.1Q (0x8100), length 88: vlan 2001, p 0, ethertype IPv6, 2003:1c08:20:1ff::2.1025 > 2001:db8:100::1.179: Flags [S], seq 0:10, win 8192, length 10: BGP, length: 10
20:09:20.572972 23:22:22:22:22:22 > 22:22:22:22:22:22, ethertype 802.1Q (0x8100), length 88: vlan 2002, p 0, ethertype IPv6, 2003:1c08:20:2ff::1.1026 > 2001:db8:100::1.179: Flags [S], seq 0:10, win 8192, length 10: BGP, length: 10
20:09:20.576035 23:22:22:22:22:22 > 22:22:22:22:22:22, ethertype 802.1Q (0x8100), length 88: vlan 2002, p 0, ethertype IPv6, 2003:1c08:20:2ff::2.1026 > 2001:db8:100::1.179: Flags [S], seq 0:10, win 8192, length 10: BGP, length: 10
20:09:20.578886 23:22:22:22:22:22 > 22:22:22:22:22:22, ethertype 802.1Q (0x8100), length 88: vlan 2003, p 0, ethertype IPv6, 2003:1c08:20:3ff::1.1027 > 2001:db8:100::1.179: Flags [S], seq 0:10, win 8192, length 10: BGP, length: 10
20:09:20.581627 23:22:22:22:22:22 > 22:22:22:22:22:22, ethertype 802.1Q (0x8100), length 88: vlan 2003, p 0, ethertype IPv6, 2003:1c08:20:3ff::2.1027 > 2001:db8:100::1.179: Flags [S], seq 0:10, win 8192, length 10: BGP, length: 10



creating double-tagged frames with 802.1p marking
=================================================
./ddos-gen.py --bgp -vid 10,20 --dot1q_prio 4
10:07:44.928246 23:22:22:22:22:22 > 22:22:22:22:22:22, ethertype 802.1Q (0x8100), length 92: vlan 10, p 4, ethertype 802.1Q, vlan 20, p 4, ethertype IPv6, 2003:1c08:20:ff::1.1024 > 2001:db8:100::1.179: Flags [S], seq 0:10, win 8192, length 10: BGP, length: 10
10:07:44.932259 23:22:22:22:22:22 > 22:22:22:22:22:22, ethertype 802.1Q (0x8100), length 92: vlan 11, p 4, ethertype 802.1Q, vlan 20, p 4, ethertype IPv6, 2003:1c08:20:ff::1.1025 > 2001:db8:100::1.179: Flags [S], seq 0:10, win 8192, length 10: BGP, length: 10

changing dest mac address and entering a interface to wire the frames
=======================================================================
sudo ./ddos-gen.py --bgp -sps 100 -subs 1 -dmac 5c:45:27:ef:da:47  -vid 2001,2001 -wire p9p3


sending router-advertisements
==============================
1 subscriber configured, so the vlan stays constant at 2000.
The one subscriber has 4 hosts on wire. The advertised PIO gets chnaged with each  host

sudo ./ddos-gen.py --RA --subs 1 -sps 4 -vid 2000

lab@ubuntu1:~/cg-ubuntu1/ddos$ tcpdump -ne -r ddos.pcap
reading from file ddos.pcap, link-type EN10MB (Ethernet)
14:08:30.412134 23:22:22:22:22:22 > 33:33:00:00:00:01, ethertype 802.1Q (0x8100), length 122: vlan 2000, p 0, ethertype IPv6, fe80::2200:ff:fe00:1 > ff02::1: ICMP6, router advertisement, length 64

lab@ubuntu1:~/cg-ubuntu1/ddos$ tcpdump -nevv -r ddos.pcap | grep prefix
reading from file ddos.pcap, link-type EN10MB (Ethernet)
prefix info option (3), length 32 (4): 2a00:c37:428:22ff::/64, Flags [onlink, auto], valid time infinity, pref. time infinity
prefix info option (3), length 32 (4): 2a00:c37:428:2300::/64, Flags [onlink, auto], valid time infinity, pref. time infinity
prefix info option (3), length 32 (4): 2a00:c37:428:2301::/64, Flags [onlink, auto], valid time infinity, pref. time infinity
prefix info option (3), length 32 (4): 2a00:c37:428:2302::/64, Flags [onlink, auto], valid time infinity, pref. time infinity

# example for enabling all traffic patterns
sudo ./ddos-gen.py --all  -subs 1 -sps 1   -RA_prefix 2a00:c37:428:22ff:: -RA_prefix_len 64 -llc fe80::2200:ff:fe00:1 -smac a0:36:9f:58:41:7a -dmac 4c:96:14:e5:b6:01 -dip 2003:1a39:47:2::2  -sip 2003:1a39:47:2::100 -vid 2000 --wire p9p3

# replay the stuff

'''


######################################################
# program starts here                                #
######################################################

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
parser.add_argument('-smac','--smac', help='defines initial source mac , if not provided, than each packet will use a random src-mac. Format: aa:bb:cc:dd:ee:ff', default='random', required=False)
parser.add_argument('-dip','--dip', help='defines destination IPv6, default 2001:db8:100::1', default='2001:db8:100::1', required=False)
parser.add_argument('-sip','--sip', help='defines initial source IPv6, default 2003:1c08:20:0ff::1', default='2003:1c08:20:ff::1', required=False)
parser.add_argument('-subs','--subs', help='total amount of subscribers to use. For each subscriber the tool will create one packet per selected protocol', type=int, default=1, required=False)
parser.add_argument('-sps','--sources_per_subscriber', help='As the subscribers have a rather large cidr-block, this knob turns on multiple sources per subscriber. Default is 1', type=int, default=1, required=False)
parser.add_argument('-pcap_file','--pcap_file', help='if provided, the resulting pcap-file will be saved under provided name, default=ddos.pcap', default=outfile, required=False)
parser.add_argument('-oid','--oid', help='defines the snmp-oid , default 1.3.6.1', default='1.3.6.1', required=False)
parser.add_argument('-snmp_community','--snmp_community', help='defines the community to use, default public', default='public', required=False)


# vlans
parser.add_argument('-vid','--vid', help='omit this knob to generate untagged traffic. enter single VID for single-tagged traffic and enter komma-sperated (a,b) inner,outer (cVLAN,SVLAN) VID to generate double-tagged traffic', default='False', required=False)
parser.add_argument('-vid_increment','--vid_increment', help='for each subscriber increment the vlan-id by the configured value. default is 1', type=int,default=1, required=False)
parser.add_argument('-dot1q_prio','--dot1q_prio', help='sets the 802.1p priority for single and double-tagged frames. Default =0 ', type=int, default=0, required=False)

parser.add_argument('-wire','--wire', help='defines the default output interface to send the packets, e.g. eth0 or p6p2. default null' , default='null', required=False)

# enabling the traffic patterns
parser.add_argument('-pattern_bfd','--pattern_bfd','--bfd','-bfd', default=False, action="store_true" , help="uses same ports as BFD, but is not a real bfd-packet. bfd single and multihop are addressed")
parser.add_argument('-pattern_icmp_request','--pattern_icmp_request','--icmp_request','-icmp_request', default=False, action="store_true" , help="enables icmp echo-requests to configured destination")
parser.add_argument('-pattern_bgp','--pattern_bgp','--bgp','-bgp', default=False, action="store_true" , help="set --pattern_bgp to enable bgp traffic generation")
parser.add_argument('-pattern_dhcp_solicit','--pattern_dhcp_solicit','--dhcp_solicit', default=False, action="store_true" , help="set --dhcp-solicit to enable dhcp-solicit messages as seen from subscriber to R1")
parser.add_argument('-pattern_ra','--pattern_ra','--ra','-ra', default=False, action="store_true" , help="set --RA to enable router advertisements")
parser.add_argument('-pattern_stp_conf','--pattern_stp_conf','--stp_conf','-stp_conf', default=False, action="store_true" , help="set --pattern_stp_conf  to enable spanning tree conf attack")
parser.add_argument('-pattern_stp_tcn','--pattern_stp_tcn','--stp_tcn','-stp_tcn', default=False, action="store_true" , help="set --pattern_stp_tcn to enable spanning tree tcn attack")
parser.add_argument('-pattern_lacp','--pattern_lacp','--lacp','-lacp', default=False, action="store_true" , help="set --pattern_lacp to enable generation of lacp packets")
parser.add_argument('-pattern_snmp','--pattern_snmp','--snmp','-snmp', default=False, action="store_true" , help="set --pattern_snmp to enable generation of snmp-queries")

# router-advertisements
parser.add_argument('-RA_prefix','--RA_prefix', help='defines the to be advetised RA prefix, default 2a00:c37:428:22ff::', default='2a00:c37:428:22ff::', required=False)
parser.add_argument('-RA_prefix_len','--RA_prefix_len', help='defines the to be advetised RA prefix length, default /64', type=int,default='64', required=False)
parser.add_argument('-llc','--link_local_src', help='defines the sc link-local address, default fe80::2200:ff:fe00:1', default='fe80::2200:ff:fe00:1', required=False)

# all-knob
parser.add_argument('--all','-all', default=False, action="store_true" , help="set this knob to turn on all available tests (bfd,bgp,icmp,..)")

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
    args.pattern_bfd                  = True
    args.pattern_icmp_request         = True
    args.pattern_bgp                  = True
    args.pattern_dhcp_solicit         = True
    args.pattern_ra                   = True
    args.pattern_stp_conf             = True
    args.pattern_stp_tcn              = True
    args.pattern_lacp		      = True
    args.pattern_snmp		      = True

offset = str(args.offset)
ip_increment= (args.subs-1) * int(offset,16)
end_ip=IPAddress(args.sip)
end_ip = end_ip + ip_increment

ra_pio_increment = 0x10000000000000000

print "."
# print used values
print "used values"
print "==========="
print "dest mac               :", args.dmac
print "src mac                :", args.smac
print "dest. ip               :", args.dip
print "src ip - start         :", args.sip
print "src ip - end           :", end_ip
print "amount customers       :", args.subs
print "sources_per_subscriber :",args.sources_per_subscriber
print "pcap-file              :", args.pcap_file
print "vlan-id                :", args.vid
print "802.1p                 :", args.dot1q_prio
print "src link-local adr     :", args.link_local_src
print "RA prefix              :", args.RA_prefix
print "RA prefix len          :", args.RA_prefix_len

print "."

print "enabled protocols"
print "================="
if args.pattern_bfd == True:
   print "BFD"
if args.pattern_bgp == True:
   print "BGP"
if args.pattern_dhcp_solicit == True:
   print "dhcp solicit"
if args.pattern_icmp_request == True:
   print "icmp request"
if args.pattern_ra == True:
   print "Router Advertisements"
if args.pattern_stp_tcn == True:
   print "spanning-tree tcn"
if args.pattern_stp_conf == True:
   print "spanning-tree conf"
if args.pattern_lacp == True:
   print "lacp"
if args.pattern_snmp== True:
   print "snmp"

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
change_again='false'
for x in range(0,args.subs):

   # Variables
   ###########
   
   # mac addresses
   # multicast mac destination required for e.g. dhcpv6 solicit
   multicast_MAC     = '33:33:00:01:00:02'
   ra_dst_mac        = '33:33:00:00:00:01'
   bpdu_mac          = "01:80:c2:00:00:00"
   pause_mac         = "01:80:c2:00:00:01"
   lag_mac           = "01:80:c2:00:00:02"

   # ip setting
   # modifier and variance is defined here
   dhcp_dst_IPv6    = "ff02::1:2"
   ra_dst_IPv6      = "ff02::1"

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
           # incrementing the advertised RA-prefix with /64 per each src_per-subscriber run
           ra_pio_add=y*int(ra_pio_increment)
           ra_pio=IPAddress(args.RA_prefix)
           ra_pio= ra_pio + ra_pio_add	
	  
           # l3 src address gets incremented with each outer and inner loop
	   ip_increment= x * int(offset,16) + y
	   src_ip=IPAddress(args.sip)
	   src_ip = src_ip + ip_increment
	   l3=IPv6(src=str(src_ip),dst=args.dip)
	   l3_ra=IPv6(src=args.link_local_src,dst=ra_dst_IPv6)
           
	   # l2 header
	   ## check if packets shall be untagged, single-tagged or double-tagged
	   ## with each subscriber (args.subs) the vlan-id is incremented

           # setting the smac
   	   # each packet generated will either have a random src-mac, or will have a static src
      	   if (args.smac == 'random') :
              src_mac   = str(RandMAC())
              print "new mac choosen ", src_mac
           else:
               # make sure the static mac is only incremented with each subscriber and not with each source per subscriber
               # first create integer out of the mac-address
               mac   = EUI(args.smac) # EUI('22-22-33-33-44-45')
               int_mac = int(mac) +x  # now an integer: 37530283230278
	       src_mac_eui   = EUI(int_mac) # again EUi format: EUI('22-22-33-33-44-46')
               src_mac_eui.dialect = mac_unix_expanded # EUI('22:22:33:33:44:46')
               src_mac=str(src_mac_eui)

	   if args.vid <> 'False':
	       # packets are either tagged or double-tagged
	       help=args.vid.split(",")
	       # single tagged
	       if len(help) == 1:
		   # make sure with each run the svlan gets incremented
		   svlan=int(help[0])+x*args.vid_increment
		   print "single tagged"
		   l2=Ether(src=src_mac, dst=args.dmac)/Dot1Q(vlan=svlan,prio=args.dot1q_prio)
		   l2_ra=Ether(src=src_mac, dst=ra_dst_mac)/Dot1Q(vlan=svlan,prio=args.dot1q_prio)
		   l2_mcast=Ether(src=src_mac, dst=multicast_MAC)/Dot1Q(vlan=svlan,prio=args.dot1q_prio)
		   l2.show()

	       if len(help) == 2:
		   # make sure with each run the svlan gets incremented
		   svlan=int(help[0])+x*args.vid_increment
		   cvlan=int(help[1])
		   print "double tagged"
		   l2=Ether(src=src_mac, dst=args.dmac)/Dot1Q(vlan=svlan,prio=args.dot1q_prio)/Dot1Q(vlan=cvlan,prio=args.dot1q_prio)
		   l2_ra=Ether(src=src_mac, dst=ra_dst_mac)/Dot1Q(vlan=svlan,prio=args.dot1q_prio)/Dot1Q(vlan=cvlan,prio=args.dot1q_prio)
		   l2_mcast=Ether(src=src_mac, dst=multicast_MAC)/Dot1Q(vlan=svlan,prio=args.dot1q_prio)/Dot1Q(vlan=cvlan,prio=args.dot1q_prio)
	   else:
	       # args.vid is default False, hence untagged
	       # print "packet is untagged"
	       l2=Ether(src=src_mac, dst=args.dmac, type=0x86dd)
	       l2_ra=Ether(src=src_mac, dst=ra_dst_mac, type=0x86dd)
	       l2_mcast=Ether(src=src_mac, dst=multicast_MAC, type=0x86dd)


	   ##############################################
	   #####     add your traffic pattern here  #####
	   ##############################################
	   # bgp
	   # for bgp two different flavors are beeing launched
	   # first a single source is generating multiple sockets to same target
	   # second multiple sources are firing against same target

	   if args.pattern_bgp == True:
	       if x == 0:
		   print "starting: bgp traffic generation "
	       # launching multiple sockets from same src-IP
	       packet=l2/l3/TCP(sport=src_port_variance,dport=179)/BGPOpen()
	       packet_count += 1
	       pktdump.write(packet)
               if (args.wire!='null'):
	          sendp(packet,iface=args.wire)
	   # dhcp solicit
	   if args.pattern_dhcp_solicit == True:
	       if x == 0:
		   print "starting: dhcp-solicit generation "
	       sol = DHCP6_Solicit()
	       iana = DHCP6OptIA_NA()
	       rc = DHCP6OptRapidCommit()
	       et= DHCP6OptElapsedTime()
	       cid = DHCP6OptClientId()
	       opreq = DHCP6OptOptReq()
	       packet = l2_mcast/IPv6(src=str(src_ip),dst=dhcp_dst_IPv6)/UDP(sport=dhcp_sport,dport=dhcp_dport)/sol/iana/rc/et/cid/opreq
	       packet_count += 1
	       pktdump.write(packet)
               if (args.wire!='null'):
	          sendp(packet,iface=args.wire)

	   # icmp_request
	   if args.pattern_icmp_request == True:
	       if x == 0:
		   print "starting: icmp echo-request"
	       packet=l2/l3/ICMPv6EchoRequest()
	       packet_count += 1
	       pktdump.write(packet)
               if (args.wire!='null'):
	          sendp(packet,iface=args.wire)

	   # bfd
	   # note: its not a real bfd-packet, its just using the port-range for bfd
	   if args.pattern_bfd == True:
	       if x == 0:
		   print "starting: BFD"
	       # generating bfd_control packets
	       packet=l2/l3/UDP(sport=bfd_srcport, dport=bfd_control)
	       packet_count += 1
	       pktdump.write(packet)
               if (args.wire!='null'):
	          sendp(packet,iface=args.wire)
	       # bfd_multihup
	       packet=l2/l3/UDP(sport=bfd_srcport, dport=bfd_multihop)
	       packet_count += 1
	       pktdump.write(packet)
               if (args.wire!='null'):
	          sendp(packet,iface=args.wire)
	       # bfd echo
	       packet=l2/l3/UDP(sport=bfd_srcport, dport=bfd_echo)
	       packet_count += 1
	       pktdump.write(packet)
               if (args.wire!='null'):
	          sendp(packet,iface=args.wire)
           # router advertisements
           if args.pattern_ra == True:
               if x == 0:
                   print "starting: Router-Advertisements"
               packet=l2_ra/l3_ra/ICMPv6ND_RA(O=1,prf=3,routerlifetime=30)/ICMPv6NDOptSrcLLAddr(lladdr=src_mac)/ICMPv6NDOptMTU(mtu=1420)/ICMPv6NDOptPrefixInfo(prefixlen=args.RA_prefix_len,prefix=str(ra_pio))
               #packet.display() 
               packet_count += 1
               pktdump.write(packet)
               if (args.wire!='null'):
	          sendp(packet,iface=args.wire)
               #packet.show()
           # spanning-tree conf
           if args.pattern_stp_conf == True:
               if x == 0:
                   print "starting: spanning tree conf"
               root_priority = RandInt() % 65536
	       bridge_priority = RandInt() % 65536
	       packet=Dot3(dst=bpdu_mac, src=src_mac)/LLC()/STP(bpdutype=0x00, bpduflags=0x01, portid=0x8002, rootmac=src_mac,bridgemac=src_mac, rootid=root_priority, bridgeid=bridge_priority) 
               packet_count += 1
               pktdump.write(packet)
               if (args.wire!='null'):
	          sendp(packet,iface=args.wire)

           # spanning-tree tcn
           if args.pattern_stp_tcn == True:
               if x == 0:
                   print "starting: spanning tree tcn"
               root_priority = RandInt() % 65536
	       bridge_priority = RandInt() % 65536
	       packet=Dot3(dst=bpdu_mac, src=src_mac)/LLC()/STP(bpdutype=0x80)
               packet_count += 1
               pktdump.write(packet)
               if (args.wire!='null'):
	          sendp(packet,iface=args.wire)
           # lacp
           if args.pattern_lacp == True:
               if x == 0:
                   print "starting: lacp"
	       rd=rdpcap("only_lacp.pcap")
               lacp=rd[0].load
               packet=Ether(src=src_mac,dst=args.dmac,type=0x8809)/lacp
               packet_count += 1
               pktdump.write(packet)
               if (args.wire!='null'):
	          sendp(packet,iface=args.wire)
	   # snmp
           if args.pattern_snmp == True:
	       if x == 0:
		   print "starting: snmp-queries"
	       # launching multiple sockets from same src-IP
	       packet=l2/l3/UDP(sport=src_port_variance,dport=161)/SNMP(community=args.snmp_community,PDU=SNMPget(varbindlist=[SNMPvarbind(oid=ASN1_OID(args.oid))]))
	       packet_count += 1
	       pktdump.write(packet)
               if (args.wire!='null'):
	          sendp(packet,iface=args.wire)

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



