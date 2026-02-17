import json
import sys
from socket import AF_INET, SOCK_STREAM, socket

HOST = "127.0.0.1"

def raw_list(listings):
    matches = []
    for listing in listings:
        matches.append(f"id={listing['id']};city={listing['city']};address={listing['address']};price={listing['price']};bedrooms={listing['bedrooms']}\n")
    response = [f"OK RESULT {len(matches)}\n"]
    response.extend(matches)
    response.append("END\n")
    return "".join(response)

def raw_search(cmd_line, listings):
    if "city" not in cmd_line or "max_price" not in cmd_line:   
        return "ERROR incorrect command arguments\n"
    if "city=" not in cmd_line or "max_price=" not in cmd_line:
        return "ERROR invalid command syntax\n"
    
    cmd_parts = cmd_line.split()
    
    city = cmd_parts[1].split('=')[1]
    if not city.isalpha():
        return "ERROR invalid city value\n"
    
    max_price = cmd_parts[2].split('=')[1]
    if max_price.isdigit():
        max_price = int(max_price)
    else:
        return "ERROR invalid max_price value\n"
    
    matches = []
    for listing in listings:
        if listing["city"] == city and listing["price"] <= max_price:
            matches.append(f"id={listing['id']};city={listing['city']};address={listing['address']};price={listing['price']};bedrooms={listing['bedrooms']}\n")
    response = [f"OK RESULT {len(matches)}\n"]
    response.extend(matches)
    response.append("END\n")
    return "".join(response)
    
def main():
    if len(sys.argv) != 3:
        print("ERROR invalid command syntax: python data_server.py <port> <db_file>\n")
        print("Example: python data_server.py 12345 listings.json\n")
        sys.exit(1)
    PORT = int(sys.argv[1])
    DB_FILE = sys.argv[2]

    try:
        with open(DB_FILE, 'r') as f:
            listings = json.load(f)
    except FileNotFoundError:
        print(f"ERROR database file '{DB_FILE}' not found\n")
        sys.exit(1)
    
    print("Successfully loaded database\n")

    s = socket(AF_INET, SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(5)
    print(f"Server is listening on {HOST}:{PORT}\n")

    while True:
        try:
            conn, addr = s.accept()
            data = conn.recv(1024)
            if not data:
                continue
            cmd_line = data.decode("ascii").strip()
            print(f"Received command: {cmd_line}\n")

            if cmd_line.startswith("RAW_LIST"):
                response = raw_list(listings)
            elif cmd_line.startswith("RAW_SEARCH"):
                if cmd_line.count(" ") != 2:
                    response = "ERROR invalid command syntax\n"
                else:
                    response = raw_search(cmd_line, listings)
            else:
                response = "ERROR invalid command syntax\n"

            conn.send(response.encode("ascii"))
        finally:
            conn.close()

if __name__ == "__main__":
    main()