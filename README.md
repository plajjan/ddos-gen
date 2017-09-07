# DDoS-Gen - a simple DDoS traffic generator

ddos-gen is meant to be used in a CI system to generate IPv6 DDoS traffic to
exercise the control plane protection features of a router.


The tool allows to create untagged, single-tagged and double-tagged non-stateful packets to target the DUT.

# actually supported traffic patterns

```
lab@ubuntu1:~/cg-ubuntu1/ddos$ ./ddos-gen.py -h | grep pattern
```

* [-pattern_bfd]
* [-pattern_icmp_request]
* [-pattern_bgp]
* [-pattern_dhcp_solicit]
* [-pattern_ra]
* [-pattern_stp_conf]
* [-pattern_stp_tcn]
* [-pattern_lacp]
* [-pattern_snmp]

                   

# two parameters of success
The tool is having predefined/default values for the IPv6 destination IP and dest MAC.
To target a device, a user shall manually define both values to match the DUT.
The knobs -dmac (destination mac) and -dip (destination ip) are shown in below example

```
# example for enabling all traffic patterns
sudo ./ddos-gen.py --all  -subs 1 -sps 1   -RA_prefix 2a00:c37:428:22ff:: -RA_prefix_len 64 -llc fe80::2200:ff:fe00:1 -smac a0:36:9f:58:41:7a -dmac 4c:96:14:e5:b6:01 -dip 2003:1a39:47:2::2  -sip 2003:1a39:47:2::100 -vid 2000 --wire p9p3
```

## usage
A brief overview is provided by the '-h' knob
```
./ddos-gen.py -h
```


## knob subscribers versus sources-per-subscriber

While most parameters are self-explaining, the '-subs' (Amount of subscribers) and the 'sps' (sources per subscriber) knob need some explanation.

* To a subscriber there is always a subnet assigned, the start-point is '-sip'.
* If there are multiple subscribers configured, then all use an incremented subnet-range. The increment between the subnets can be influenced by the --offset knob.
* for each given subnet/subscriber we may have multiple src-addresses to launch for DDOS. This is defined via the '-sps' knob

### example knobs '-subs' / '-sps'

lets assume 3 subscribers with each 2 sources. protocol shall be bgp.

```
sudo ./ddos-gen.py --pattern_bgp -subs 3 -sps 2  --wire p9p3 --offset 0x10000000 -sip 2003::1

lab@ubuntu1:~$ sudo tcpdump -n -i p9p3 port 179
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on p9p3, link-type EN10MB (Ethernet), capture size 262144 bytes
10:32:21.726779 IP6 2003::1.1024 > 2001:db8:100::1.179: Flags [S], seq 0:10, win 8192, length 10: BGP
10:32:21.803173 IP6 2003::2.1024 > 2001:db8:100::1.179: Flags [S], seq 0:10, win 8192, length 10: BGP
10:32:21.879501 IP6 2003::1000:1.1025 > 2001:db8:100::1.179: Flags [S], seq 0:10, win 8192, length 10: BGP
10:32:21.950678 IP6 2003::1000:2.1025 > 2001:db8:100::1.179: Flags [S], seq 0:10, win 8192, length 10: BGP
10:32:22.027186 IP6 2003::2000:1.1026 > 2001:db8:100::1.179: Flags [S], seq 0:10, win 8192, length 10: BGP
10:32:22.095452 IP6 2003::2000:2.1026 > 2001:db8:100::1.179: Flags [S], seq 0:10, win 8192, length 10: BGP
```

### the used src-address in relevance to '-subs' / 'sps'
The used src-mac address can be either static configured or randomly choosen.

Default is random in the below fashion, but can be user-defined via the knob '-smac':

```
lab@ubuntu1:~/cg-ubuntu1/ddos$ ./ddos-gen.py -subs 3 -pattern_bgp -pattern_stp -sps 2 -smac 11:22:33:44:55:66
```

Running the tool with BGP and STP pattern. 3 subscribers and per subscriber 2 sources active.
makes in total 12 packets 

Please notice how the src-mac is getting randomly modified with each source-per-subscriber below.

