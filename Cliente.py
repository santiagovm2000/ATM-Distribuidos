import Pyro4
from datetime import datetime

atm = Pyro4.Proxy("PYRONAME:atm")

def show_menu():
    print("\n")
    print("Bienvenido a Mini-Banco - ATM")
    print("1. Apertura de cuenta")
    print("2. Realizar transacción")
    print("0. Salir")

def show_transaction_menu():
    print("\n")
    print("Realizar transacción")
    print("1. Consulta de cuenta")
    print("2. Depósito a cuenta")
    print("3. Retiro de cuenta")
    print("4. Transferencia entre cuentas")
    print("0. Volver")
    
def run_transaction_menu():
    id_documento = autenticar()
    if id_documento:
        while True:
            show_transaction_menu()
            transaction_choice = input("Ingrese opción: ")
            if transaction_choice == "1":
                check_accounts(id_documento)
                break
            elif transaction_choice == "2":
                deposit(id_documento)
                break
            elif transaction_choice == "3":
                withdraw(id_documento)
                break
            elif transaction_choice == "4":
                transaction(id_documento)
                break
            elif transaction_choice == "0":
                break
            else:
                print("Opción inválida.")
    else:
        print("Error de autenticación.")

def autenticar():
    print("\n")
    print("Proceso de autenticación")
    usuario = input("Ingrese nombre de usuario: ")
    contrasena = input("Ingrese contraseña: ")
    return atm.autenticar(usuario, contrasena)

def account_options(cuentas, show_third_party_option):
    print("Cuentas del cliente:")
    for i, cuenta in enumerate(cuentas):
        print(f"{i+1}.- Nro. Cuenta: {cuenta}")
    if show_third_party_option:
        print("X.- Depositar en una cuenta de terceros")
    opcion_acc_number = input("Ingrese la opción asociada al número de cuenta: ")
    opcion_acc_number = opcion_acc_number.upper()
    if opcion_acc_number == "X" and show_third_party_option:
        return "terceros"
    opcion_acc_number = int(opcion_acc_number)-1
    if opcion_acc_number < 0 or opcion_acc_number >= len(cuentas):
        print("Opción inválida.")
        return None
    else:
        return cuentas[opcion_acc_number]
        
def transaction(id_documento):
    cuentas = atm.get_user_accounts(id_documento)
    if cuentas:
        print("\n")
        print("Seleccione la cuenta de origen: ")
        cuenta_seleccionada_origen = account_options(cuentas, False)
        if cuenta_seleccionada_origen is not None:
            cuentas.remove(cuenta_seleccionada_origen)
            print("\n")
            print("Seleccione la cuenta destino:")
            cuenta_seleccionada_destino = account_options(cuentas, True)
            if cuenta_seleccionada_destino is not None:
                monto = float(input("Ingrese monto: "))
                descripcion = input("Ingrese una descripcion: ")
                if cuenta_seleccionada_destino != "terceros":
                    response =confirm_dialog(f"Esta seguro de que desea tranferir {monto}$ desde Nro. Cta. {cuenta_seleccionada_origen} al Nro cuenta: {cuenta_seleccionada_destino}")
                    if response:
                        execute_transaction(cuenta_seleccionada_origen,cuenta_seleccionada_destino,monto,descripcion)
                        balance = atm.get_balance(cuenta_seleccionada_origen)
                        print("Saldo de cuenta Nro. " + cuenta_seleccionada_origen + ": " + str(balance) + "$")
                    else:
                        return
                else:
                    num_cuenta = input("Ingrese el número de cuenta destino: ")
                    id_documento_dest = input("Ingrese el documento de identidad asociado: ")
                    info_cuenta_dest = atm.check_account_owner(num_cuenta,id_documento_dest)
                    if info_cuenta_dest:
                        response =confirm_dialog(f"Esta seguro de que desea transferir {monto}$ desde Nro. Cta. {cuenta_seleccionada_origen} a:\nDocumento identidad: {info_cuenta_dest[0]}\nNombre titular: {info_cuenta_dest[1]}\nNro cuenta: {info_cuenta_dest[2]}")
                        if response:
                            execute_transaction(cuenta_seleccionada_origen,info_cuenta_dest[2],monto,descripcion)
                            balance = atm.get_balance(cuenta_seleccionada_origen)
                            print("Saldo de cuenta Nro. " + cuenta_seleccionada_origen + ": " + str(balance) + "$")
                        else:
                            return
                    else:
                        print("No existe cuenta con el documento de identidad y el Nro. cuenta dado.")
                        return
            

def check_accounts(id_documento):
    cuentas = atm.get_user_accounts(id_documento)
    if cuentas:
        print("\n")
        cuenta_seleccionada = account_options(cuentas, False)
        if cuenta_seleccionada is not None:
            check_balance(cuenta_seleccionada)
    else:
        print("No se encontraron cuentas para el usuario.")

