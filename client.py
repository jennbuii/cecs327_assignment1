import json
import sys
from socket import AF_INET, SOCK_STREAM, socket

HOST = "127.0.0.1"

def pretty_print(response):
    if response.startswith("ERROR"):
        print(response)
        return
    listings = response.splitlines()[1:-1]
    print(f"{'ID':<5} | {'City':<15} | {'Address':<20} | {'Price':<10} | {'Bedrooms':<10}")
    print("-" * 71)
    for listing in listings:
        parts = listing.strip().split(";")
        id = parts[0].split("=")[1]
        city = parts[1].split("=")[1]
        address = parts[2].split("=")[1]
        price = parts[3].split("=")[1]
        bedrooms = parts[4].split("=")[1]
        print(f"{id:<5} | {city:<15} | {address:<20} | ${price:<10} | {bedrooms:<10}")

def main():
    if len(sys.argv) != 2:
        print("ERROR invalid command syntax: python client.py <app_port>\n")
        print("Example: python client.py 12345\n")
        sys.exit(1)
    app_port = int(sys.argv[1])
    s = socket(AF_INET, SOCK_STREAM)
    s.connect((HOST, app_port))
    while True:
        print("Menu:"
              "\n LIST: Display all listings"
              "\n SEARCH: Filter listings by city and max price"
              "\n QUIT: Exit the application\n")
        choice = input("Enter your choice: ").strip().upper()

        if choice =="LIST":
            s.send("LIST\n".encode("ascii"))
            response = s.recv(4096).decode("ascii")
            pretty_print(response)
        
        elif choice =="SEARCH":
            city = input("Enter city name: ").strip()
            max_price = input("Enter maximum price: ").strip()

            s.send(f"SEARCH city={city} max_price={max_price}\n".encode("ascii"))
            response = s.recv(4096).decode("ascii")
            pretty_print(response) 

        elif choice =="QUIT":
            s.send("QUIT\n".encode("ascii"))
            response = s.recv(4096).decode("ascii")
            print(response)
            break

        else:
            print("ERROR invalid command syntax\n")
    s.close()

if __name__ == "__main__":
    main()
        