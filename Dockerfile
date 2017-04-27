FROM ubuntu

RUN add-apt-repository ppa:appneta/ppa \
 && apt-get -qy update \
 && apt-get -qy install \
    iproute2 \
    tcpdump \
    tcpreplay \
    python-netaddr \
    python-scapy 

RUN mkdir /usr/lib/python2.7/dist-packages/scapy/contrib \
 && touch /usr/lib/python2.7/dist-packages/scapy/contrib/__init__.py \
 && wget -O /usr/lib/python2.7/dist-packages/scapy/contrib/bgp.py https://raw.githubusercontent.com/levigross/Scapy/master/scapy/contrib/bgp.py

COPY ddos-gen.py /

ENTRYPOINT ["/ddos-gen.py"]
