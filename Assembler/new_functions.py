from opcodes import opcodes_alt
import re


def limpiar(linea):
    if linea.find("//"):  # Si hay un comentario
        linea = (linea.split("//"))[0]  # deja el texto antes del comentario

    # Elimina los saltos de linea y espacios al inicio y final
    linea = linea.strip("\n").strip(" ")
    return linea


def clean_section(program_str):
    # Limpia todas las lineas de la sección
    s = ''
    for line in program_str.split('\n'):
        clean_line = limpiar(line)
        if '//' in clean_line or clean_line == '':
            continue
        s += clean_line + '\n'
    return s.strip()


def is_literal(x, variables, labels):
    # Revisa si x está en variables o labels (si es un literal)
    for variable in variables.keys():
        if x == variable:
            return False
    for label in labels.keys():
        if x == label:
            return False
    if x == 'A' or x == 'B':
        return False
    return True


def literal_to_int(literal):
    # Recibe literal y lo pasa a int, retorna el int
    # binario (b), decimal (d) y hexadecimal (h). si no hay nada se asume decimal
    if literal[-1] == "h":
        literal = literal[:-1]
        return int(literal, base=16)

    elif literal[-1] == "b":
        literal = literal[:-1]
        return int(literal, base=2)

    elif literal[-1] == "d":
        literal = literal[:-1]
        return int(literal, base=10)
    return int(literal)


def get_operands(instruction):
    # Dada una instrucicón como 'JMP loop' o 'MOV (0), A'
    # Obtiene el nombre de la operación y los operandos
    # Ejemplo
    # ret = ('NOP')
    # ret = ('JMP', 'loop')
    # ret = ('ADD', 'A', '(0)')
    if ',' in instruction:  # Hay 2 operandos separados por ,
        split_ret = instruction.split(',')
        name_op1, op2 = split_ret[0], remove_spaces(split_ret[1])
        split_ret = name_op1.split(' ', 1)
        split_ret = remove_empty(split_ret)
        name, op1 = remove_spaces(split_ret[0]), remove_spaces(split_ret[1])
        ret = [name, op1, op2]
    elif ' ' in instruction:  # Solo 1 operando
        split_ret = instruction.split(' ', 1)
        split_ret = remove_empty(split_ret)
        name, op = remove_spaces(split_ret[0]), remove_spaces(split_ret[1])
        ret = [name, op]
    else:  # Es un comando especial ####################
        ret = [instruction]

    # Remover espacios extra y elementos vacíos
    for i in range(len(ret)):
        if ret[i] == '':
            continue
        ret[i] = ret[i].replace(' ', '')
    return tuple(ret)


def remove_empty(str_list):
    # Remueve los '' de una lista de str
    ret = []
    for elem in str_list:
        if elem != '':
            ret.append(elem)
    return ret


def remove_spaces(str):
    return str.replace(' ', '')


################ COPIADO TAL CUAL ################################################
def int_to_16bits(entero):
    if entero >= 2**16:
        print("valor por sobre espacio de memoria")
    # numero binario de 16 bits. rellenado con 0 en bits sobrantes
    return format(entero, '016b')


# valor es un string. Solo recibe numeros-no variables
def get_binary_16(valor, incremento):
    # binario (b), decimal (d) y hexadecimal (h). si no hay nada se asume decimal
    valor = str(valor)  # ver porque a veces llega int-.
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
                literal = get_binary_16(valor, 0)

            if instruccion == "INCA" or instruccion == "DECA":
                literal = get_binary_16("1", 0)  # INCA incluye un literal 1
            # primeros 16 de literal, 20 bits despues de operacion
            return [literal + operacion]
    return ["0"*36]  # Cuando inicio de la linea no es ninguna instruccion. ->N"OP


def get_bytearray(instruccion):  # instruccion es un string de 0´s y 1´s de largo
    # Se interpreta toda la instruccion como un numero entero
    inst_to_int = int(instruccion, 2)
    # Se interpreta el numero en 5 bytes, es importante que sea de este largo
    inst_to_bytes = inst_to_int.to_bytes(5, "big")
    return bytearray(inst_to_bytes)  # Se crea un bytearray de la instruccion
