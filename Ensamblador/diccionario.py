def crear_diccionario(ins : list, codes : list):
    diccionario = {}
    for i in ins:
        instruccion = i.split(" ")
        if len(instruccion) > 1:
            generador = instruccion[1].split(";")
            codigos = codes.pop(0)
            dic_sec = {}
            for j in generador:
                elemento = {j : codigos.pop(0)}
                dic_sec.update(elemento)
            agregar = {instruccion[0] : dic_sec}
            diccionario.update(agregar)
    diccionario.update({'RET' : '00000000010100100'})
    diccionario.update({'NOP' : '000000000000000000000000000000000000'})
    
    return diccionario