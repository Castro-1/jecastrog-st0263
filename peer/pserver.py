import grpc
from concurrent import futures
from protobufs import service_pb2, service_pb2_grpc
from dotenv import load_dotenv
import os
from utils import main as utils
import threading
import time
import signal
from contextlib import contextmanager

server = None

peer_ip = os.getenv("PEER_IP")
peer_port = os.getenv("PEER_PORT")
base_server_ip = os.getenv("BASE_SERVER_IP")
base_server_port = os.getenv("BASE_SERVER_PORT")

peer_address = f"{peer_ip}:{peer_port}"
base_server_address = f"{base_server_ip}:{base_server_port}"
resources = utils.get_files_from_directory("files")

@contextmanager
def graceful_shutdown(server):
    try:
        yield
    finally:
        print('Shutting down the server...')
        server.stop(10)  # Espera hasta 10 segundos para que las operaciones pendientes finalicen
        logout(base_server_address, peer_address)
        print('Server shut down. Logged out successfully.')


def login(base_server_address: str, peer_address: str, resources: list):
    with grpc.insecure_channel(base_server_address) as channel:
        stub = service_pb2_grpc.LoginServiceStub(channel)
        response = stub.Login(service_pb2.LoginRequest(address=peer_address, items=resources))
        print("Login response:", response.message)


def logout(base_server_address: str, peer_address: str):
    with grpc.insecure_channel(base_server_address) as channel:
        stub = service_pb2_grpc.LogoutServiceStub(channel)
        response = stub.Logout(service_pb2.LogoutRequest(address=peer_address))
        print("Logout response:", response.message)


def update(base_server_address: str, peer_address: str):
    global resources
    with grpc.insecure_channel(base_server_address) as channel:
        stub = service_pb2_grpc.TableServiceStub(channel)
        response = stub.Table(service_pb2.TableRequest(address=peer_address, items=resources))
        print("Resources updated:", response.message)


class TransferService(service_pb2_grpc.TransferServiceServicer):
    def Transfer(self, request, context):
        name = request.name
        if name not in self.resources:
            return service_pb2.TransferResponse(success=False, content="")
        content = self.resources[name]
        return service_pb2.TransferResponse(success=True, content=content)
    

class UploadService(service_pb2_grpc.UploadServiceServicer):
    def Upload(self, request, context):
        name = request.name
        content = request.content
        if name in self.resources:
            return service_pb2.UploadResponse(success=False, name=name)
        utils.write_files_in_directory("files", {name: content})
        return service_pb2.UploadResponse(success=True, name=name)


def serve_resources(peer_port: str):
    global server, resources
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    TransferService.resources = resources
    UploadService.resources = resources
    service_pb2_grpc.add_TransferServiceServicer_to_server(TransferService(), server)
    service_pb2_grpc.add_UploadServiceServicer_to_server(UploadService(), server)
    server.add_insecure_port('[::]:' + peer_port)
    server.start()
    server.wait_for_termination()

def check_for_files(base_server_address: str, peer_address: str):
    global resources
    while True:
        newResources = utils.get_files_from_directory("files")
        if newResources != resources:
            resources = newResources
            update(base_server_address, peer_address)
        time.sleep(1)


def run():
    global base_server_address, peer_address, resources, server
    login(base_server_address, peer_address, resources)
    
    with graceful_shutdown(server):
        grpc_thread = threading.Thread(target=serve_resources, args=(peer_port,))
        check_thread = threading.Thread(target=check_for_files, args=(base_server_address, peer_address))
        
        grpc_thread.start()
        check_thread.start()
        
        signal.signal(signal.SIGINT, lambda sig, frame: print('Interrupted'))
        
        grpc_thread.join()

if __name__ == "__main__":
    load_dotenv()
    run()
