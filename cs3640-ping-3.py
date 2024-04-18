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


def main():
    # Gets user input from the command line, setting them equal to destination, n, and ttl
    parser = argparse.ArgumentParser(description="Ping")
    parser.add_argument('-destination', required=True, help="Destination IP address")
    parser.add_argument('-n', type=int, required=True, help="Number of packets to send")
    parser.add_argument('-ttl', type=int, required=True, help="Time to Live")
    args = parser.parse_args()
    destination = args.destination
    n = args.n
    ttl = args.ttl

    # Adder and Counter for AVERAGE_RTT
    SUM_ADD = 0
    counter = 0

    # Loops through the seq to the range n to send echoes and recieve response time.
    for seq in range(n):
        icmp_socket = make_icmp_socket(ttl, timeout=3.5)
        id = seq
        start_time = time.time()
        send_icmp_echo(icmp_socket, payload='Hey! Checkout this new Pizza Place!', id=id, seq=seq,
                       destination=destination)
        response_packet = recv_icmp_response()
        end_time = time.time()
        route_trip_around_Times = []
        if response_packet:
            # converting to milliseconds...
            trip_around_time = (start_time - end_time) * 1000
            route_trip_around_Times.append(trip_around_time)
            SUM_ADD = SUM_ADD + trip_around_time
            counter = counter + 1
            # the .1f on the rtt is used for decimal formation like 14.0 in the example output.
            print(
                f"destination = {destination}; icmp_seq = {seq}; icmp_id = {id}; ttl = {ttl}; rtt = {trip_around_time:.1f} ms")
        else:
            print(
                f"destination = {destination}; icmp_seq = {seq}; icmp_id = {id}; ttl = {ttl}; Can't calculate rtt since response was not recieved.")
    # calculates the average and also shows if the pings were successful.
    AVERAGE_RTT = SUM_ADD / n
    print(f"Average rtt: {AVERAGE_RTT:.1f} ms; {counter}/{n} successful pings.")


main()


