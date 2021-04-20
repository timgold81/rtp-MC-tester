import signal
import argparse
import time
import socket
from random import randint
import threading
import struct
import binascii

def signal_handler(signal, frame):
    # if needed to stop some kind of main loop
    config.loop = 0
    config.operation_status=False
    print("\nStopping RTP tester. Thanks for using.")
    print("Please visit https://github.com/timgold81/")
    print("contact timgold@gmail.com\n")
    exit()

signal.signal(signal.SIGINT, signal_handler)


def myPause(sec):
    dev = 50  # devision - how many times in second to pause
    maximum = sec * dev
    i = 0
    while (config.loop and i < maximum):
        time.sleep(1 / dev)
        i = i + 1


class Config:
    loop = 1
    mode=""
    some_argument = ""
    operation_status=True
    dest_ip=""
    interface_ip=""
    port_nu=0
    max_packets=500
    thread=1
    amount=1
    port_increment=10

    def handle_args(self):
        parser = argparse.ArgumentParser(description="RTP Checker. The program \
            sends RTP traffic to an address and checks if got RTP")
        parser.add_argument("-s", "--sender", help="Acts as a sender, specify MC address to send to")
        parser.add_argument("-i","--interface_ip", help="IP of an interface to send or listen to MC traffic", required=True)
        parser.add_argument("-r", "--receiver", help="Acts as a MC receiver, specify address to listen")
        parser.add_argument("-p", "--port", help="Starting port address to use. Default 10000",type=int)
        parser.add_argument("-a", "--amount",help="How many port groups to use. Will increment by 10 the staring port a times. Default = 1" , type=int)
        parser.add_argument("-n", "--number_of_packets", help="How many packets to send. Default=500")
        # parser.add_argument("-n", "--number_of_packets", help="How many packets to send. Default=500")
        args = parser.parse_args()

        if args.receiver:
            config.mode="receiver"
            config.dest_ip=args.receiver

        if args.sender:
            config.mode="sender"
            config.dest_ip=args.sender

        if args.amount:
            config.amount=args.amount
            if config.amount < 0:
                print ("amount -a must be >= 1")
                exit(-1)

        if args.interface_ip:
            config.interface_ip=args.interface_ip

        if not args.sender and not args.receiver:
            print ("Must specify if sender or receiver with IP address")
            exit(-1)
        if args.sender and args.receiver:
            print ("Cannot be sender and receiver at the same time")
            exit(-1)


        if args.port:
            self.port_nu=args.port
        else:
            self.port_nu = 10000

        if args.number_of_packets:
            self.max_packets=args.number_of_packets
        else:
            self.max_packets = 500


class Packet:
    Coder="alaw"
    sequence_number = 0  # 16 bits
    timestamp = 0  # 32 bits
    SSRC = 0x0  # 32 bits
    CSRC = 0  # 0 to 15 items 32 bits each
    # payload = 0x00005a5a00005a5a00005a5a00005a5a00005a5a00005a5a00005a5a00005a5a00005a5a00005a5a00005a5a00005a5a00005a5a00005a5a00005a5a00005a5a00005a5a00005a5a00005a5a00005a5a00005a5a00005a5a00005a5a00005a5a00005a5a00005a5a00005a5a00005a5a00005a5a00005a5a
    # payload = 0xc030c030c030c030c030c030c030c030c030c030c030c030c030c030c030c030c030c030c030c030c030c030c030c030c030c030c030c030c030c030c030c030c030c030c030c030c030c030c030c030c030c030c030c030c030c030c030c030c030c030c030c030c030c030c030c030c030c030c030c030c030
    # payload = 0xb0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0303030303030303030303030303030303030303030303030303030303030303030303030303030303030
    payload = 0xb0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0303030303030303030303030303030303030303030303030303030303030303030303030303030303030


    def __init__(self):
        self.gen_ssrc()

    def get_payload(self):
        return self.payload


    def get_packet_hex(self):
        if self.Coder=="alaw":
            coder=0x8000
        else:
            coder=0x8008

        # output=f'{coder:x}{self.sequence_number:04x}{self.timestamp:08x}{self.SSRC:04x}{self.CSRC:04x}{self.payload:x}'
        # payload=f'{self.payload}'.format()
        output=f'{coder:x}{self.sequence_number:04x}{self.timestamp:08x}{self.SSRC:04x}{self.CSRC:04x}{self.payload:0{316}x}'

        return output

    def gen_ssrc(self):
        self.SSRC=randint(0,1073741824)

    def decode(self,data):
        pass