```
12 = (3*2*(BGP+STP)=3*2*2
lab@ubuntu1:~/cg-ubuntu1/ddos$ ./ddos-gen.py -subs 3 -pattern_bgp -pattern_stp -sps 2

lab@ubuntu1:~/cg-ubuntu1/ddos$ tcpdump -ne -r ddos.pcap
reading from file ddos.pcap, link-type EN10MB (Ethernet)
12:07:43.320222 1c:11:40:b8:de:69 > 22:22:22:22:22:22, ethertype IPv6 (0x86dd), length 84: 2003:1c08:20:ff::1.1024 > 2001:db8:100::1.179: Flags [S], seq 0:10, win 8192, length 10: BGP
12:07:43.322237 1c:11:40:b8:de:69 > 01:80:c2:00:00:00, 802.3, length 38: LLC, dsap STP (0x42) Individual, ssap STP (0x42) Command, ctrl 0x03: STP 802.1d, Config, Flags [Topology change], bridge-id 1194.1c:11:40:b8:de:69.8002, length 35
12:07:43.324093 e7:c9:6c:e6:e5:91 > 22:22:22:22:22:22, ethertype IPv6 (0x86dd), length 84: 2003:1c08:20:ff::2.1024 > 2001:db8:100::1.179: Flags [S], seq 0:10, win 8192, length 10: BGP
12:07:43.325792 e7:c9:6c:e6:e5:91 > 01:80:c2:00:00:00, 802.3, length 38: LLC, dsap STP (0x42) Individual, ssap STP (0x42) Command, ctrl 0x03: STP 802.1d, Config, Flags [Topology change], bridge-id 25f6.e7:c9:6c:e6:e5:91.8002, length 35
12:07:43.327589 38:c5:41:7e:da:c9 > 22:22:22:22:22:22, ethertype IPv6 (0x86dd), length 84: 2003:1c08:20:ff::1.1025 > 2001:db8:100::1.179: Flags [S], seq 0:10, win 8192, length 10: BGP
12:07:43.329189 38:c5:41:7e:da:c9 > 01:80:c2:00:00:00, 802.3, length 38: LLC, dsap STP (0x42) Individual, ssap STP (0x42) Command, ctrl 0x03: STP 802.1d, Config, Flags [Topology change], bridge-id 98d8.38:c5:41:7e:da:c9.8002, length 35
12:07:43.330965 e3:d7:42:1f:01:f4 > 22:22:22:22:22:22, ethertype IPv6 (0x86dd), length 84: 2003:1c08:20:ff::2.1025 > 2001:db8:100::1.179: Flags [S], seq 0:10, win 8192, length 10: BGP
12:07:43.332698 e3:d7:42:1f:01:f4 > 01:80:c2:00:00:00, 802.3, length 38: LLC, dsap STP (0x42) Individual, ssap STP (0x42) Command, ctrl 0x03: STP 802.1d, Config, Flags [Topology change], bridge-id cfd2.e3:d7:42:1f:01:f4.8002, length 35
12:07:43.334457 d7:a2:8d:3f:7a:9d > 22:22:22:22:22:22, ethertype IPv6 (0x86dd), length 84: 2003:1c08:20:ff::1.1026 > 2001:db8:100::1.179: Flags [S], seq 0:10, win 8192, length 10: BGP
12:07:43.336015 d7:a2:8d:3f:7a:9d > 01:80:c2:00:00:00, 802.3, length 38: LLC, dsap STP (0x42) Individual, ssap STP (0x42) Command, ctrl 0x03: STP 802.1d, Config, Flags [Topology change], bridge-id f2b9.d7:a2:8d:3f:7a:9d.8002, length 35
12:07:43.337785 df:d2:26:92:91:5d > 22:22:22:22:22:22, ethertype IPv6 (0x86dd), length 84: 2003:1c08:20:ff::2.1026 > 2001:db8:100::1.179: Flags [S], seq 0:10, win 8192, length 10: BGP
12:07:43.339214 df:d2:26:92:91:5d > 01:80:c2:00:00:00, 802.3, length 38: LLC, dsap STP (0x42) Individual, ssap STP (0x42) Command, ctrl 0x03: STP 802.1d, Config, Flags [Topology change], bridge-id 31d6.df:d2:26:92:91:5d.8002, length 35
```


### vlan-tagging and the relevance to '-subs' / 'sps'

