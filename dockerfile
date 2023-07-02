FROM python:3.9

# Instalar las dependencias necesarias
RUN pip install psycopg2 Pyro4

# Copiar el código fuente de la aplicación en el contenedor
COPY . /app
WORKDIR /app

# Exponer el puerto que usará el servidor Pyro4
EXPOSE 9090

# Ejecutar el servidor Pyro4 al iniciar el contenedor
CMD ["python", "Server.py"]