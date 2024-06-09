# REVISAR: funcion limpiar. hay que eliminar /n, entre otros detalles.
# Terminar diccionario de opcodes
# Pasar de base 10(d o nada al final) a binario(b al final) o hexagesimal(h)
# ejecución mediante a: python3 assembler.py code.txt
import re  # Para comparar string entregado con esperados
import sys
from opcodes import opcodes_alt
from funciones import limpiar, get_bytearray, get_binary_16
# Dict, relaciona instruccion en assembly(llave) a su secuencia binaria(valor) de acuerdo al opcode
from iic2343 import Basys3


def save_data(diccionario, line):  # Guardar variables
    line = line.split(" ")
    diccionario[line[0]] = line[1]
    return diccionario


def operation(labels, line):  # opcode(36 bits) = literal(16 bits) + operacion(20 bits)
    operacion = "0"*20  # 20 bits
    # 16 bits menos significativos. por estandar es 0 si no se especifica otra cosa
    literal = "0"*16
    # si se ocupa como direccion se toman encuenta los 12 menos significativo

    for instruccion in opcodes_alt:  # entrega secuencia de 20 bits si coincide
        pattern = re.compile(instruccion)
        if pattern.match(line):  # instrucciones que reciben siempre un solo valor
            operacion = (opcodes_alt[instruccion]).replace(
                " ", "")  # Entrega secuencia binaria
            if instruccion.startswith("OR"):
                # Elimina instruccion. OR es la unica de largo 2
                line = line[2:]
            elif (instruccion.startswith("CALL") or instruccion.startswith("PUSH")):
                line = line[4:]  # CALL Y PULL son intrucciones de 4 caracteres

            elif instruccion.startswith("POP") or instruccion == "RET":
                operacion = operacion.split("-")  # arreglo de 2 operaciones
                for i in range(0, 2):
                    operacion[i] = literal + operacion[i]
                return operacion

            else:
                # print(line)
                line = line[3:]
                # print(line)

            if "," in line:
                line = line.split(",")  # Deja uno o dos valores
            else:
                line = [line]
            for valor in line:
                # Si hay una direccion de memoria o un literal
                if (valor not in ["A", "B", "(B)"]) and (valor != ""):
                    # print(valor)
                    # Se eliminan los parentesis si es una direccion
                    if valor.startswith("("):
                        valor = valor[1:-1]

                    if (valor in labels):  # ETAPA 2. camba lavels y variables por su valor
                        valor = labels[valor]
                    literal = get_binary_16(valor, 0)

            if instruccion[:3] in ("JMP", "JEQ", "JNE", "JGT", "JGE", "JLT", "JLE", "JCR"):
                literal = get_binary_16(valor, 1)

            if instruccion == "INCA" or instruccion == "DECA":
                literal = get_binary_16("1", 0)  # INCA incluye un literal 1
            # primeros 16 de literal, 20 bits despues de operacion
            return [literal + operacion]
    return ["0"*36]  # Cuando inicio de la linea no es ninguna instruccion. ->N"OP


instance = Basys3()  # Se crea la instancia de la Basys3
# Puede ser que deban elegir otro puerto si no les conecta
# Pueden intentar cambiando el numero de puerto del 0-2
instance.begin(2)

# Obtiene el nombre del txt con informacion en assembly que se va a leer.
path = sys.argv[1]
file = open(path, "r")  # Abre archivo para lectura

labels = dict()
# 2 lecturas del codigo. una para obtener labels y otra para variables y traduccion assembly.
# Encargado de tomar todas las labels de la sección code
seccion = 0
# parte de 1 ya que intrucciones dadas por usuario parten en 1. posicion 0 para SSP.
indice = 1
for line in file:
    clean = limpiar(line, seccion)
    if clean == "CODE:":
        seccion = 2

    elif (seccion == 2):
        if (":" in clean):
            clean = clean.split(":")[0]
            labels[clean] = str(indice + 1)
        if clean != "":
            indice += 1


# Se reinicia el valor de indice y seccion y se hace una segunda pasada.
seccion = 0  # indica en que sección se esta. determina que se hace
sec = ""  # Secuencia en binario
# para CODE. indica direccion de la instruccion (address in the ROM)
indice = 0
# Se ejecuta la primera intruccion para setear SP.
# unico elemento del arreglo que retorna operacion
sec = (operation(labels, "SSP"))[0]
instance.write(indice, get_bytearray(sec))
indice += 1

file.close()
file = open(path, 'r')

for line in file:  # Para cada linea line del archivo
    clean = limpiar(line, seccion)  # Sin comentarios o espacios
    if clean == "DATA:":
        seccion = 1

    elif clean == "CODE:":
        seccion = 2

    elif clean != "" and clean != "SSP":  # Linea limpia no esta vacia
        if seccion == 1:
            # Guarda variables en el diccionario
            labels = save_data(labels, clean)
        elif seccion == 2 and indice < 2**12:
            sec = operation(labels, clean)
            for s in sec:  # sec es un arreglo de 1 o 2 instrucciones binarias
                print(f"{s} ({clean})")
                print(f"{s[:16]} (literal)")
                # Se escribe el bytearray de la instruccion en la placa
                instance.write(indice, get_bytearray(s))
                indice += 1

# ver como esta el diccionario
print("diccionario:")
for label in labels:
    print(label, labels[label])

file.close()  # Cerrar archivo al terminar lectura
instance.end()  # Se termina la instancia de la Basys3
