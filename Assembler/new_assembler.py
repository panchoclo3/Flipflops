from new_functions import clean_section, literal_to_int, is_literal, get_operands, operation, get_bytearray
from iic2343 import Basys3
import sys


def get_sections(program, code_indicator, data_indicator):
    # Dado un str del código retorna data y code limpios
    data_str = program[program.find(
        DATA_indicator)+len(DATA_indicator):program.rfind(CODE_indicator)].strip()
    code_str = program.split(CODE_indicator, 1)[1].strip()
    data = clean_section(data_str)
    code = clean_section(code_str)
    return data, code


def get_instructions(code):
    # Se le entrega la sección con CODE y retorna lista con instrucciónes
    instructions = []
    for line in code.split('\n'):
        instructions.append(line)
    return instructions


def get_memory(data):
    # Se le entrega la sección con DATA y retorna lista de direcciones
    data_addr = []
    for line in data.split('\n'):
        if line != '':  # Por si no hay sección DATA
            data_addr.append(line)
    return data_addr


def get_labels_instructions(instructions_labels):
    # Dada una lista de instrucciones con labels, retorna un diccionario con los labels
    # y las instrucciones sin labels
    # Tener en consideración que RET y POP usan dos instrucciones
    labels = {}
    instructions = []
    PC = 0
    for instr in instructions_labels:
        if ':' in instr:  # Si es una línea de label
            instr = instr.replace(':', '')
            labels[instr] = PC
        else:
            if 'RET' in instr or 'POP' in instr:  # RET y POP valen doble
                PC += 1
            instructions.append(instr)
            PC += 1
    return labels, instructions


def get_memory_address_value(data):
    # Dada una lista de lineas de data
    # key = data_label_name    El nombre de la dirección de memoria
    # Valores (una tupla)
    # data_address = dirección en memoria
    # data_value = valor inicial en memoria en dirección
    #       #data_value es una lista con los cvalores iniciales
    #       #si tiene un elemento es el valor, si son varios es un arreglo
    # dic[key] = (data_address, data_value)
    data_dict = {}
    data_address = 0
    for data_address, data_line in enumerate(data):
        ret = data_line.split(' ')
        if len(ret) > 1:  # Es un valor asociado a una variable
            data_label_name = ret[0]
            data_value = ret[1]
            data_dict[data_label_name] = (data_address, [data_value])
        else:  # Es un valor asociado a un array
            data_value = ret[0]
            data_dict[data_label_name][1].append(data_value)
    print(data_dict)
    return data_dict


def get_initial_instructions(variables):
    # Recibe un diccionario de variables con 'nombre variable': valor variable
    # Retorna instrucciones a agregar al inicio del programa para cargar memoria
    # dic[nombre variable] = (data_address, data_value)
    instructions = []  # "SSP"

    # Cargar para variables de ARRAY que no esten en variables
    #########################################################
    #########################################################
    #########################################################

    for variable in variables.values():
        address_dir = variable[0]
        data_values = variable[1]
        for offset, data_value in enumerate(data_values):
            ins1 = f'MOV A, {data_value}'
            ins2 = f'MOV ({address_dir + offset}), A'
            instructions.append(ins1)
            instructions.append(ins2)
    return instructions


def replace_if_variables(operand, variables):
    # Revisar si corresponde a una variable como dirección o como valor
    # Mov A, (var) -> Mov A, (0)
    # Mov A, var -> Mov A, 0
    brackets = False
    operand_content = operand
    if '(' in operand or ')' in operand:
        brackets = True
        operand_content = operand[1:-1]
    # Revisar si contenido en variables si lo está, cambiamos por su dirección
    for variable in variables.keys():
        if operand_content == variable:
            data_address, _ = variables[variable]
            if brackets:
                return f'({data_address})'
            else:
                return str(data_address)
    return operand  # Si no hay variable retorna tal cual


def replace_if_labels(operand, labels):
    # Si operand está en labels la cambia por su valor en labels
    # Revisar si contenido en variables si lo está, cambiamos por su dirección
    for label in labels.keys():
        if operand == label:
            return str(labels[label])
    return operand  # Si no hay variable retorna tal cual


