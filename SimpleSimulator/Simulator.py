import sys

def getup(value, bit_len):
    value = str(int(value))
    while len(value)<bit_len:
        value = '0' + value
    if len(value)>bit_len:
        value = value[-bit_len:]
    return value
def deci_to_us(value, bit_len):
    #function to convert decimal value to unsigned binary
    return format(int(value), f'{bit_len}b')[-int(bit_len):]

def us_to_deci(value):
    #function to convert unsigned binary to decimal value
    return int(str(value),2)

def deci_to_tc(value, bit_len):
    #function to convert decimal value to two's complement representation
    value = int(value)
    if value < 0:
        us = (1 << int(bit_len)) + value
        biy = deci_to_us(us, bit_len)
    else:
        biy = deci_to_us(value, bit_len)
    return biy

def tc_to_deci(value):
    #function to convert two's complement representation to decimal value
    value = str(value)
    bit_len = len(value)
    if value[0] == '1':
        max_value = 2**(bit_len-1)
        deci = -(max_value - us_to_deci(str(value)[1:]))
    else:
        deci = us_to_deci(value)
    return deci

def desplay_pc():
    global program_counter
    #two's complement representation of program counter
    return '0b' + deci_to_tc(program_counter, '032')

def desplay_reg():
    global register_val
    #two's complement representation of register values
    max_value = (1 << 32) - 1
    binary_strings = ['0b' + deci_to_tc(value, '032') for value in register_val.values()]
    return ' '.join(binary_strings)

def desplay_memo():
    global memory
    #two's complement representation of memory values
    max_value = (1 << 32) - 1
    addres = 65536
    binary_strings = []
    for value in memory:
        hexa_addres = f"{addres:#0{10}x}"
        binary_strings.append(f'{hexa_addres}:0b' + deci_to_tc(value, '032'))
        addres += 4
    return '\n'.join(binary_strings)

def r_type_instruction(instruction):
    global register_val
    rd = instruction[-12:-7]
    funct3 = instruction[-15:-12]
    rs1 = instruction[-20:-15]
    rs2 = instruction[-25:-20]
    funct7 = instruction[-32:-25]

    if funct7 == '0100000':  # sub
        register_val[rd] = register_val[rs1] - register_val[rs2]
    elif funct3 == '000':  # add
        register_val[rd] = register_val[rs1] + register_val[rs2]
    elif funct3 == '001':  #sll
        register_val[rd] = register_val[rs1] << us_to_deci(deci_to_tc(register_val[rs2],'005'))
    elif funct3 == '010':  #stl
        if register_val[rs1] < register_val[rs2]:
            register_val[rd] = 1
    elif funct3 == '011':  #stlu
        if us_to_deci(deci_to_tc(register_val[rs1],'032')) < us_to_deci(deci_to_tc(register_val[rs2],'032')):
            register_val[rd] = 1
    elif funct3 == '100':  #xor
        register_val[rd] = register_val[rs1] ^ register_val[rs2]
    elif funct3 == '101':  #srl
        register_val[rd] = register_val[rs1] >> us_to_deci(deci_to_tc(register_val[rs2],'005'))
    elif funct3 == '110':  #or
        register_val[rd] = register_val[rs1] | register_val[rs2]
    elif funct3 == '111':  #and
        register_val[rd] = register_val[rs1] & register_val[rs2]

