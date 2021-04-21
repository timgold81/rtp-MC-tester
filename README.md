# rtp-MC-tester
Tests Multicast RTP traffic. As a client, will send RTP traffic to specified RTP address from specifically selected interface. As a server will listen to MC RTP traffic and tell if the traffic di arrive or not.
<pre>
python main.py -h
usage: main.py [-h] [-s SENDER] -i INTERFACE_IP [-r RECEIVER] [-p PORT] [-a AMOUNT] [-n NUMBER_OF_PACKETS]

RTP Checker. The program sends RTP traffic to an address and checks if got RTP

optional arguments:
  -h, --help            show this help message and exit
  -s SENDER, --sender SENDER
                        Acts as a sender, specify MC address to send to
  -i INTERFACE_IP, --interface_ip INTERFACE_IP
                        IP of an interface to send or listen to MC traffic
  -r RECEIVER, --receiver RECEIVER
                        Acts as a MC receiver, specify address to listen
  -p PORT, --port PORT  Starting port address to use. Default 10000
  -a AMOUNT, --amount AMOUNT
                        How many port groups to use. Will increment by 10 the staring port a times. Default = 1
  -n NUMBER_OF_PACKETS, --number_of_packets NUMBER_OF_PACKETS
                        How many packets to send. Default=500

</pre>
