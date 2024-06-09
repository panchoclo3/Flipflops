
def limpiar(linea, seccion):
    if linea.find("//"):  # Si hay un comentario
        linea = (linea.split("//"))[0]  # deja el texto antes del comentario

    # Elimina los saltos de linea y espacios al inicio y final
    linea = linea.strip("\n").strip(" ")

    # eliminar espacio si seccion distinta a DATA (espacios utiles)... REVISAR
    if seccion != 1:
        # reemplaza todos los espacios por nada. elimina espacios
        linea = linea.replace(" ", "")
    return linea


def get_bytearray(instruccion):  # instruccion es un string de 0´s y 1´s de largo
    # Se interpreta toda la instruccion como un numero entero
    inst_to_int = int(instruccion, 2)
    # Se interpreta el numero en 5 bytes, es importante que sea de este largo
    inst_to_bytes = inst_to_int.to_bytes(5, "big")
    return bytearray(inst_to_bytes)  # Se crea un bytearray de la instruccion


def int_to_16bits(entero):
    if entero >= 2**16:
        print("valor por sobre espacio de memoria")
    # numero binario de 16 bits. rellenado con 0 en bits sobrantes
    return format(entero, '016b')


# valor es un string. Solo recibe numeros-no variables
def get_binary_16(valor, incremento):
    # binario (b), decimal (d) y hexadecimal (h). si no hay nada se asume decimal
    binary = ""
    if valor[-1] == "h":
        valor = valor[:-1]
        int_hex = int(valor, 16)
        binary = bin(int_hex)
        return ("0"*(16 - len(binary))) + binary

    elif valor[-1] == "b":
        valor = valor[:-1]
        # para que secuencia sea de 16 bits
        return ("0"*(16 - len(valor))) + valor

    elif valor[-1] == "d":
        valor = valor[:-1]  # elimina d
    valor = int(valor) + incremento
    binary = int_to_16bits(valor)
    return binary
