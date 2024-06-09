import sys
from os import path
from iic2343 import Basys3
from diccionario import crear_diccionario
from label import obtener_labels
from lista import obtener_lista

instrucciones, codes = [], []

with open(path.join("Instrucciones.txt"), "r") as file:
    ins = file.readlines()
    for i in ins:
        instrucciones.append(i.strip())

with open(path.join("Opcodes.txt"), "r") as file:
    op = file.readlines()
    for i in op:
        lista = i.strip().split(",")
        codes.append(lista)

diccionario_nuevo = crear_diccionario(instrucciones, codes)
#print(diccionario_nuevo)
with open(path.join(sys.argv[1]), "r") as file:
    data = file.readlines()


assembly, inc_ins, variables, sin_variable = [], [], {}, 0

for i in data:
    i = i.strip()
    i = i.strip(" ")
    if "//" in i:
        #print(i)
        pos = i.find("//")
        i = i[:pos].strip(" ")
        #print(i)
    if i.count(" ") > 1:
        #print(i, len(i))
        principal = i.find(" ")
        p_1 = i[:principal+1]
        p_2 = i[principal + 1:].replace(" ", "")
        i = p_1 + p_2

    #print(i)    
    #print(len(i))
    assembly.append(i.strip())

while "" in assembly:
    assembly.remove("")

assembly_copia = assembly.copy()

labels = obtener_labels(assembly_copia)
#print(labels)
#print(labels)
data_asign = True
#print(assembly)
#for datos in assembly:
    #print(datos)

assembly.remove("DATA:")

print(len(assembly))

