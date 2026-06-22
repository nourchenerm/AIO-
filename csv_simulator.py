import socket
import json
import pandas as pd
import time

HOST = "127.0.0.1"
PORT = 5001

df = pd.read_csv("data/marwa_a.csv")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind((HOST, PORT))
server.listen(1)

print(f"TCP Server listening on {HOST}:{PORT}")

conn, addr = server.accept()

print("Client connected:", addr)

while True:

    for _, row in df.iterrows():

        payload = {
            "offset": [
                float(row["C1"]),
                float(row["C2"]),
                float(row["C3"]),
                float(row["C4"]),
                float(row["C5"]),
                float(row["C6"]),
                float(row["C7"]),
                float(row["C8"]),
                float(row["C9"]),
                float(row["C10"])
            ]
        }

        message = json.dumps(payload) + "\n"

        conn.sendall(message.encode())

        print(message)

        time.sleep(0.05)