With vlan-tagging the 'subs' and 'sps' knobs become more meaningful.
using same example as above, however adding vlan-id 2000 

adding knob -e in tcpdump to display the mac-layer

As seen in below tcpdump, each subnet/subscriber uses a seperate vlan (increment of 1) with again in each sunet having 2 sources (-sps 2) active

Note: if all traffic shall be sent within a single vlan only, then two options exists:

* use -subs 1 and -sps 1000 setting
* use any subs and any sps setting, but have the vid_increment 0 setting


```
sudo ./ddos-gen.py --pattern_bgp -subs 3 -sps 2  --wire p9p3 --offset 0x10000000 -sip 2003::1 -vid 2000

lab@ubuntu1:~$ sudo tcpdump -n -i p9p3 -e
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on p9p3, link-type EN10MB (Ethernet), capture size 262144 bytes
10:51:04.549637 a0:36:9f:58:41:7a > 01:80:c2:00:00:00, 802.3, length 38: LLC, dsap STP (0x42) Individual, ssap STP (0x42) Command, ctrl 0x03: STP 802.1d, Config, Flags [none], bridge-id 8000.a0:36:9f:58:41:7a.8002, length 35
10:51:05.946628 23:22:22:22:22:22 > 22:22:22:22:22:22, ethertype 802.1Q (0x8100), length 88: vlan 2000, p 0, ethertype IPv6, 2003::1.1024 > 2001:db8:100::1.179: Flags [S], seq 0:10, win 8192, length 10: BGP
10:51:06.026594 23:22:22:22:22:22 > 22:22:22:22:22:22, ethertype 802.1Q (0x8100), length 88: vlan 2000, p 0, ethertype IPv6, 2003::2.1024 > 2001:db8:100::1.179: Flags [S], seq 0:10, win 8192, length 10: BGP
10:51:06.110769 23:22:22:22:22:22 > 22:22:22:22:22:22, ethertype 802.1Q (0x8100), length 88: vlan 2001, p 0, ethertype IPv6, 2003::1000:1.1025 > 2001:db8:100::1.179: Flags [S], seq 0:10, win 8192, length 10: BGP
10:51:06.195208 23:22:22:22:22:22 > 22:22:22:22:22:22, ethertype 802.1Q (0x8100), length 88: vlan 2001, p 0, ethertype IPv6, 2003::1000:2.1025 > 2001:db8:100::1.179: Flags [S], seq 0:10, win 8192, length 10: BGP
10:51:06.278624 23:22:22:22:22:22 > 22:22:22:22:22:22, ethertype 802.1Q (0x8100), length 88: vlan 2002, p 0, ethertype IPv6, 2003::2000:1.1026 > 2001:db8:100::1.179: Flags [S], seq 0:10, win 8192, length 10: BGP
10:51:06.347531 23:22:22:22:22:22 > 22:22:22:22:22:22, ethertype 802.1Q (0x8100), length 88: vlan 2002, p 0, ethertype IPv6, 2003::2000:2.1026 > 2001:db8:100::1.179: Flags [S], seq 0:10, win 8192, length 10: BGP
10:51:06.549633 a0:36:9f:58:41:7a > 01:80:c2:00:00:00, 802.3, length 38: LLC, dsap STP (0x42) Individual, ssap STP (0x42) Command, ctrl 0x03: STP 802.1d, Config, Flags [none], bridge-id 8000.a0:36:9f:58:41:7a.8002, length 35
``` 

## doube-tagged frames and an example for dot1q priority setting

Double-tagged frames can be sent via comma-separated vlan-ids with the "-vid" knob.

* Increment between outer-vlan id (svlan) is set to 10
* svlan starts with 2001
* cvlan stays constant at 100
* dot1p priority is set to dec 4 (bin 100)