for datos in assembly:
    #print(datos)
    if 'CODE:' in datos:
        data_asign = False

    if data_asign:
        #print(datos)
        input = datos.split(" ")
        while " " in input:
            input.remove(" ")

        if(len(input) > 1):
            #print(input)
            var, lit = input
            opco = diccionario_nuevo['MOV']['A,Lit']
            if "d" in lit:
                lit = lit.strip("d")
            elif "b" in lit:
                lit = lit.strip("b")
                lit = int(lit, 2)
            elif "h" in lit:
                lit = lit.strip("h")
                lit = int(lit, 16)
            direct = f"{int(lit):019b}"
            inc_ins.append(opco + direct)
            opco = diccionario_nuevo['MOV']['(Dir),A']
            direct = f"{(len(variables)+sin_variable):019b}"
            inc_ins.append(opco + direct)
            variables.update({var : direct})
        else:
            lit = input[0]
            opco = diccionario_nuevo["MOV"]['A,Lit']
            if "d" in lit:
                lit = lit.strip("d")
            elif "b" in lit:
                lit = lit.strip("b")
                lit = int(lit, 2)
            elif "h" in lit:
                lit = lit.strip("h")
                lit = int(lit, 16)
            elif "\'" in lit:
                lit = lit.strip("\'")
                lit = lit.decode()
            elif "\"" in lit:
                lit = lit.strip("\'")
            #print(lit)
            direct = f"{int(lit):019b}"
            inc_ins.append(opco + direct)
            opco = diccionario_nuevo['MOV']['(Dir),A']
            direct = f"{(len(variables)+sin_variable):019b}"
            sin_variable += 1
            inc_ins.append(opco + direct)
    
    elif datos != '' and "CODE" not in datos:
        #print(datos)
        if ':' in datos and 'CODE' not in datos:
            #print(datos)
            #labels.update({datos.strip(":") : f"{(len(inc_ins) - 1):019b}"})
            pass
        else:
            try:
                operacion, parametros = datos.split(" ")
                #print(operacion)
                #print(parametros)
                #print("--------------------------------------------------")
            except ValueError:
                operacion, parametros = datos, ""
            if operacion in ["RET", "POP"]:
                inc_ins.append("00000000000000010" + f"{0:019b}")
                #print(diccionario_nuevo[operacion])
                try:
                    inc_ins.append(diccionario_nuevo[operacion] + f"{0:019b}")
                except TypeError:
                    #print("Instruccion POP")
                    #print(operacion, parametros)
                    #print(diccionario_nuevo[operacion][parametros])
                    inc_ins.append(diccionario_nuevo[operacion][parametros] + f"{0:019b}")
            elif parametros not in diccionario_nuevo[operacion]:
                #print(datos)
                lista_parametros = parametros.split(',')
                if "" not in lista_parametros and len(lista_parametros) >= 2:
                    #print(lista_parametros)
                    try:
                        parametro_1, parametro_2 = lista_parametros
                    except ValueError:
                        parametro_1, parametro_2 = lista_parametros, ""
                    if parametro_1 == 'A' or parametro_1 == 'B':
                        if "(" in parametro_2 and ")" in parametro_2:
                            pos_1, pos_2 = parametro_2.find("("), parametro_2.find(")")
                            direccion = parametro_2[pos_1 + 1: pos_2]
                            print(direccion)
                            #print(type(direccion))
                            if direccion.isnumeric() or direccion not in variables:
                                if "d" in direccion:
                                    direccion =  direccion.strip("d")
                                elif "b" in direccion:
                                    direccion = direccion.strip("b")
                                    direccion = int(direccion, 2)
                                elif "h" in parametro_2:
                                    direccion = direccion.strip("h")
                                    direccion = int(direccion, 16)
                                opco_op = diccionario_nuevo[operacion][",".join([parametro_1, "(Dir)"])]
                                direct = f"{int(direccion):019b}"
                                inc_ins.append(opco_op + direct)
                            else:
                                #key = ",".join([parametro_1, "(Dir)"])
                                opco_op = diccionario_nuevo[operacion][",".join([parametro_1, "(Dir)"])]
                                direct = variables[direccion]
                                inc_ins.append(opco_op + direct)
                        else:
                            if "d" in parametro_2:
                                parametro_2 =  parametro_2.strip("d")
                            elif "b" in parametro_2:
                                parametro_2 = parametro_2.strip("b")
                                parametro_2 = int(parametro_2, 2)
                            elif "h" in parametro_2:
                                parametro_2 = parametro_2.strip("h")
                                parametro_2 = int(parametro_2, 16)
                            try:
                                literal = int(parametro_2)
                                print(datos)
                                opco_op = diccionario_nuevo[operacion][",".join([parametro_1, "Lit"])]
                                direct = f"{literal:019b}"
                                inc_ins.append(opco_op + direct)
                            except ValueError:
                                literal = variables[parametro_2]
                                opco_op = diccionario_nuevo[operacion][",".join([parametro_1, "Lit"])]
                                direct = literal
                                inc_ins.append(opco_op + direct)
                            
                    elif parametro_2 == 'A' or parametro_2 == 'B':
                        if "(" in parametro_1 and ")" in parametro_1:
                            pos_1, pos_2 = parametro_1.find("("), parametro_1.find(")")
                            direccion = parametro_1[pos_1 + 1: pos_2]
                            #key = ",".join([parametro_1, "(Dir)"])
                            try:
                                opco_op = diccionario_nuevo[operacion][",".join(["(Dir)", parametro_2])]
                                direct = variables[direccion]
                                inc_ins.append(opco_op + direct)
                            except KeyError:
                                if "d" in direccion:
                                    direccion =  direccion.strip("d")
                                elif "b" in direccion:
                                    direccion = direccion.strip("b")
                                    direccion = int(direccion, 2)
                                elif "h" in parametro_2:
                                    direccion = direccion.strip("h")
                                    direccion = int(direccion, 16)
                                opco_op = diccionario_nuevo[operacion][",".join(["(Dir)", parametro_2])]
                                literal_error = int(direccion)
                                direct = f"{literal_error:019b}"
                                inc_ins.append(opco_op + direct)
                        else:
                            if "d" in parametro_1:
                                parametro_1 = parametro_1.strip("d")
                            elif "b" in parametro_1:
                                parametro_1 = parametro_1.strip("b")
                                parametro_1 = int(parametro_1, 2)
                            elif "h" in parametro_1:
                                parametro_1 = parametro_1.strip("h")
                                parametro_1 = int(parametro_1, 16)
                            literal = int(parametro_1)
                            opco_op = diccionario_nuevo[operacion][",".join([parametro_2, "Lit"])]
                            direct = f"{literal:019b}"
                            inc_ins.append(opco_op + direct)
                    elif parametro_1 == "(B)" and parametro_2 not in variables:
                        opcode = diccionario_nuevo[operacion]["(B),Lit"]
                        if "d" in parametro_2:
                            parametro_2 = parametro_2.strip("d")
                        elif "b" in parametro_2:
                            parametro_2 = parametro_2.strip("b")
                            parametro_2 = int(parametro_2, 2)
                        elif "h" in parametro_2:
                            parametro_2 = parametro_2.strip("h")
                            parametro_2 = int(parametro_2, 16)
                        print(datos)
                        literal = int(parametro_2)
                        direct = f"{literal:019b}"
                        inc_ins.append(opcode + direct)
                    elif parametro_1 == "(B)" and parametro_2 in variables:
                        opcodo = diccionario_nuevo[operacion]["(B),Lit"]
                        direct = variables[parametro_2]
                        inc_ins.append(opcodo + direct)
                else:
                    #print(lista_parametros)
                    #print(datos)
                    parametro_unit = lista_parametros[0]
                    if parametro_unit in diccionario_nuevo[operacion]:
                        opco_op = diccionario_nuevo[operacion][parametro_unit]
                        fill_up = f"{literal:019b}"
                        inc_ins.append(opco_op + fill_up)
                    else:
                        #print(parametro_unit)
                        if "(" in parametro_unit and ")" in parametro_unit:
                            pos_1, pos_2 = parametro_unit.find("("), parametro_unit.find(")")
                            direccion = parametro_unit[pos_1 + 1 : pos_2]
                            opco_op = diccionario_nuevo[operacion]["(Dir)"]
                            try:
                                fill_up = variables[direccion]
                            except KeyError:
                                literal_error = int(direccion)
                                fill_up = f"{literal_error:019b}"
                            inc_ins.append(opco_op + fill_up)
                        elif parametro_unit in labels:
                            opco_op = diccionario_nuevo[operacion]["Ins"]
                            fill_up = labels[parametro_unit]
                            inc_ins.append(opco_op + fill_up)
                        
            else:
                if operacion in ["INC", "DEC"] and parametros == "A":
                    opco_op = diccionario_nuevo[operacion][parametros]
                    fill = f"{1:019b}"
                    inc_ins.append(opco_op + fill)
                elif operacion == "NOP":
                    inc_ins.append(diccionario_nuevo["NOP"])
                else:
                    #print(datos)
                    opco_op = diccionario_nuevo[operacion][parametros]
                    fill = f"{0:019b}"
                    inc_ins.append(opco_op + fill)
            #print("--------------------------")
            #print(datos)

print(variables)
contador = 0
for i in inc_ins:
    print(contador)
    print(i)
    contador += 1

rom_programmer = Basys3()

rom_programmer.begin()

#print(len(inc_ins))

print(len(inc_ins))

for i in range(len(inc_ins)):
    #print(i)
    rom_programmer.write(i, obtener_lista(inc_ins[i]))
    #print(i, obtener_lista(inc_ins[i]))

rom_programmer.end()