import grpc
from protobufs import service_pb2, service_pb2_grpc
from dotenv import load_dotenv
from utils import main as utils
import requests
import os

def get_pserver_address(query_type: str, base_server_address: str, data: str = None):
    url = f"http://{base_server_address}/peer"
    try:
        if query_type == "download":
            response = requests.post(url, json={"name": data})
        elif query_type == "upload":
            response = requests.get(url, params={"address": data})

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                return data.get("address")
            else:
                print(data.get("message"))
        else:
            print(f"Error: HTTP {response.status_code} received from server.")
    except Exception as e:
        print(f"Error connecting to server: {e}")
    return None

def download_file(pserver_address: str, name: str):
    try:
        with grpc.insecure_channel(pserver_address) as channel:
            stub = service_pb2_grpc.TransferServiceStub(channel)
            response = stub.Transfer(service_pb2.TransferRequest(name=name))
            return response.content if response.success else None
    except grpc.RpcError as e:
        print(f"RPC failed: {e}")
    return None

def upload_file(pserver_address: str, name: str, content: str):
    try:
        with grpc.insecure_channel(pserver_address) as channel:
            stub = service_pb2_grpc.UploadServiceStub(channel)
            response = stub.Upload(service_pb2.UploadRequest(name=name, content=content))
            if response.success:
                print(f"File '{name}' uploaded successfully.")
            else:
                print(f"Failed to upload file '{name}'.")
    except grpc.RpcError as e:
        print(f"RPC failed: {e}")

def mainloop(peer_address: str, base_server_address: str, resources: dict):
    while True:
        try:
            choice = input("1. Descargar un archivo\n2. Subir un archivo\n3. Cerrar\n").strip()
            if choice == '3':
                print("Closing client.")
                break

            if choice not in ['1', '2']:
                print("Seleccione una opción correcta.\n")
                continue

            name = input("Ingrese el nombre del archivo: ").strip()
            if choice == '1':
                if name in resources:
                    print(f"El archivo {name} ya existe en el peer.")
                else:
                    pserver_address = get_pserver_address("download", base_server_address, name)
                    if pserver_address:
                        content = download_file(pserver_address, name)
                        if content:
                            utils.write_files_in_directory("files", {name: content})
                            print(f"Archivo '{name}' descargado y guardado.")
            elif choice == '2':
                content = input("Ingrese el contenido del archivo: ").strip()
                pserver_address = get_pserver_address("upload", base_server_address, peer_address)
                if pserver_address:
                    upload_file(pserver_address, name, content)
        except Exception as e:
            print(f"An error occurred: {e}")

def run():
    load_dotenv()
    peer_ip = os.getenv("PEER_IP")
    peer_port = os.getenv("PEER_PORT")
    peer_directory = os.getenv("PEER_DIRECTORY")
    base_server_ip = os.getenv("BASE_SERVER_IP")
    base_server_port = os.getenv("BASE_SERVER_PORT2")

    peer_address = f"{peer_ip}:{peer_port}"
    base_server_address = f"{base_server_ip}:{base_server_port}"
    resources = utils.get_files_from_directory(peer_directory)

    mainloop(peer_address, base_server_address, resources)

if __name__ == '__main__':
    run()