```
lab@ubuntu1:~/cg-ubuntu1/ddos$ sudo ./ddos-gen.py --pattern_bgp -subs 3 -sps 2  --wire p9p3 --offset 0x10000000 -sip 2003::1 -vid 2001,100 -vid_increment 10

11:25:56.127414 23:22:22:22:22:22 > 22:22:22:22:22:22, ethertype 802.1Q (0x8100), length 92: vlan 2001, p 4, ethertype 802.1Q, vlan 100, p 4, ethertype IPv6, 2003::1.1024 > 2001:db8:100::1.179: Flags [S], seq 0:10, win 8192, length 10: BGP
11:25:56.215223 23:22:22:22:22:22 > 22:22:22:22:22:22, ethertype 802.1Q (0x8100), length 92: vlan 2001, p 4, ethertype 802.1Q, vlan 100, p 4, ethertype IPv6, 2003::2.1024 > 2001:db8:100::1.179: Flags [S], seq 0:10, win 8192, length 10: BGP
11:25:56.291078 23:22:22:22:22:22 > 22:22:22:22:22:22, ethertype 802.1Q (0x8100), length 92: vlan 2011, p 4, ethertype 802.1Q, vlan 100, p 4, ethertype IPv6, 2003::1000:1.1025 > 2001:db8:100::1.179: Flags [S], seq 0:10, win 8192, length 10: BGP
11:25:56.370824 23:22:22:22:22:22 > 22:22:22:22:22:22, ethertype 802.1Q (0x8100), length 92: vlan 2011, p 4, ethertype 802.1Q, vlan 100, p 4, ethertype IPv6, 2003::1000:2.1025 > 2001:db8:100::1.179: Flags [S], seq 0:10, win 8192, length 10: BGP
11:25:56.451858 23:22:22:22:22:22 > 22:22:22:22:22:22, ethertype 802.1Q (0x8100), length 92: vlan 2021, p 4, ethertype 802.1Q, vlan 100, p 4, ethertype IPv6, 2003::2000:1.1026 > 2001:db8:100::1.179: Flags [S], seq 0:10, win 8192, length 10: BGP
11:25:56.527329 23:22:22:22:22:22 > 22:22:22:22:22:22, ethertype 802.1Q (0x8100), length 92: vlan 2021, p 4, ethertype 802.1Q, vlan 100, p 4, ethertype IPv6, 2003::2000:2.1026 > 2001:db8:100::1.179: Flags [S], seq 0:10, win 8192, length 10: BGP

```

### Router advertisements
When generating RA messages, the following parms can be user defined:

* the prefix to advertise (pio)
* prefix len (e.g /64)
* used src link-local address

example

```
lab@ubuntu1:~/cg-ubuntu1/ddos$ sudo ./ddos-gen.py --pattern_RA -subs 1 -sps 1  --wire p9p3 -RA_prefix 2a00:c37:428:22ff:: -RA_prefix_len 64 -llc fe80::2200:ff:fe00:1 -smac 23:22:22:22:22:22

lab@ubuntu1:~$ sudo tcpdump -n -i p9p3 -e -vvv
tcpdump: listening on p9p3, link-type EN10MB (Ethernet), capture size 262144 bytes

11:46:30.606884 23:22:22:22:22:22 > 33:33:00:00:00:01, ethertype IPv6 (0x86dd), length 118: (hlim 255, next-header ICMPv6 (58) payload length: 64) fe80::2200:ff:fe00:1 > ff02::1: [icmp6 sum ok] ICMP6, router advertisement, length 64
	hop limit 0, Flags [other stateful], pref low, router lifetime 30s, reachable time 0s, retrans time 0s
	  source link-address option (1), length 8 (1): 23:22:22:22:22:22
	    0x0000:  2322 2222 2222
	  mtu option (5), length 8 (1):  1420
	    0x0000:  0000 0000 058c
	  prefix info option (3), length 32 (4): 2a00:c37:428:22ff::/64, Flags [onlink, auto], valid time infinity, pref. time infinity
	    0x0000:  40c0 ffff ffff ffff ffff 0000 0000 2a00
	    0x0010:  0c37 0428 22ff 0000 0000 0000 0000
```
	
###snmpget
The tools allows to generate snmpqueries via a user-configurable OID. Default is "1.3.6.1"
Default value for the community is public, but can be overwritten.

```
lab@ubuntu1:~/cg-ubuntu1/ddos$ ./ddos-gen.py --pattern_snmp -oid 1.3.6.1.2 -snmp_community test

lab@ubuntu1:~/cg-ubuntu1/ddos$ tcpdump -ne -c 2 -r ddos.pcap -vvv
reading from file ddos.pcap, link-type EN10MB (Ethernet)
16:31:53.219300 d1:23:5b:0e:b5:71 > 22:22:22:22:22:22, ethertype IPv6 (0x86dd), length 96: (hlim 64, next-header UDP (17) payload length: 42) 2003:1c08:20:ff::1.1024 > 2001:db8:100::1.161: [udp sum ok]  { SNMPv2c C="test" { GetRequest(21) R=0  .1.3.6.1.2 } }

```

