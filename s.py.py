import socket
import threading
import sqlite3

HOST = "0.0.0.0"
PORT = 80

clients = {}  # socket: username
lock = threading.Lock()


# ---------------- DATABASE ----------------

def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            username TEXT PRIMARY KEY,
            password TEXT,
            colors TEXT
        )
    """)
    conn.commit()
    conn.close()


def register_user(username, password, color):
    try:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users VALUES(?,?,?)", (username, password, color))
        conn.commit()
        conn.close()
        return True
    except:
        return False


def login_user(username, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?",
                   (username, password))
    result = cursor.fetchone()
    conn.close()
    return result is not None

#########################
def save_color(username, password, coloru):
    try:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users
            SET colors=?
            WHERE username=? AND password=?
        """, (coloru, username, password))

        conn.commit()
        conn.close()
        return True
    except:
        return False
   

def get_color(username, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?",
                   (username, password))
    result = cursor.fetchone()
    colorr = result[2]
    conn.close()
    return colorr

# ---------------- BROADCAST ----------------

def broadcast(message, exclude=None):
    with lock:
        for client in list(clients.keys()):
            if client != exclude:
                try:
                    client.sendall((message + "\n").encode())
                except:
                    remove_client(client)


def remove_client(client):
    with lock:
        username = clients.get(client)
        if username:
            print(f"{username} disconnected")
            broadcast(f"SYSTEM@{username} покинув чат")
            del clients[client]
    client.close()


# ---------------- CLIENT HANDLER ----------------

def handle_client(client):
    username = None
    try:
        print("SOMETHING")
        while True:
            data = client.recv(4096)
            if not data:
                break

            message = data.decode().strip()
            parts = message.split("@", 3)
            command = parts[0]

            # ---------- REGISTER ----------
            if command == "REGISTER":
                if len(parts) < 4:
                    continue

                username = parts[1]
                password = parts[2]
                color = parts[3]

                if register_user(username, password, color):
                    client.send("REGISTER_OK\n".encode())
                else:
                    client.send("REGISTER_FAIL@Користувач існує\n".encode())

            # ---------- LOGIN ----------
            elif command == "LOGIN":
                if len(parts) < 3:
                    continue

                username = parts[1]
                password = parts[2]

                if login_user(username, password):
                    with lock:
                        clients[client] = username
                    client.send("LOGIN_OK\n".encode())
                    broadcast(f"SYSTEM@{username} приєднався")
                else:
                    client.send("LOGIN_FAIL\n".encode())

            # ---------- TEXT ----------
            elif command == "TEXT":
                if client in clients:
                    text = parts[1]
                    broadcast(f"TEXT@{clients[client]}@{text}", exclude=client)

            # ---------- IMAGE ----------
            elif command == "IMAGE":
                if client in clients and len(parts) >= 3:
                    filename = parts[1]
                    image_data = parts[2]
                    broadcast(
                        f"IMAGE@{clients[client]}@{filename}@{image_data}",
                        exclude=client
                    )
            # ----------- COLOR ----------
            elif command == "COLOR":
                if len(parts) < 4:
                    continue
                username = parts[1]
                password = parts[2]
                colordata = parts[3]
                if save_color(username,password,colordata):
                    client.send(colordata.encode())
                else:
                    print("FAILURE")
                    client.send("COLOR_SAVE_FAIL\n".encode())
            # ----------- GET COLOR VALUE FROM USER ---------
            elif command == "COLOR_GET":
 
                username = parts[1]
                password = parts[2]
                colorda = get_color(username,password)
                print(colorda)
                client.send(f"COLOR_GET@{colorda}\n".encode())

    except Exception as e:
        print("Client error:", e)

    finally:
        remove_client(client)


# ---------------- MAIN ----------------

def main():
    init_db()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server.bind((HOST, PORT))
    except Exception as e:
        print("Помилка bind:", e)
        return

    server.listen(10)
    print(f"Server started on {HOST}:{PORT}")

    while True:
        client, addr = server.accept()
        print("New connection:", addr)
        threading.Thread(
            target=handle_client,
            args=(client,),
            daemon=True
        ).start()


if __name__ == "__main__":
    main()
