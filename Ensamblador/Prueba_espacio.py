data = ["v1 10 // 10 se asume decimal",
"v2 10d // 10 en decimal",
"v3 10b // 10 en binario",
"v4 10h // 16 en hexadecima"]

ins = []

for i in data:
    if "//" in i:
        pos = i.find("//")
        i = i[:pos]
    ins.append(i.strip(" "))

code = ["MOV B, ( v4 ) // B = Mem[3] = 16",
"MOV A, ( 10b ) // A = Mem[2] = 2",
"label1:",
"MOV (v1),B // Mem[0] = 16",
"JMP label2"]

new_code = []

for i in code:
    if "//" in i:
        pos = i.find("//")
        i = i[:pos]
        i.strip(" ")
    if i.count(" ") > 1:
        principal = i.find(" ")
        p_1 = i[:principal+1]
        p_2 = i[principal + 1:].replace(" ", "")
        i = p_1 + p_2
    new_code.append(i)

print(new_code)



print(ins)