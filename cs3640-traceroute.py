import argparse
import time
import dpkt
import socket


def make_icmp_socket(ttl, timeout):
    # Creates raw ICMP socket
    ICMP_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    # Sets the TTL and timeout.
    ICMP_socket.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
    ICMP_socket.settimeout(timeout)

    return ICMP_socket


def send_icmp_echo(socket, payload, id, seq, destination, port=0):
    # Create Echo request packet
    echo = dpkt.icmp.ICMP.Echo()

    # set icmp id and seq number
    echo.id = id
    echo.seq = seq

    # set payload
    echo.payload = bytes(payload, 'utf-8')

    icmp = dpkt.icmp.ICMP()
    icmp.type = dpkt.icmp.ICMP_ECHO
    icmp.data = echo

    # Pack the echo packet and send to the destination
    icmp.pack = icmp.pack()
    destination = (destination, port)
    socket.sendto(icmp.pack, destination)

    return


def recv_icmp_response():
    recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    while True:
        try:
            arrived, address = recv_socket.recvfrom(1024)
            break
        except socket.error as e:
            return e
    return arrived

#Traceroute Code starts here!
def traceroute(destination, n_hops):
    for ttl in range(1, n_hops + 1):
        icmp_socket = make_icmp_socket(ttl, timeout = 2)
        seq = 0

        #Send ICMP Echo packet
        start_time = time.time()
        send_icmp_echo(icmp_socket, payload='Hey, can I get an infinite amount of Pizzas?', id=1, seq=seq, destination=destination)

        #Receive the response ICMP Packet!
        response_recievedPacket = recv_icmp_response()
        end_time = time.time()
        icmp_socket.close()

        if response_recievedPacket:
            ip = dpkt.ip.IP(response_recievedPacket[20:])
            sending_ip = socket.inet_ntoa(ip.src)
            round_trip_time = (end_time - start_time) * 1000
            print(f"desination = {destination}; hop {ttl} = {sending_ip}; rtt = {round_trip_time:.2f} ms")
        else:
            print(f"destination = {destination}; hop {ttl} =*")

        if sending_ip == destination:
            break

def main():
    parser = argparse.ArgumentParser(description="Traceroute")
    parser.add_argument("-destination", required=True, help="Destination IP address")
    parser.add_argument("-n_hops", type=int, required=True, help="Number of hops needed")
    
    args = parser.parse_args()
    
    destination = args.destination
    n_hops = args.n_hops
    
    traceroute(destination, n_hops)
    return

main()

