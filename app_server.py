import json
import sys
from socket import AF_INET, SOCK_STREAM, socket
from datetime import datetime

HOST = "127.0.0.1"

#Cache
USE_Cache = True
Cache = {}

def logger(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("app_server.log", "a") as log_file:
        log_file.write(f"{timestamp} - {message}\n")

def raw_list(data_port):
    s = socket(AF_INET, SOCK_STREAM)
    try:
        s.connect((HOST, data_port))
        s.send("RAW_LIST\n".encode("ascii"))
        response = s.recv(4096)
        response = response.decode("ascii")
    finally:
        s.close()

    if response.startswith("ERROR"):
        return response
    
    end_response = [f"OK RESULT {len(response.splitlines()[1:-1])}"]
    ranked_response = sorted(response.splitlines()[1:-1], key=lambda x: (int(x.split(";")[3].split("=")[1]), -int(x.split(";")[4].split("=")[1])))
    end_response.extend(ranked_response)
    end_response.append("END")
    return "\n".join(end_response) + "\n"

def raw_search(cmd_line, data_port):
    s = socket(AF_INET, SOCK_STREAM)
    try:
        s.connect((HOST, data_port))
        # cmd_line = "SEARCH city=LongBeach max_price=2500\n"
        cmd_parts = cmd_line.strip().split()
        # need to send the command in the format "RAW_SEARCH city=CityName max_price=123\n"
        s.send(("RAW_SEARCH " + cmd_parts[1] + " " + cmd_parts[2] + "\n").encode("ascii"))
        response = s.recv(4096)
        response = response.decode("ascii")
    finally:
        s.close()

    if response.startswith("ERROR"):
        return response
    
    end_response = [f"OK RESULT {len(response.splitlines()[1:-1])}"]
    ranked_response = sorted(response.splitlines()[1:-1], key=lambda x: (int(x.split(";")[3].split("=")[1]), -int(x.split(";")[4].split("=")[1])))
    end_response.extend(ranked_response)
    end_response.append("END")
    return "\n".join(end_response) + "\n"

def main():
    if len(sys.argv) != 3:
        print("ERROR invalid command syntax: python app_server.py <app_port> <data_port>\n")
        print("Example: python app_server.py 12345 54321\n")
        sys.exit(1)
    app_port = int(sys.argv[1])
    data_port = int(sys.argv[2])
    s = socket(AF_INET, SOCK_STREAM)
    s.bind((HOST, app_port))
    s.listen(5)
    print(f"App server listening on port {app_port}\n")
    print(f"Caching is: {'enabled' if USE_Cache else 'disabled'}\n")

    while True:
        conn, addr = s.accept()
        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                cmd_line = data.decode("ascii").strip()
                logger(f"Received command: {cmd_line}")

                #Caching logic
                if USE_Cache and cmd_line in Cache:
                    logger(f"Cache hit: Serving {cmd_line} from memory\n")
                    response = Cache[cmd_line]
                else:
                    if USE_Cache:
                        logger(f"Cache miss: Fetching {cmd_line} from data server\n")
    
                    if cmd_line.startswith("LIST"):
                        response = raw_list(data_port)
                    elif cmd_line.startswith("SEARCH"):
                        response = raw_search(cmd_line, data_port)
                    elif cmd_line.startswith("QUIT"):
                        response = "OK QUIT\n"
                        conn.send(response.encode("ascii"))
                        break
                    else:
                        response = "ERROR invalid command syntax\n"
                    logger(f"Sending response: {response.strip()}\n")
                conn.send(response.encode("ascii"))

                #Store result in cache if valid and caching is enabled
                if USE_Cache and response.startswith("OK RESULT"):
                    Cache[cmd_line] = response
                
        finally:
            conn.close()

if __name__ == "__main__":
    main()