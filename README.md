# cecs327_assignment1

Instructions on how to start each component (exact commands, ports, order).

Starting data_server.py: 
  1. New Terminal (A)
  2. Command Syntax: python data_server.py <port> <db_file>
        ex: python data_server.py 3200 listings.json

Starting app_server.py:
  1. Start data_server.py
  2. New Terminal (B)
  3. Command Syntax: python app_server.py <app_port> <data_port>
        ex: python data_server.py 3400 3200

Starting client.py:
  1. Start data_server.py (Terminal A)
  2. Start app_server.py (Terminal B)
  3. New Terminal (C)
  4. Command Syntax: python client.py <app_port>
       ex: python client.py 3400

Any configuration options... (Include how to toggle cache here, if making toggable?)
