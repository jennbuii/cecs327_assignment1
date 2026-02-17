import json
import sys
from socket import AF_INET, SOCK_STREAM, socket
from datetime import datetime

HOST = "127.0.0.1"

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
    
    end_response = [f"OK RESULT {len(response.splitlines()[1:-1])}\n"]
    ranked_response = sorted(response.splitlines()[1:-1], key=lambda x: (int(x.split(";")[3].split("=")[1]), -int(x.split(";")[4].split("=")[1])))
    end_response.extend(ranked_response)
    end_response.append("END\n")
    return "\n".join(end_response)

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
    
    end_response = [f"OK RESULT {len(response.splitlines()[1:-1])}\n"]
    ranked_response = sorted(response.splitlines()[1:-1], key=lambda x: (int(x.split(";")[3].split("=")[1]), -int(x.split(";")[4].split("=")[1])))
    end_response.extend(ranked_response)
    end_response.append("END\n")
    return "\n".join(end_response)

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

    while True:
        conn, addr = s.accept()
        try:
            data = conn.recv(1024)
            if not data:
                continue
            cmd_line = data.decode("ascii").strip()
            logger(f"Received command: {cmd_line}")

            if cmd_line.startswith("LIST"):
                response = raw_list(data_port)
            elif cmd_line.startswith("SEARCH"):
                response = raw_search(cmd_line, data_port)
            elif cmd_line.startswith("QUIT"):
                response = "OK QUIT\n"
                conn.send(response.encode("ascii"))
                continue
            else:
                response = "ERROR invalid command syntax\n"
            logger(f"Sending response: {response.strip()}\n")
            conn.send(response.encode("ascii"))
        finally:
            conn.close()

if __name__ == "__main__":
    main()