class sender_worker(threading.Thread):
    port_nu=10000;
    ip_addr = ""

    def __init__(self):
        threading.Thread.__init__(self)

    def __init__(self,p,ip):
        threading.Thread.__init__(self)
        self.port_nu=p
        self.ip_addr = ip

    def run(self):
        sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        ttl=struct.pack('b',24)
        sock.setsockopt(socket.IPPROTO_IP,socket.IP_MULTICAST_TTL,ttl)
        sock.setsockopt(socket.IPPROTO_IP,socket.IP_MULTICAST_IF,socket.inet_aton(config.interface_ip))
        sock.settimeout(0.2)
        p=Packet()
        packets_number_sent=0
        #need to send packet every 20 msec, 50 packets per second
        time_sep=0.02

        #for reporting every second
        report_max_packets=1/time_sep
        report_counter=1
        myPause(0.5)
        while config.operation_status:
            # if report==0:
            # print (f'Sending {self.ip_addr} to port {self.port_nu} the data {p.get_packet_hex()[32:]}')
            arrr=bytearray.fromhex(p.get_packet_hex())

            sock.sendto(arrr, (self.ip_addr,int(self.port_nu)))
            # sock.sendto(bytearray.fromhex(p.get_packet_hex()), ("239.0.0.1", 10000))
            if packets_number_sent>=int(config.max_packets):
                print(f"Port {self.port_nu} - break!")
                break
            time.sleep(time_sep)
            packets_number_sent=packets_number_sent+1

            # print report every second
            if report_counter==report_max_packets:
                print (f"Port {self.port_nu} sent {packets_number_sent} packets, max packets {config.max_packets}")
                report_counter=0
            report_counter=report_counter+1

            if config.operation_status==False:
                exit(-1)

            # need to increment timestamp and sequence number
            p.sequence_number=p.sequence_number+1
            p.timestamp=p.timestamp+160


class receiver_worker(threading.Thread):
    ip_addr = ""
    port_nu = 10000

    def __init__(self):
        threading.Thread.__init__(self)


    def __init__(self,p,ip):
        threading.Thread.__init__(self)
        self.port_nu = p
        self.ip_addr=ip

    def run(self):
        print(f"Opening socket on port {self.port_nu}")

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        sock.setsockopt(socket.SOL_IP,socket.IP_ADD_MEMBERSHIP, socket.inet_aton(self.ip_addr)+socket.inet_aton(config.interface_ip))
        sock.bind(('',int(self.port_nu)))
        data="None"
        addr="NONE"
        sock.settimeout(1)

        # For reporting
        number_of_packets=0
        report_every_x_packets=50
        report_max_packet_counter=1
        while config.operation_status:
            try:
                data, addr=sock.recvfrom(256)
            except socket.error:
                print(f"port {self.port_nu} socket.error - no traffic")
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP,
                                socket.inet_aton(self.ip_addr) + socket.inet_aton(config.interface_ip))
                sock.bind(('', int(self.port_nu)))
                data = "None"
                addr = "NONE"
                sock.settimeout(1)
                continue
            except socket.timeout:
                print("timeout!")
                config.operation_status == False
                exit(-1)
            str_data=binascii.hexlify(data[16:])
            # print(str_data)
            if "0b0b0b" in str(str_data) and "303030" in str(str_data):
                number_of_packets=number_of_packets+1
                if report_max_packet_counter==report_every_x_packets:
                    print (f"Port {self.port_nu} got {number_of_packets} packets")
                    report_max_packet_counter=0
                report_max_packet_counter=report_max_packet_counter+1

            # strr=binascii.hexlify(strr)
            # print (f"got from client:{binascii.hexlify(data[16:])} from {addr}")
            if config.operation_status==False:
                exit(-1)
            myPause(0.01)


def main():
    # print (config)
    if config.mode=="receiver":
        for i in range (0,config.amount):
            thread=receiver_worker(config.port_nu+(i*10),config.dest_ip)
            thread.start()
    elif config.mode=="sender":
        for i in range(0,config.amount):
            config.thread = sender_worker(config.port_nu+(i*10),config.dest_ip)
            config.thread.start()
    while True:
        myPause(1)



if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    global config
    config = Config()
    config.handle_args()
    main()