def i_type_instruction(instruction):
    global register_val, program_counter, memory
    opcode = instruction[-7:]
    rd = instruction[-12:-7]
    funct3 = instruction[-15:-12]
    rs = instruction[-20:-15]
    imm = instruction[-32:-20]

    if opcode=="0000011":  #lw
        register_val[rd] = memory[int(((register_val[rs] + tc_to_deci(imm))-65536)//4)]

    elif opcode=="0010011":
        if funct3=="000":  #addi
            register_val[rd] = register_val[rs] + tc_to_deci(imm)

        elif funct3=="011":  #sltiu
            if deci_to_us(register_val[rs]) < deci_to_us(imm):
                register_val[rd] = 1.
            else:
                register_val[rd]=0

    elif opcode=="1100111":  #jalr
        register_val[rd] = program_counter+4
        program_counter = register_val[rs] + tc_to_deci(imm)

def s_type_instruction(instruction):
    global register_val, memory
    imm = instruction[-32:-25]+instruction[-12:-7]
    rs1 = instruction[-20:-15]
    rs2 = instruction[-25:-20] 
    # with open(write_filepath,'w') as f:
    #     f.write(f'{register_val[rs1]=}{tc_to_deci(imm)=} 65536 4)')
    memory[int(((register_val[rs1]+tc_to_deci(imm))-65536)//4)]=register_val[rs2]

def b_type_instruction(instruction):
    # 0000000 10010 00000 000 10000 1111111
    # 0000000 00000 00000 000 00000
    global register_val, program_counter
    imm = instruction[-32] + instruction[-8] + instruction[-31:-25] + instruction[-12:-8]
    rs2 = instruction[-25:-20]
    rs1 = instruction[-20:-15]
    funct3 = instruction[-15:-12]

    if(funct3=="000"): #beq
        if(register_val[rs1] == register_val[rs2]):
            program_counter += tc_to_deci(imm+'0') - 4
    elif(funct3=="001"): #bne
        if(register_val[rs1] != register_val[rs2]):
            program_counter += tc_to_deci(imm+'0') - 4
    elif(funct3=="100"): #blt
        if(register_val[rs1] < register_val[rs2]):
            program_counter += tc_to_deci(imm+'0') - 4
    elif(funct3=="101"): #bge
        if(register_val[rs1] >= register_val[rs2]):
            program_counter += tc_to_deci(imm+'0') - 4
    elif(funct3=="110"): #bltu
        if(us_to_deci(deci_to_tc(register_val[rs1], "032")) < us_to_deci(deci_to_tc(register_val[rs2], "032"))):
            program_counter += tc_to_deci(imm+'0') - 4
    elif(funct3=="111"): #bgeu
        if(us_to_deci(deci_to_tc(register_val[rs1], "032")) >= us_to_deci(deci_to_tc(register_val[rs2], "032"))):
            program_counter += tc_to_deci(imm+'0') - 4

def u_type_instruction(instruction):
    global register_val, program_counter
    rd = instruction[-12:-7]
    imm = getup(instruction[-32:-12] + '000000000000',20)
    opcode = instruction[-7:]

    if(opcode=="0110111"):  #lui
        register_val[rd] = tc_to_deci(imm)
    elif(opcode=="0010111"):  #aupic
        register_val[rd] = tc_to_deci(deci_to_tc((program_counter + tc_to_deci(imm)-4),'021'))

def j_type_instruction(instruction):
    global register_val, program_counter
    rd = instruction[-12:-7]
    imm = instruction[-32] + instruction[-20:-12] + instruction[-21] + instruction[-31:-21]

    register_val[rd] = program_counter
    program_counter += tc_to_deci(imm+'0') -4

def bonus_0r_type_instruction(instruction):
    global register_val
    for key in register_val:
        register_val[key] = 0
    register_val['00010'] = 256

def bonus_2r_type_instruction(instruction):
    global register_val
    rs1 = deci_to_tc(register_val[instruction[-20:-15]], '032')
    register_val[instruction[-12:-7]] = tc_to_deci(rs1[::-1])

def bonus_3r_type_instruction(instruction):
    global register_val
    rs1 = register_val[instruction[-20:-15]]
    rs2 = register_val[instruction[-25:-20]]
    register_val[instruction[-12:-7]] = rs1*rs2

def main(read_filepath, write_filepath):
    global register_val, program_counter, memory
    register_val = {
    '00000': 0,
    '00001': 0,
    '00010': 256,
    '00011': 0,
    '00100': 0,
    '00101': 0,
    '00110': 0,
    '00111': 0,
    '01000': 0,
    '01001': 0,
    '01010': 0,
    '01011': 0,
    '01100': 0,
    '01101': 0,
    '01110': 0,
    '01111': 0,
    '10000': 0,
    '10001': 0,
    '10010': 0,
    '10011': 0,
    '10100': 0,
    '10101': 0,
    '10110': 0,
    '10111': 0,
    '11000': 0,
    '11001': 0,
    '11010': 0,
    '11011': 0,
    '11100': 0,
    '11101': 0,
    '11110': 0,
    '11111': 0
    }

    memory = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

    program_counter = 4

    with open(read_filepath, 'r') as file:
        BIN = ['/n']
        for line in file.readlines():
            BIN.append('\n')
            BIN.append('\n')
            BIN.append('\n')
            BIN.append(line.rstrip('\n'))

    simulator = []
    R_TYPE = ['0110011']
    I_TYPE = ['0000011', '0010011', '1100111']
    S_TYPE = ['0100011']
    B_TYPE = ['1100011']
    U_TYPE = ['0110111', '0010111']
    J_TYPE = ['1101111']
    BONUS_3R_TYPE = ['0101010']
    BONUS_2R_TYPE = ['1010101']
    BONUS_0R_TYPE = ['0000000']
    while True:
        register_val['00000'] = 0
        if (BIN[program_counter]) in ['\n','',' ']:
            program_counter +=1
            continue
        elif (BIN[program_counter])[-7:]=='1111111' or BIN[program_counter] == '00000000000000000000000001100011':  # halt
            break
        elif (BIN[program_counter])[-7:] in R_TYPE:
            r_type_instruction(BIN[program_counter])
        elif (BIN[program_counter])[-7:] in I_TYPE:
            i_type_instruction(BIN[program_counter])
        elif (BIN[program_counter])[-7:] in S_TYPE:
            s_type_instruction(BIN[program_counter])
        elif (BIN[program_counter])[-7:] in B_TYPE:
            b_type_instruction(BIN[program_counter])
        elif (BIN[program_counter])[-7:] in U_TYPE:
            u_type_instruction(BIN[program_counter])
        elif (BIN[program_counter])[-7:] in J_TYPE:
            j_type_instruction(BIN[program_counter])
        elif (BIN[program_counter])[-7:] in BONUS_0R_TYPE:
            bonus_0r_type_instruction(BIN[program_counter])
        elif (BIN[program_counter])[-7:] in BONUS_2R_TYPE:
            bonus_2r_type_instruction(BIN[program_counter])
        elif (BIN[program_counter])[-7:] in BONUS_3R_TYPE:
            bonus_3r_type_instruction(BIN[program_counter])
        else:
            simulator.append(f'ERROR: Incorrect Instruction "{BIN[program_counter][-7:]}" at program_counter {program_counter} ({"".join(BIN[program_counter])})')
            break
        register_val['00000'] = 0
        simulator.append(f'{desplay_pc()} {desplay_reg()}')
        program_counter+=4
        if program_counter//4>(len(BIN)-2):
            if '00000000000000000000000001111111' in BIN or '00000000000000000000000001100011' in BIN:
                simulator.append('ERROR: Vertual hault not at end')
            else:
                simulator.append('ERROR: Vertual hault not present')
            break
    program_counter-=4
    simulator.append(f'{desplay_pc()} {desplay_reg()}')
    simulator.append(f'{desplay_memo()}')
    with open(write_filepath, 'w') as file:
        for i in simulator:
            if i[0] == 'E':
                file.seek(0)
                file.truncate(0)
                file.write(str(i))
                return
            file.write(str(i))
            file.write('\n')

read_filepath = sys.argv[1]
write_filepath = sys.argv[2]

# read_filepath = 'automatedTesting/tests/bin/simple/s_test4.txt'
# write_filepath = 'automatedTesting/tests/user_traces/simple/s_test4.txt'
main(read_filepath, write_filepath)
