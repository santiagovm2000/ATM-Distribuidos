import psycopg2
import Pyro4
import random
import subprocess

subprocess.Popen(['/usr/bin/pyro4-ns'])

@Pyro4.expose
class ATM:
    
    @staticmethod
    def get_connection():
        conn = psycopg2.connect(
                database="postgres",
                user="postgres", 
                password="romero-vieira", 
                host="localhost",
                port=5432,
                options=f"-c search_path=public")
        cur = conn.cursor()
        return conn, cur
    
    def cerrar_conexion(self,cur,conn):
        cur.close()
        conn.close()
    
    def get_balance(self, account_number):
        conn, cur = ATM.get_connection()
        cur.execute("SELECT saldo FROM cuenta WHERE numero_cuenta=%s", (account_number,))
        row = cur.fetchone()
        self.cerrar_conexion(cur,conn)
        if row:
            return row[0]
        else:
            return None

    def withdraw(self, account_number, amount):
        conn, cur = ATM.get_connection()
        cur.execute("SELECT saldo FROM cuenta WHERE numero_cuenta=%s", (account_number,))
        row = cur.fetchone()
        if row:
            balance = row[0]
            if balance >= amount:
                cur.execute("UPDATE cuenta SET saldo=%s WHERE numero_cuenta=%s", (balance-amount, account_number))
                conn.commit()
                self.cerrar_conexion(cur,conn)
                return True
            else:
                self.cerrar_conexion(cur,conn)
                return False
        else:
            self.cerrar_conexion(cur,conn)
            return None
        
    def user_exist(self, id_documento):
        conn, cur = ATM.get_connection()
        cur.execute("SELECT id_documento FROM usuario WHERE id_documento=%s", (id_documento,))
        row = cur.fetchone()
        self.cerrar_conexion(cur,conn)
        if row:
            return True
        else:
            return False
        
    def num_cuentas(self, id_beneficiario):
        conn, cur = ATM.get_connection()
        cur.execute("SELECT COUNT(*) FROM cuenta WHERE id_beneficiario=%s", (id_beneficiario,))
        row = cur.fetchone()
        self.cerrar_conexion(cur,conn)
        if row:
            return row[0]
        else:
            return 0
        
    def autenticar(self,usuario,contrasena):
        conn, cur = ATM.get_connection()
        cur.execute("SELECT id_documento FROM usuario WHERE usuario=%s AND contrasena=%s", (usuario,contrasena))
        row = cur.fetchone()
        self.cerrar_conexion(cur,conn)
        if row:
            return row[0]
        else:
            return False
            
    def get_transactions(self, account_number):
        conn, cur = ATM.get_connection()
        cur.execute("SELECT fecha, monto, descripcion, num_cuenta_destino FROM transaccion WHERE num_cuenta_origen=%s ORDER BY fecha DESC LIMIT 5", (account_number,))
        rows = cur.fetchall()
        self.cerrar_conexion(cur, conn)
        if rows:
            return rows
        else:
            return None
            
    def transaction(self,cta_origen,cta_destino,monto,descripcion):
        conn, cur = ATM.get_connection()
        try:
            cur.execute("SELECT saldo FROM cuenta WHERE numero_cuenta=%s", (cta_origen,))
            row = cur.fetchone()
            if row:
                balance = row[0]
                if balance >= monto:
                    cur.execute("INSERT INTO transaccion (monto, descripcion, num_cuenta_origen, num_cuenta_destino) VALUES (%s, %s, %s, %s)",
                    (monto, descripcion, cta_origen, cta_destino))
                    cur.execute("UPDATE cuenta SET saldo=saldo+%s WHERE numero_cuenta=%s", (monto, cta_destino))
                    cur.execute("UPDATE cuenta SET saldo=saldo-%s WHERE numero_cuenta=%s", (monto, cta_origen))
                    conn.commit()
                    self.cerrar_conexion(cur,conn)
                    return True
                else:
                    return False
        except Exception as e:
            print(e)
            conn.rollback()
            self.cerrar_conexion(cur,conn)
            return None
            
    def check_account_owner(self, numero_cuenta, id_beneficiario):
        conn, cur = ATM.get_connection()
        cur.execute("SELECT usuario.id_documento, usuario.nombre, cuenta.numero_cuenta FROM cuenta INNER JOIN usuario ON cuenta.id_beneficiario=usuario.id_documento WHERE cuenta.numero_cuenta=%s AND cuenta.id_beneficiario=%s", (numero_cuenta, id_beneficiario))
        row = cur.fetchone()
        self.cerrar_conexion(cur, conn)
        if row:
            return row
        else:
            return None
            
    def deposit(self, numero_cuenta, monto):
        conn, cur = ATM.get_connection()
        try:
            cur.execute("UPDATE cuenta SET saldo=saldo+%s WHERE numero_cuenta=%s", (monto, numero_cuenta))
            conn.commit()
            self.cerrar_conexion(cur, conn)
            return True
        except Exception as e:
            print(e)
            conn.rollback()
            self.cerrar_conexion(cur, conn)
            return False
        
    def crear_cuenta(self,id_beneficiario,monto_inicial):
        conn, cur = ATM.get_connection()
        try:
            num_cuenta = str(random.randint(10000, 99999))
            cur.execute("INSERT INTO cuenta (numero_cuenta, saldo, id_beneficiario) VALUES(%s, %s, %s)", (num_cuenta,float(monto_inicial),id_beneficiario))
            conn.commit()
            self.cerrar_conexion(cur,conn)
            return num_cuenta
        except Exception as e:
            print(e)
            conn.rollback()
            self.cerrar_conexion(cur,conn)
            return None
        
    def registrar(self, id_documento, nombre, usuario, contrasena):
        conn, cur = ATM.get_connection()
        try:
            cur.execute("INSERT INTO usuario (id_documento, nombre, usuario, contrasena) VALUES (%s, %s, %s, %s)", (id_documento, nombre, usuario, contrasena))
            conn.commit
            self.cerrar_conexion(cur,conn)
            return True
        except Exception as e:
            print(e)
            conn.rollback()
            self.cerrar_conexion(cur,conn)
            return False
            
    def get_user_accounts(self, id_beneficiario):
        conn, cur = ATM.get_connection()
        cur.execute("SELECT numero_cuenta,saldo FROM cuenta WHERE id_beneficiario=%s", (id_beneficiario,))
        rows = cur.fetchall()
        self.cerrar_conexion(cur, conn)
        if rows:
            return [row[0] for row in rows]
        else:
            return None

# crear instancia de la clase ATM que deseas registrar como objeto remoto
atm = ATM()

# registrar el objeto remoto con el servidor de nombres Pyro4
daemon = Pyro4.Daemon()
uri = daemon.register(atm)
ns = Pyro4.locateNS()
ns.register("atm", uri)

# iniciar el servidor para aceptar solicitudes de los clientes
print("ATM server ready.")
daemon.requestLoop()