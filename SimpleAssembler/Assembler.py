import sys

def check_reg_name(reg,register_map):
    if reg in register_map:
        return True
    return "Invalid register name: "+reg

def isNewLabel(instruction,labels):
    global program_counter
    if instruction.endswith(':') and instruction not in labels:
        labels[instruction[:-1]] = program_counter*4
        return True
    return False

def label_to_bin(label,num_bits,labels):
    if label in labels:
        global program_counter
        offset = labels[label] - program_counter*4
        return deci_to_bin(offset,num_bits)
    return deci_to_bin(label,num_bits)

def deci_to_bin(deci,num_bits):
    deci = int(deci)
    if deci < 0:
        us_biy = (1 << num_bits) + deci
        biy = bin(us_biy)[2:] #conversion to binary
    else:
        biy = bin(deci)[2:] #conversion to binary
    biy = biy.zfill(num_bits) #if binary representation is in less than num_bits fill left over bits with 0
    return biy

def r_type_instruction(instruction, register_map):
    op = instruction[0]
    rd = instruction[1]
    rs1 = instruction[2]
    rs2 = instruction[3]

    opcode = '0110011'

    funct_map = {
        'add': ('000', '0000000'),
        'sub': ('000', '0100000'),
        'sll': ('001', '0000000'),
        'slt': ('010', '0000000'),
        'sltu': ('011', '0000000'),
        'xor': ('100', '0000000'),
        'srl': ('101', '0000000'),
        'or': ('110', '0000000'),
        'and': ('111', '0000000')
        }

    funct3, funct7 = funct_map[op]

    checkReg=check_reg_name(rd,register_map)
    if checkReg==True:
        rd_encoding = register_map[rd]
    else:
        return f'{checkReg} at line {program_counter} ({" ".join(instruction)})'

    checkReg=check_reg_name(rs1,register_map)
    if checkReg==True:
        rs1_encoding = register_map[rs1]
    else:
        return f'{checkReg} at line {program_counter} ({" ".join(instruction)})'

    regCheck=check_reg_name(rs2,register_map)
    if regCheck==True:
        rs2_encoding = register_map[rs2]
    else:
        return f'{checkReg} at line {program_counter} ({" ".join(instruction)})'
    
    return funct7 + rs2_encoding + rs1_encoding + funct3 + rd_encoding + opcode

def i_type_instruction(instruction, register_map):
    op = instruction[0]
    rd = instruction[1]
    if op == 'lw':
        imm = instruction[2]
        rs1 = instruction[3]
    else:
        rs1 = instruction[2]
        imm = instruction[3]

    opcode_map = {
        'lw': '0000011',
        'addi': '0010011',
        'sltiu': '0010011',
        'jalr': '1100111'
    }

    funct3_map = {
        'lw': '010',
        'addi': '000',
        'sltiu': '011',
        'jalr': '000'
        }

    opcode = opcode_map[op]
    funct3 = funct3_map[op]

    checkReg=check_reg_name(rd,register_map)
    if checkReg==True:
        rd_encoding = register_map[rd]
    else:
        return f'{checkReg} at line {program_counter} ({" ".join(instruction)})'

    checkReg=check_reg_name(rs1,register_map)
    if checkReg==True:
        rs1_encoding = register_map[rs1]
    else:
        return f'{checkReg} at line {program_counter} ({" ".join(instruction)})'

    imm_binary = deci_to_bin(imm, 12) #binary of imm
    imm_11_0 = imm_binary[-12:]

    if len(imm_11_0)>12:
        return f'Invalid imm ({imm}) of length {len(imm_11_0)} at line {program_counter} ({" ".join(instruction)})'

    return imm_11_0 + rs1_encoding + funct3 + rd_encoding + opcode

def s_type_instruction(instruction, register_map):
    op = instruction[0]
    rs2 = instruction[1]
    imm = instruction[2]
    rs1 = instruction[3]

    opcode = '0100011'

    funct3 = '010'

    imm_binary = deci_to_bin(imm, 12)
    imm_4_0 = imm_binary[-5:]
    imm_11_5 = imm_binary[:-5]

    if len(imm_4_0)+len(imm_11_5)>15:
        return f'Invalid imm ({imm}) of length {len(imm_4_0)+len(imm_11_5)} at line {program_counter} ({" ".join(instruction)})'

    checkReg=check_reg_name(rs2,register_map)
    if checkReg==True:
        rs2_encoding = register_map[rs2]
    else:
        return f'{checkReg} at line {program_counter} ({" ".join(instruction)})'

    checkReg=check_reg_name(rs1,register_map)
    if checkReg==True:
        rs1_encoding = register_map[rs1]
    else:
        return f'{checkReg} at line {program_counter} ({" ".join(instruction)})'

    return imm_11_5 + rs2_encoding + rs1_encoding + funct3 + imm_4_0 + opcode

def b_type_instruction(instruction, labels, register_map):
    op = instruction[0]
    rs1 = instruction[1]
    rs2 = instruction[2]
    lab = instruction[3]

    funct3_map = {
        'beq': '000',
        'bne': '001',
        'blt': '100',
        'bge': '101',
        'bltu': '110',
        'bgeu': '111'
        }

    opcode = '1100011'

    funct3 = funct3_map[op]

    checkReg=check_reg_name(rs1,register_map)
    if checkReg==True:
        rs1_encoding = register_map[rs1]
    else:
        return f'{checkReg} at line {program_counter} ({" ".join(instruction)})'

    checkReg=check_reg_name(rs2,register_map)
    if checkReg==True:
        rs2_encoding = register_map[rs2]
    else:
        return f'{checkReg} at line {program_counter} ({" ".join(instruction)}))'

    imm_binary = label_to_bin(lab, 20, labels)

    imm_4_1__11 = imm_binary[-5:-1] + imm_binary[-11]
    imm_12__10_5 = imm_binary[-12] + imm_binary[-11:-5]

    if len(imm_4_1__11)+len(imm_12__10_5)>12:
        return f'Invalid imm ({lab}) of length {len(imm_4_1__11)+len(imm_12__10_5)} at line {program_counter} ({" ".join(instruction)})'

    return imm_12__10_5 + rs2_encoding + rs1_encoding + funct3 + imm_4_1__11 + opcode

