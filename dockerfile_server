FROM python:3.9

ADD Servidor.py .

# Instalar las dependencias necesarias
RUN pip install psycopg2 Pyro4

# Exponer el puerto que usará el servidor Pyro4
EXPOSE 9090

# Ejecutar el servidor Pyro4 al iniciar el contenedor
CMD ["python", "Servidor.py"]