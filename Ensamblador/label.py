def obtener_labels(data):
    suma = 0
    while 'CODE:' in data:
        if 'DATA' not in data[0] and 'CODE:' not in data[0]:
            suma+=2
        data.pop(0)
    print(suma)
    labels = {}
    restador = -1
    for i in range(len(data)):
        if ':' in data[i] and 'POP' not in data[i] and 'RET' not in data[i]:
            restador += 1
            valor = i - restador + suma
            labels[data[i].strip(":")] = f"{bin(valor)[2:].zfill(19)}"
        elif 'POP' in data[i] or 'RET' in data[i]:
            restador -= 1
    return labels
