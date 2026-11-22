import ollama
import socket
import threading

class Sage:
    def __init__(self):
        self.sage = {"answer": ""}
        self.lock = threading.Lock()

    def ask_sage(self, text):
        system_prompt = (
            "You are Sage, you help with questions from the user involving "
            "physics and space. You will answer in around 3 sentences or shorter."
        )
        try:
            response = ollama.chat(
                model='llama3.2:3b',
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': text},
                ],
            )
            answer = response.message.content
        except Exception as e:
            answer = f"Error: {e}"

        with self.lock:
            self.sage["answer"] = answer
        return answer

    def sage_line(self, i):
        with self.lock:
            return str(self.sage["answer"])[i * 44:(i + 1) * 44]


def handle_client(sage, conn, addr):
    print(f"Connection from: {addr}")
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            message = data.decode(errors="replace").strip()
            if not message:
                continue
            print(f"[{addr}] Received: {message!r}")
            try:
                response = sage.ask_sage(message)
            except Exception as e:
                print(f"[{addr}] Handler error: {e}")
                response = "Sorry, something went wrong processing that."
            print(f"[{addr}] Replying: {response!r}")
            conn.sendall(response.encode())
    except Exception as e:
        print(f"Error from {addr}: {e}")
    finally:
        conn.close()
        print(f"Connection closed: {addr}")


if __name__ == "__main__":
    sage = Sage()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", 1337))
    s.listen()

    print("Sage server listening on port 1337...")
    while True:
        conn, addr = s.accept()
        threading.Thread(
            target=handle_client, args=(sage, conn, addr), daemon=True
        ).start()
