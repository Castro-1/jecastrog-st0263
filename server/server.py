from concurrent import futures
import threading
from flask import Flask, request, jsonify, abort
import grpc
from protobufs import service_pb2, service_pb2_grpc
import random
import os
from dotenv import load_dotenv

app = Flask(__name__)

peer_connected = set()
item_to_peer = {}


class LoginService(service_pb2_grpc.LoginServiceServicer):
    def Login(self, request, context):
        address = request.address
        items = request.items

        if address in peer_connected:
            return service_pb2.LoginResponse(success=False, message="Ya estás iniciado!")

        peer_connected.add(address)

        for item in items:
            item_to_peer.setdefault(item, []).append(address)

        return service_pb2.LoginResponse(success=True, message="Bienvenido!")


class LogoutService(service_pb2_grpc.LogoutServiceServicer):
    def Logout(self, request, context):
        address = request.address

        if address not in peer_connected:
            return service_pb2.LogoutResponse(success=False, message="No estabas iniciado")

        peer_connected.remove(address)

        for items in item_to_peer.values():
            if address in items:
                items.remove(address)

        return service_pb2.LogoutResponse(success=True, message="Hasta pronto!")


class TableService(service_pb2_grpc.TableServiceServicer):
    def Table(self, request, context):
        address = request.address
        items = request.items

        for item in items:
            item_to_peer.setdefault(item, []).append(address)

        return service_pb2.TableResponse(success=True, message="Tabla actualizada")


@app.route('/peer', methods=['POST', 'GET'])
def get_peer():
    if request.method == 'POST':
        if not request.json or 'name' not in request.json:
            abort(400)

        name = request.json['name']

        if name not in item_to_peer or not item_to_peer[name]:
            return jsonify(success=False, message="No existe el archivo.")

        peer_address = random.choice(item_to_peer[name])
        return jsonify(success=True, address=peer_address)

    if request.method == 'GET':
        bad_address = request.args.get('address')

        valid_peers = [peer for peer in peer_connected if peer != bad_address]

        if not valid_peers:
            return jsonify(success=False, message="No hay peers disponibles.")

        peer_address = random.choice(valid_peers)
        return jsonify(success=True, address=peer_address)


def run_flask_app():
    app.run(debug=True, host='0.0.0.0', port=50052, use_reloader=False)


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