def deposit(id_documento):
    cuentas = atm.get_user_accounts(id_documento)
    if cuentas:
        print("\n")
        cuenta_seleccionada = account_options(cuentas, True)
        if cuenta_seleccionada is not None:
            monto = input("Ingrese el monto: ")
            if cuenta_seleccionada != "terceros":
                response =confirm_dialog(f"Esta seguro de que desea depositar {monto}$ al Nro cuenta: {cuenta_seleccionada}")
                if response:
                    deposito = atm.deposit(cuenta_seleccionada,monto)
                else:
                    return
            else:
                num_cuenta = input("Ingrese el número de cuenta destino: ")
                id_documento_dest = input("Ingrese el documento de identidad asociado: ")
                info_cuenta_dest = atm.check_account_owner(num_cuenta,id_documento_dest)
                if info_cuenta_dest:
                    response =confirm_dialog(f"Esta seguro de que desea depositar {monto}$ a:\nDocumento identidad: {info_cuenta_dest[0]}\nNombre titular: {info_cuenta_dest[1]}\nNro cuenta: {info_cuenta_dest[2]}")
                    if response:
                        deposito = atm.deposit(info_cuenta_dest[2],monto)
                    else:
                        return
                else:
                    print("No existe cuenta con el documento de identidad y el Nro. cuenta dado.")
                    return
            if (deposito):
                print("\nDepósito exitoso")
                if cuenta_seleccionada != "terceros":
                    balance = atm.get_balance(cuenta_seleccionada)
                    print("Saldo de cuenta Nro. " + cuenta_seleccionada + ": " + str(balance) + "$")
            else:
                print("\nDepósito fallido")
    else:
        print("No se encontraron cuentas para el usuario.")
    
def confirm_dialog(mensaje):
    while True:
        print("\n")
        print(mensaje)
        print("1. Sí")
        print("2. No")
        choice = input("Ingrese opción: ")
        if choice == "1":
            return True
        elif choice == "2":
            return False
        else:
            print("Opción inválida. Por favor, seleccione 1 o 2.")
        
def execute_transaction(cta_origen,cta_destino,monto,descripcion):
    if atm.transaction(cta_origen,cta_destino,monto,descripcion):
        print("Transacción exitosa.")
    else:
        print("Transacción fallida.")

def abrir_cuenta():
    id_documento = input("Ingrese número de documento de identidad: ")
    if atm.user_exist(id_documento):
        if atm.num_cuentas(id_documento) >= 3:
            print("Ha alcanzado el límite máximo de cuentas permitido")
        else:
            if autenticar():
                monto_inicial = input("Ingrese monto inicial: ")
                num_cuenta = atm.crear_cuenta(id_documento, monto_inicial)
                if num_cuenta is None:
                    print('Error al abrir cuenta')
                else:
                    print('Cuenta creada exitosamente, su número es ', num_cuenta)
            else:
                print("Error de autenticación")
    else:
        print("Usuario no encontrado, debe registrarse")
        nombre = input("Ingrese su nombre: ")
        usuario = input("Ingrese nombre de usuario: ")
        contrasena = input("Ingrese contraseña: ")
        result = atm.registrar(id_documento, nombre, usuario, contrasena)
        if result:
            print("Cuenta creada exitosamente.")
        else:
            print("Error al crear cuenta.")

def check_balance(account_number):
    print("\n")
    balance = atm.get_balance(account_number)
    print("Saldo de cuenta Nro. " + account_number + ": " + str(balance) + "$")
    transactions = atm.get_transactions(account_number)
    if transactions:
        print("Ultimas 5 transacciones:")
        for i, transaction in enumerate(transactions):
            fecha_str, monto, descripcion, cuenta_destino = transaction
            fecha = datetime.strptime(fecha_str, "%Y-%m-%dT%H:%M:%S.%f")
            fecha_str = fecha.strftime("%d/%m/%Y %I:%M:%S %p")  # Convertir fecha a string
            print(f"{i+1}. Fecha: {fecha_str}    Monto: {monto}    Descripción: {descripcion}    Nro. Cta. Destino: {cuenta_destino}")

def withdraw(id_documento):
    cuentas = atm.get_user_accounts(id_documento)
    if cuentas:
        print("\n")
        cuenta_seleccionada = account_options(cuentas, False)
        if cuenta_seleccionada is not None:
            monto = float(input("Ingrese monto: "))
            result = atm.withdraw(cuenta_seleccionada, monto)
            if result:
                print("Retiro exitoso.")
                balance = atm.get_balance(cuenta_seleccionada)
                print("Saldo de cuenta Nro. " + cuenta_seleccionada + ": " + str(balance) + "$")
            else:
                print("Retiro fallido. Saldo insuficiente.")

def run():
    while True:
        show_menu()
        choice = input("Ingrese opción: ")
        if choice == "1":
            abrir_cuenta()
        elif choice == "2":
            run_transaction_menu()
        elif choice == "0":
            print("\n Hasta luego.")
            break
        else:
            print("Opción inválida.")

if __name__ == "__main__":
    run()