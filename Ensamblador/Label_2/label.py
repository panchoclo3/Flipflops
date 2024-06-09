def obtener_labels(data):
    senal_code, numero, labels = False, -1, {}
    data.remove("DATA:")
    #print("aqui comienza la asignacion")
    for instruccion in data:
        #print(instruccion)
        if instruccion == "CODE:":
            senal_code = True
        elif not senal_code:
            numero += 2
        else:
            operacion = instruccion.split(" ")
            if operacion[0] in ["POP", "RET"]:
                print(operacion)
                numero += 2
            elif ":" in operacion[0]:
                #print(f"{instruccion} caso especial")
                #print(numero)
                #print(operacion[0])
                labels.update({operacion[0].strip(":") : f"{bin(numero+1)[2:].zfill(19)}"})
                #print(operacion[0].strip(":"))
            else:
                numero += 1
    #print("aqui termina la asignacion")
    print(numero)
    return labels