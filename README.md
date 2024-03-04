# ST0263 Tópicos Especiales en Telemática

## Estudiante: Juan Esteban Castro Garcia, jecastrog@eafit.edu.co

## Profesor: Edwin Nelson Montoya Munera, emontoya@eafit.edu.co

# Reto 1 y 2

### 1. Breve descripción de la actividad
Desarrollar un sistema P2P distribuido y descentralizado con el objetivo de compartir archivos. Esta implementación se debe basar en un esquema de red no estructurado en el cual un servidor central sirva como directorio y localizador. Un peer está compuesto por un cliente y un servidor. El cliente se debe comunicar con el servidor central para cargar y descargar archivos, este le debe responder con la dirección de un peer que contenga el archivo a descargar o que tenga espacio para cargar un archivo. El servidor del peer debe comunicarse con el servidor central para darle su estado y los archivos que contiene.

### 1.1. Qué aspectos cumplió o desarrolló de la actividad propuesta por el profesor (requerimientos funcionales y no funcionales)
Se desarrolló un servidor central que almacena los peers que se encuentran conectados en la red y su tabla de archivos. El servidor se comunica con los los servidores del peer a través de comunicación gRPC. Estos pueden iniciar sesión en la red, comunicar el estado de su tabla de archivos y desconectarse de la red. En adición, el cliente de los peers se comunica con el servidor central a través de REST API, de esta manera puede pedirle la dirección de un peer que tenga un archivo de que desee descargar o un peer en el cual cargar un archivo. La comunicación entre peers se hace a través de gRPC, haciendo la transferencia de archivos mucho más eficiente. Se cumple con todos los requisitos generales de la red. 


### 1.2. Qué aspectos NO cumplió o desarrolló de la actividad propuesta por el profesor (requerimientos funcionales y no funcionales)
No se cumplió con el requisito de "heartbeat", un mensaje por el cual el servidor del peer le comunica al servidor central que aún sique conectado a la red.

### 2. Información general de diseño de alto nivel, arquitectura, patrones, mejores prácticas utilizadas.
- **Descripción general diseño de alto nivel**: Este proyecto implementa una red peer-to-peer (P2P) no estructurada, con un enfoque híbrido que integra un servidor central para facilitar la localización y el intercambio de archivos entre peers. El servidor central actúa como un directorio y localizador para los peers en la red. Este servidor mantiene un registro de los archivos disponibles en la red y su ubicación correspondiente en los peers. El peer actúa como cliente y servidor (pclient y pserver). El pserver se encarga de gestionar los archivos locales, mientras que el pclient se utiliza para interactuar con otros peers y con el servidor central para buscar y transferir archivos. Al iniciarse, el pserver se comunica con el servidor central utilizando gRPC para registrarse en la red y enviar la lista de archivos disponibles en su directorio "files". El pclient interactúa con el servidor central mediante REST API para realizar consultas sobre la disponibilidad de archivos en la red y recibir direcciones de peers que contienen los archivos solicitados. Posteriormente, establece comunicación directa con otros pservers a través de gRPC para descargar o subir archivos.
- **Arquitectura de comunicaciones:** Se utiliza gRPC para la comunicación entre pclients y pservers y entre pserver y servidor central. Esta elección permite una comunicación eficiente, aprovechando las ventajas de gRPC como su alto rendimiento y la definición clara de interfaces mediante protocol buffers. Se utiliza REST API para la interacción entre pclients y el servidor central, proporcionando una interfaz sencilla y flexible para realizar consultas y recibir respuestas en un formato ampliamente compatible y fácil de usar.
- **Patrones de diseño y mejores prácitcas**: Se puede evidenciar la utilización del patrón Cliente - Servidor, y esta se manifiesta de dos formas: la comunicación entre pclient y servidor central, y entre pclient y pserver. Esta separación de roles facilita la modularidad y la escalabilidad de la red. Se hace uso de la técnica Round Robin para equilibrar la carga entre los peers, asignando de manera rotativa la dirección de un peer para la carga de nuevos archivos. El pserver monitorea constantemente el directorio "files" para detectar cambios. Al identificar una modificación, actualiza la tabla de archivos y la envía al servidor central, asegurando que la información en la red esté siempre actualizada.

