# DDoS-Gen - a simple DDoS traffic generator

ddos-gen is meant to be used in a CI system to generate IPv6 DDoS traffic to
exercise the control plane protection features of a router.


The tool allows to create untagged, single-tagged and double-tagged non-stateful packets to target the DUT.
Various packet-patterns do exist, like bgp, bfd, icmp_request, Router-Advertisements,...


## usage
A brief overview is provided by the '-h' knob
```
./ddos-gen.py -h
```

While most parameters are self-explaining, the '-subs' (Amount of subscribers) and the 'sps' (sources per subscriber) knob need some explanation.

* To a subscriber there is always a subnet assigned, the start-point is '-sip'.
* If there are multiple subscribers configured, then all use an incremented subnet-range. The increment between the subnets can be influenced by the --offset knob.
* for each given subnet/subscriber we may have multiple src-addresses to launch for DDOS. This is defined via the '-sps' knob

### example 'subs' / 'sps'

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
	


### wire or pcap

the tool always generates a pcap-file which can then be fire-up via tcpreplay for example. The default name is "ddos.pcap", however can be user-defined by the "-pcap_file" knob.

optional an interface can be given as seen in above example to send the packets directly to a named interface (e.g. /dev/p9p3)


