from concurrent import futures
import threading
from flask import Flask, request, jsonify, abort
import grpc
from protobufs import service_pb2, service_pb2_grpc
import random
import os
from dotenv import load_dotenv

app = Flask(__name__)

peer_connected = []
item_to_peer = {}
peer_count = 0



class LoginService(service_pb2_grpc.LoginServiceServicer):
    def Login(self, request, context):
        global item_to_peer
        address = request.address
        items = request.items

        print("Login")

        if address in peer_connected:
            return service_pb2.LoginResponse(
                success=False, message="Ya estás iniciado!"
            )

        peer_connected.append(address)

        print(items)
        for item in items:
            if item not in item_to_peer.keys():
                item_to_peer[item] = [address]
                continue
            if address in item_to_peer[item]:
                continue

            item_to_peer[item] += [address]

        print(f"Peers conectados: {peer_connected}")
        print(f"Items a Peer: {item_to_peer}")

        return service_pb2.LoginResponse(success=True, message="Bienvenido!")


class LogoutService(service_pb2_grpc.LogoutServiceServicer):
    def Logout(self, request, context):
        address = request.address

        print("Logout")

        if address not in peer_connected:
            return service_pb2.LogoutResponse(
                success=False, message="No estabas iniciado"
            )

        peer_connected.remove(address)

        print(f"Estado de Peers: {peer_connected}")

        return service_pb2.LogoutResponse(success=True, message="Hasta pronto!")

class TableService(service_pb2_grpc.TableServiceServicer):
    def Table(self, request, context):
        global item_to_peer
        address = request.address
        items = request.items

        print("Table")

        for item in items:
            if item not in item_to_peer.keys():
                item_to_peer[item] = [address]
                continue
            if address in item_to_peer[item]:
                continue

            item_to_peer[item] += [address]
        
        print(item_to_peer)

        return service_pb2.TableResponse(success=True, message="Tabla actualizada")

@app.route('/peer', methods=['POST', 'GET'])
def get_peer():
    global peer_count
    if request.method == 'POST':
        if not request.json or 'name' not in request.json:
            abort(400)
        
        name = request.json['name']

        print("Download")

        if name not in item_to_peer:
            return jsonify(success=False, message="No existe el archivo.")
        
        peer_addresses = item_to_peer[name]
        random_number = random.randint(0, len(peer_addresses) - 1)
                
        peer_address = peer_addresses[random_number]

        print(f"Peer seleccionado: {peer_address}")

        return jsonify(success=True, address=peer_address)
    
    if request.method == 'GET':
        bad_address = request.args.get('address')
        if len(peer_connected) == 0:
            return jsonify(success=False, message="No hay peers conectados.")
        
        peer_address = ""

        if peer_count >= len(peer_connected):
            peer_count = 0

        peer_address = peer_connected[peer_count]
        print("Bad address: ", bad_address)
        print("Peer seleccionado: ", peer_address)
        peer_count += 1
        while bad_address == peer_address and peer_count < len(peer_connected):
            peer_address = peer_connected[peer_count]
            peer_count += 1

        if peer_address == "" or bad_address == peer_address:
            return jsonify(success=False, message="No hay peers disponibles.")
        return jsonify(success=True, address=peer_address)

        


def run_flask_app():
    server_ip = os.getenv("SERVER_IP")
    app.run(debug=True, host=server_ip, port=50052, use_reloader=False)
        

def serve():
    print("El servidor se está ejecutando")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_LoginServiceServicer_to_server(LoginService(), server)
    service_pb2_grpc.add_LogoutServiceServicer_to_server(LogoutService(), server)
    service_pb2_grpc.add_TableServiceServicer_to_server(TableService(), server)
    server.add_insecure_port("[::]:50051")

    grpc_thread = threading.Thread(target=server.start)
    grpc_thread.start()
    
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.start()

    grpc_thread.join()
    flask_thread.join()


if __name__ == "__main__":
    load_dotenv()
    serve()