def convert_if_literal(operand, variables, labels, offset):
    # Recibe un operando tipo "0002b", "1000d", "1000" "(A)"  "(1d)" etc y
    # Retorna el operando con el literal a int y le suma el offset
    # Revisar dos casos (value) y value
    if '(' in operand or ')' in operand:
        # primer caso, sacamos el contenido
        operand_content = operand[1:-1]
        if is_literal(operand_content, variables, labels):
            value = literal_to_int(operand_content) + offset
            return f'({value})'  # Retorna "(value + offset)"
    elif is_literal(operand, variables, labels):
        value = literal_to_int(operand) + offset
        return str(value)
    return operand  # Si no es literal retorna tal cual


def process_instructions(instructions, variables, labels, offset):
    # recibe lista instrucciones en str que pueden contener labels,
    # variables o literales en distintas representacioens
    processed_instruction = []
    for instruction in instructions:
        ret = get_operands(instruction)
        name = ret[0]
        # print(instruction)
        if len(ret) == 1:  # Instrucción especial se deja igual
            name = ret[0]
            processed_instruction.append(name)
        if len(ret) == 2:  # Instrucción con 1 operando
            name, op = ret
            # Convierte el operando si es literal (con los JUMPS aplica)
            # Solo suma el offset a los literales si son en un jump
            # Si es jump o CALL (se pueden llamar con literales)
            if 'J' in name or 'CALL' == name:
                op = convert_if_literal(op, variables, labels, offset=offset)
            else:
                op = convert_if_literal(op, variables, labels, offset=0)
            # Reemplazar labels por su valor
            # AQUÏ
            op = replace_if_labels(op, labels)

            # Reemplazar variables por su valor
            # AquÏ
            op = replace_if_variables(op, variables)

            processed_instruction.append(f'{name}{op}')

        if len(ret) == 3:  # Instrucción con 2 operandos
            name, op1, op2 = ret
            # Convertimos todos los literales a base 10
            op1 = convert_if_literal(op1, variables, labels, offset=0)
            op2 = convert_if_literal(op2, variables, labels, offset=0)

            # Reemplalzamos variables por su valor aquí
            op1 = replace_if_variables(op1, variables)
            op2 = replace_if_variables(op2, variables)

            processed_instruction.append(f'{name}{op1},{op2}')
    return processed_instruction


def get_opcodes(code, CODE_indicator, DATA_indicator):
    # Get DATA
    data, code = get_sections(
        code, code_indicator=CODE_indicator, data_indicator=DATA_indicator)
    data_lines = get_memory(data)

    variables = get_memory_address_value(data_lines)
    # Instrucciones iniciales para cargar memoria
    initial_instructions = get_initial_instructions(variables)

    # Get CODE
    instructions_and_labels = get_instructions(code)
    total_instructions = initial_instructions + instructions_and_labels
    # Las labels ya consideran las instrucciones iniciales
    labels, instructions = get_labels_instructions(total_instructions)
    offset = len(initial_instructions)

    # Cambia variables
    # Cambia labels
    # Considera offsets y todo
    # print(variables, labels)
    opcodes = []
    processed_instructions = process_instructions(
        instructions, variables, labels, offset)
    print('\n'.join(processed_instructions))
    print(labels)

    # Hay un uso relajado de la palabra instrucción y opcode acá sori
    for instruction in processed_instructions:
        # Puede ser 1 o 2 instrucciones por opcode
        for opcode in operation(labels, instruction):
            opcodes.append(opcode)
    return opcodes


if __name__ == '__main__':
    path = sys.argv[1]
    with open(path, "r") as f:
        code = f.read()
    CODE_indicator = 'CODE:'
    DATA_indicator = 'DATA:'

    # Contiene literal + opcode
    opcodes = get_opcodes(code, CODE_indicator, DATA_indicator)
    print('\n'.join(opcodes))

    instance = Basys3()  # Se crea la instancia de la Basys3
    # Puede ser que deban elegir otro puerto si no les conecta
    # Pueden intentar cambiando el numero de puerto del 0-2
    instance.begin(3)
    for ix, opcode in enumerate(opcodes):
        instance.write(ix, get_bytearray(opcode))
    instance.end()  # Se termina la instancia de la Basys3