def u_type_instruction(instruction, register_map):
    op = instruction[0]
    rd = instruction[1]
    imm = instruction[2]

    opcode_map = {
        'lui': '0110111',
        'auipc': '0010111'
    }

    opcode = opcode_map[op]

    imm_binary = deci_to_bin(imm,32) 
    imm_31_12 = imm_binary[:-12]

    if len(imm_31_12)>20:
        return f'Invalid imm ({imm}) of length {len(imm_31_12)} at line {program_counter} ({" ".join(instruction)})'

    checkReg=check_reg_name(rd,register_map)
    if checkReg==True:
        rd_encoding = register_map[rd]
    else:
        return f'{checkReg} at line {program_counter} ({" ".join(instruction)})'

    return imm_31_12 + rd_encoding + opcode

def j_type_instruction(instruction, labels, register_map):
    op = instruction[0]
    rd = instruction[1]
    lab = instruction[2]

    opcode = '1101111'

    checkReg=check_reg_name(rd,register_map)
    if checkReg==True:
        rd_encoding = register_map[rd]
    else:
        return f'{checkReg} at line {program_counter} ({" ".join(instruction)})'

    imm_binary = label_to_bin(lab, 20, labels)
    imm_20__10_1__11__19_12 = imm_binary[-21] + imm_binary[-11:-1] + imm_binary[-12] + imm_binary[-20:-12]

    if len(imm_20__10_1__11__19_12)>20:
        return f'Invalid imm ({lab}) of length {len(imm_20__10_1__11__19_12)} at line {program_counter} ({" ".join(instruction)})'

    return imm_20__10_1__11__19_12 + rd_encoding + opcode

def tokenise_assembly_text(assembly_text):
    tokenised_lines = []
    assembly_text = assembly_text.replace(',', ' ')
    assembly_text = assembly_text.replace('(', ' ')
    assembly_text = assembly_text.replace(')', ' ')

    lines = assembly_text.strip().split('\n')
    for line in lines:
        tokenised_lines.append(line.strip().split())

    return tokenised_lines

def main(read_filepath,write_filepath):
    global program_counter
    # Define mapping for registers
    register_map = {
        'zero': '00000',
        'ra': '00001',
        'sp': '00010',
        'gp': '00011',
        'tp': '00100',
        't0': '00101',
        't1': '00110',
        't2': '00111',
        's0': '01000',
        's1': '01001',
        'a0': '01010',
        'a1': '01011',
        'a2': '01100',
        'a3': '01101',
        'a4': '01110',
        'a5': '01111',
        'a6': '10000',
        'a7': '10001',
        's2': '10010',
        's3': '10011',
        's4': '10100',
        's5': '10101',
        's6': '10110',
        's7': '10111',
        's8': '11000',
        's9': '11001',
        's10': '11010',
        's11': '11011',
        't3': '11100',
        't4': '11101',
        't5': '11110',
        't6': '11111'
        }

    with open(read_filepath, 'r') as file:
        assembly_text = file.read()

    ASM = tokenise_assembly_text(assembly_text)
    binary = []
    program_counter = 0
    labels = dict()

    R_TYPE = ['add', 'sub', 'sll', 'slt', 'sltu', 'xor', 'srl', 'or', 'and']
    I_TYPE = ['lw', 'addi', 'sltiu', 'jalr']
    S_TYPE = ['sw']
    B_TYPE = ['beq', 'bne', 'blt', 'bge', 'bltu', 'bgeu']
    U_TYPE = ['lui', 'auipc']
    J_TYPE = ['jal']

    for line in ASM: # for labels
        if isNewLabel(line[0], labels):
            line.remove(line[0])
            if len(line) == 0:
                ASM.remove(line)
        program_counter+=1

    hault=""
    program_counter = 0
    for line in ASM:
        if line==['beq', 'zero', 'zero', '0']:
            labels['0'] = program_counter*4
            hault=line
        if line[0] in R_TYPE:
            binary.append(r_type_instruction(line, register_map))
        elif line[0] in I_TYPE:
            binary.append(i_type_instruction(line, register_map))
        elif line[0] in S_TYPE:
            binary.append(s_type_instruction(line, register_map))
        elif line[0] in B_TYPE:
            binary.append(b_type_instruction(line, labels, register_map))
        elif line[0] in U_TYPE:
            binary.append(u_type_instruction(line, register_map))
        elif line[0] in J_TYPE:
            binary.append(j_type_instruction(line, labels, register_map))
        else:
            with open('bin.txt','w') as file :
                file.write(f'Incorrect Instruction "{line[0]}" at line {program_counter} ({" ".join(line)})')
                return
            #handling error in instruction name type
        program_counter+=1

    if hault=="":
        with open('bin.txt','w') as file :
            file.write("Error: Virtual hault not present at end of instructions.")
            return
    elif ASM[-1]!=hault:
        with open('bin.txt','w') as file :
            file.write("Error: Virtual hault present but not at end of instructions.")
            return

    with open(write_filepath, 'w') as file:
        for i in binary:
            if i[0] == 'I':
                file.truncate(0)
                file.write(str(i))
                return
            file.write(str(i))
            file.write('\n')
        

read_filepath = sys.argv[1]
write_filepath = sys.argv[2]

main(read_filepath, write_filepath)