### spanning tree
For STP 2 options do exist.

* The 'stp_tcn' is just a topology-change notification (packet=Dot3(dst=bpdu_mac, src=src_mac)/LLC()/STP(bpdutype=0x80))
* The stp_conf fires up configuration BPDU's, with random root_priority and random bridge_priority (packet=Dot3(dst=bpdu_mac, src=src_mac)/LLC()/STP(bpdutype=0x00, bpduflags=0x01, portid=0x8002, rootmac=src_mac,bridgemac=src_mac, rootid=root_priority, bridgeid=bridge_priority))


```
lab@ubuntu1:~/cg-ubuntu1/ddos$ ./ddos-gen.py --pattern_stp_tcn
lab@ubuntu1:~/cg-ubuntu1/ddos$ tcpdump -ne -c 2 -r ddos.pcap -vvv
reading from file ddos.pcap, link-type EN10MB (Ethernet)
16:33:49.802864 f3:0f:59:f4:95:3f > 01:80:c2:00:00:00, 802.3, length 38: LLC, dsap STP (0x42) Individual, ssap STP (0x42) Command, ctrl 0x03: STP 802.1d, Topology Change

lab@ubuntu1:~/cg-ubuntu1/ddos$ ./ddos-gen.py --pattern_stp_conf
lab@ubuntu1:~/cg-ubuntu1/ddos$ tcpdump -ne -c 2 -r ddos.pcap -vvv
reading from file ddos.pcap, link-type EN10MB (Ethernet)
16:34:32.975872 47:42:96:ac:17:bf > 01:80:c2:00:00:00, 802.3, length 38: LLC, dsap STP (0x42) Individual, ssap STP (0x42) Command, ctrl 0x03: STP 802.1d, Config, Flags [Topology change], bridge-id 44a0.47:42:96:ac:17:bf.8002, length 35
	message-age 1.00s, max-age 20.00s, hello-time 2.00s, forwarding-delay 15.00s
	root-id f623.47:42:96:ac:17:bf, root-pathcost 0
```

### LACP
Scapy does not natively support SNMP. The tool is reading a LACP-packet taken from a EX4300 series switch (provided via pcap "only_lacp.pcap") and overwrites src_mac and dst_mac of the to be generated LACP-frames.

```
lab@ubuntu1:~/cg-ubuntu1/ddos$ ./ddos-gen.py --pattern_lacp -dmac 22:22:22:00:00:00

lab@ubuntu1:~/cg-ubuntu1/ddos$ tcpdump -ne -c 2 -r ddos.pcap -vvv
reading from file ddos.pcap, link-type EN10MB (Ethernet)
16:42:50.313046 8b:42:f6:f3:28:fc > 22:22:22:00:00:00, ethertype Slow Protocols (0x8809), length 124: LACPv1, length 110
	Actor Information TLV (0x01), length 20
	  System 4c:96:14:e5:b6:00, System Priority 127, Key 1, Port 1, Port Priority 127
	  State Flags [Activity, Timeout, Aggregation, Default, Expired]
	  0x0000:  007f 4c96 14e5 b600 0001 007f 0001 c700
	  0x0010:  0000
	Partner Information TLV (0x02), length 20
	  System 00:00:00:00:00:00, System Priority 1, Key 1, Port 1, Port Priority 1
	  State Flags [Timeout, Aggregation, Default]
	  0x0000:  0001 0000 0000 0000 0001 0001 0001 4600
	  0x0010:  0000
	Collector Information TLV (0x03), length 16
	  Max Delay 0
	  0x0000:  0000 0000 0000 0000 0000 0000 0000
	Terminator TLV (0x00), length 0

```


### wire or pcap

the tool always generates a pcap-file which can then be fire-up via tcpreplay for example. The default name is "ddos.pcap", however can be user-defined by the "-pcap_file" knob.

optional an interface can be given as seen in above example to send the packets directly to a named interface (e.g. /dev/p9p3)


