def obtener_lista(valor):
    valor_entero = int(valor, 2)

    valor_bytes = valor_entero.to_bytes(5, "big")

    lista_enteros = []
    #print(valor_bytes)

    for i in valor_bytes:
        lista_enteros.append(i)

    return bytearray(lista_enteros)
    #return bytearray([int(valor[:4], 2), int(valor[4:12], 2), int(valor[12:20], 2), int(valor[20:28], 2), int(valor[28:36], 2)])

