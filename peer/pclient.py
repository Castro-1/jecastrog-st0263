import grpc
from protobufs import service_pb2, service_pb2_grpc
from dotenv import load_dotenv
from utils import main as utils
import requests
import os

resources = []  



def get_pserver_address(query_type: str, base_server_address: str, data: str | None):
    if query_type == "download":
        try:
            response = requests.post(f"http://{base_server_address}/peer", json={"name": data})
            data = response.json()
            if not data.get("success", False):
                print(data.get("message"))
                return None
            return data.get("address", None)
        except Exception as e:
            print(e)
            return None
    if query_type == "upload":
        try:
            response = requests.get(f"http://{base_server_address}/peer?address={data}")
            data = response.json()
            if not data.get("success", False):
                print(data.get("message"))
                return None
            return data.get("address", None)
        except Exception as e:
            print(e)
            return None

def download_file(pserver_address:str, name: str):

    with grpc.insecure_channel(pserver_address) as channel:

        stub = service_pb2_grpc.TransferServiceStub(channel)

        response = stub.Transfer(service_pb2.TransferRequest(name=name))

        return response.content

def upload_file(pserver_address:str, name: str, content: str):
    
        with grpc.insecure_channel(pserver_address) as channel:
    
            stub = service_pb2_grpc.UploadServiceStub(channel)
    
            response = stub.Upload(service_pb2.UploadRequest(name=name, content=content))

            if response.success:
                print("Contenido del archivo subido: ", response.name)
            else:
                print("No se pudo subir el archivo.")

def mainloop(peer_address: str, base_server_address: str, resources: dict):
    try:
        while True:
            choice = int(input("1. Descargar un archivo\n2. Subir un archivo\n3. Cerrar\n"))

            if choice == 3:
                break

            if choice > 3 or choice <= 0:
                print("Seleccione una opción correcta:\n")
                continue

            if choice == 1:
                name = str(input("Ingrese el nombre del archivo: "))

                if name in resources:
                    print(f"El archivo {name} ya existe en el peer.")
                    continue

                pserver_address = get_pserver_address("download", base_server_address, name)

                if pserver_address:
                   content = download_file(pserver_address, name)
                   utils.write_files_in_directory("files", {name: content})
                   print(f"Archivo Creado: {name}")
                continue

            if choice == 2:
                name = str(input("Ingrese el nombre del archivo: "))
                content = str(input("Ingrese el contenido del archivo: "))

                if name in resources:
                    print(f"El archivo {name} ya existe en el peer.")
                    continue

                pserver_address = get_pserver_address("upload", base_server_address, peer_address)

                if pserver_address:
                    upload_file(pserver_address, name, content)
                continue

    except Exception as e:
        print(e)
        print("Something went wrong. Exiting...")

def run():
    global resources

    peer_ip = os.getenv("PEER_IP")
    peer_port = os.getenv("PEER_PORT")
    peer_directory = os.getenv("PEER_DIRECTORY")
    base_server_ip = os.getenv("BASE_SERVER_IP")
    base_server_port = os.getenv("BASE_SERVER_PORT2")

    resources = utils.get_files_from_directory(peer_directory)

    peer_address = f"{peer_ip}:{peer_port}"
    base_server_address = f"{base_server_ip}:{base_server_port}"

    mainloop(peer_address, base_server_address, resources)


if __name__ == '__main__':
    load_dotenv()
    run()