![image](https://github.com/Castro-1/jecastrog-st0263/assets/82610906/27c391c4-6da5-4943-ad4d-cc773e8e3e02)



### 3. Descripción del ambiente de desarrollo y técnico: lenguaje de programación, librerias, paquetes, etc, con sus numeros de versiones.

- **Lenguaje de Programación:** Python 3.10.12.
- **Entorno de Desarrollo Integrado (IDE):** Visual Studio Code

#### Librerías y Paquetes Principales:

- **grpcio:** Proporciona funcionalidades gRPC en Python para la comunicación entre los peers y el servidor central. Versión 1.62.0.
- **grpcio-tools:** Incluye herramientas para trabajar con gRPC en Python, como la compilación de archivos .proto. Versión 1.62.0.
- **requests:** Utilizada para realizar peticiones HTTP, en este caso, desde el pclient hacia el servidor central. Versión 2.31.0.
- **python-dotenv:** Permite cargar variables de entorno desde un archivo .env, lo que facilita la configuración del proyecto sin hardcodear valores. Versión 1.0.1.
- **Flask:** Un microframework para Python que se usa para implementar la interfaz REST API del servidor central. Versión 3.0.2.

#### Cómo se compila y ejecuta.
1. Hacerle git clone a este repositorio:
```
git clone https://github.com/Castro-1/jecastrog-st0263.git
```
2. (Opcional): Navegar hasta la carpeta del proyecto y crear un ambiente virtual de python con el siguiente comando:
```
python -m venv venv
```
Activamos el ambiente virutal creado:
```
source venv/bin/activate
```
3. Navegamos hacia la carpeta server e instalamos los paquetes necesarios:
```
pip install -r requirements.txt
```
4. Corremos el servidor:
```
python server.py
```
5. Navegamos a la carpeta peer e instalamos los paquetes necesarios:
```
pip install -r requirements.txt
```
6. Modificamos el nombre del archivo ".env.example" a ".env".
7. Damos permisos de ejecución al script para ejecutar pclient y pserver:
```
chmod +x start_services.sh
```
8. Ejecutamos el peer haciendo uso del script:
```
./start_services.sh
```
Ya puedes interactuar con el servidor principal!

9. Ahora, si quieres probar con más peers: copia la carpeta peer, cambiale el nombre, cambiale el nombre a algunos archivos de la carpeta files, camiba el PEER_PORT dentro del archivo ".env" para que sea diferente al puerto del primer peer. Si usaste el entorno virutal, asegurate de activarlo y luego ejecuta el script.

### 4. Descripción del ambiente de EJECUCIÓN (en producción) lenguaje de programación, librerias, paquetes, etc, con sus numeros de versiones.
Los ambientes en ejecución se basan en contenedores Docker que encapsulan el entorno de Python y las dependencias necesarias.
- **Lenguaje de Programación:** Python 3.8.
- **Base de la Imagen Docker:** python:3.8-slim.
- **Librerías y Paquetes:** Las librerías y paquetes están especificados en los requirements.txt de cada componente (peer y servidor) y son instalados en la imagen Docker sin almacenar en caché para asegurar que se use la versión más actual en el momento de la creación de la imagen.
Si se desea conocer la configuración detallada, se puede observar en el archivo Dockerfile del peer y del servidor.

**Para el peer:**
- Puertos Externos: 50051 y 5005 son expuestos y utilizados para la comunicación gRPC.

**Para el servidor:**
- Puertos Externos: 50051 y 50052 son expuestos y utilizados para la comunicación gRPC y API REST respectivamente.

#### IP o Nombres de Dominio en la Nube o en la Máquina Servidor

Las máquinas virtuales de Ubuntu en AWS se utilizan para desplegar los servicios. Cada máquina tiene asignada una IP elástica para mantener la consistencia de las direcciones IP entre diferentes sesiones.

#### Descripción y Configuración de Parámetros del Proyecto
- **Variables de Entorno:** Las variables de entorno necesarias para cada contenedor (por ejemplo, PEER_IP, PEER_PORT, BASE_SERVER_IP, BASE_SERVER_PORT) deben ser pasadas al comando docker run utilizando la opción -e para establecer cada variable, por ejemplo, -e PEER_IP='x.x.x.x'.
- **Puertos:** En AWS, el grupo de seguridad debe tener habilitado el tráfico entrante para los puertos 50051 y 50052 para permitir la comunicación.

**Cómo se lanza el servidor**
Para lanzar el servidor central, se utiliza el comando docker run, especificando los puertos a mapear y el modo interactivo:
```
docker run -it -p 50051:50051 -p 50052:50052 imagen_servidor_central
```
**Cómo se lanza el peer**
```
docker run -it -p 50051:50051 -e PEER_IP=ip_elástica_instancia -e PEER_PORT=50051 -e BASE_SERVER_IP=ip_elástica_instancia_servidor -e BASE_SERVER_PORT=50051 -e BASE_SERVER_PORT2=50052 imagen_peer
```
#### Mini Guía de Uso para el Usuario

1. **Inicio:** El usuario debe asegurarse de que la máquina virtual y el contenedor Docker estén en ejecución.

2. **Conexión al Peer:** Para los peers, después de ejecutar el contenedor con el comando docker run, el usuario puede interactuar a través de la CLI proporcionada por el script start_services.sh para el peer.

3. **Operaciones Disponibles:**
- **Descargar un Archivo:** El usuario puede seleccionar la opción para descargar archivos disponibles en la red P2P.
- **Subir un Archivo:** El usuario puede elegir subir un archivo, que luego estará disponible para otros peers.
- **Cierre:** El usuario puede cerrar la aplicación de peer siguiendo las instrucciones proporcionadas en la CLI, generalmente seleccionando la opción de cerrar o terminar la sesión.

### referencias:
1. **[gRPC](https://www.paradigmadigital.com/dev/grpc-que-es-como-funciona/)**
2. **[Docker](https://www.redhat.com/es/topics/containers/what-is-docker)**
3. **[ChatGPT](https://chat.openai.com/)**
