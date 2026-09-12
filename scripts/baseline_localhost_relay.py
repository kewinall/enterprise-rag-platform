import socket
import socketserver
import threading


class Relay(socketserver.BaseRequestHandler):
    def handle(self):
        with socket.create_connection(("127.0.0.1", 6333)) as target:

            def pump(src, dst):
                try:
                    while True:
                        data = src.recv(65536)
                        if not data:
                            break
                        dst.sendall(data)
                except OSError:
                    pass
                try:
                    dst.shutdown(socket.SHUT_WR)
                except OSError:
                    pass

            t = threading.Thread(target=pump, args=(self.request, target), daemon=True)
            t.start()
            pump(target, self.request)
            t.join()


class Server(socketserver.ThreadingTCPServer):
    address_family = socket.AF_INET6
    daemon_threads = True
    allow_reuse_address = True


with Server(("::1", 6333), Relay) as server:
    print("IPv6 localhost relay ready", flush=True)
    server.serve_forever()
