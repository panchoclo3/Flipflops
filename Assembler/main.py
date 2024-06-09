from iic2343 import Basys3

# Se crea la instancia de la Basys3
instance = Basys3()

# Puede ser que deban elegir otro puerto si no les conecta
# Pueden intentar cambiando el numero de puerto del 0-2
instance.begin(port_number=1)

# Despues (a modo de ejemplo) se escribiran 0s en todas las lineas de la ROM y una instruccion a partir de un string
i = 0
while i < 2**12:
    # Opcion 1:
    instance.write(i, bytearray([0x00, 0x00, 0x00, 0x00, 0x00])) # Se puede escribir los bytes directamente

    # Opcion 2:
    inst = "111000100010011010101111010100010101"  # Tenemos la instruccion en un string
    inst_to_int = int(inst, 2) # Se interpreta toda la instruccion como un numero entero
    inst_to_bytes = inst_to_int.to_bytes(5, "big") # Se interpreta el numero en 5 bytes, es importante que sea de este largo
    instance.write(i, bytearray(inst_to_bytes)) # Se crea un bytearray de la instruccion y se escribe en la placa

    i += 1

# Se termina la instancia de la Basys3
instance.end()