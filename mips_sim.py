import sys

file_path = sys.argv[1]

# bin파일 읽기(바이트 자료형)
with open(file_path, "rb") as f:
    data = f.read()

# 8개씩 끊기
# length=8
# t1_list=[test1[i:i+length] for i in range(0, len(test1), length)]

# 바이트 자료형 비트로 바꾸는 함수 정의
def bytetoBit(d):
    return ''.join('{:08b}'.format(b) for b in d)
test = bytetoBit(data)    

# 이진수를 16진수로 바꾸는 함수
def binaryToHex(binaryValue):
    number = int(binaryValue,2)
    return format(number, '08x')

# 4바이트는 32비트니까 32글자씩 끊어서 리스트에 넣기
test_bitlist=[test[i:i+32] for i in range(0, len(test), 32)]

# 리스트에 잘 들어갔나 확인차
# for items in t1_bitlist:
#     print(items)

# 사용 유형별
rCase1 = ['add','addu','and','nor','or','slt','sltu','sub','subu','xor']
rCase2 = ['div','divu','mult','multu']
rCase3 = ['jalr','syscall']
rCase4 = ['jr','mthi','mtlo']
rCase5 = ['mfhi','mflo']
rCase6 = ['sll','sra','srl']
rCase7 = ['sllv','srav','srlv']

iCase1 = ['addi','andi','ori','slti','xori','addiu','sltiu']
iCase2 = ['beq','bne']
iCase3 = ['lb','lbu','lh','lhu','lw','sb','sh','sw']
iCase4 = ['lui']

# funct로 instruction명 return
def rSwitch(f1, f2):
    if f1 == '000':
        inst = {'000':'sll','010':'srl','011':'sra','100':'sllv','110':'srlv','111':'srav'}.get(f2)
    elif f1 == '001':
        inst = {'000':'jr','001':'jalr','100':'syscall'}.get(f2)
    elif f1 == '010':
        inst = {'000':'mfhi','001':'mthi','010':'mflo','011':'mtlo'}.get(f2)
    elif f1 == '011':
        inst = {'000':'mult','001':'multu','010':'div','011':'divu'}.get(f2)
    elif f1 == '100':
        inst = {'000':'add','001':'addu','010':'sub','011':'subu','100':'and','101':'or','110':'xor','111':'nor'}.get(f2)
    elif f1 == '101':
        inst = {'010':'slt','011':'sltu'}.get(f2)
    else:
        inst = 'unknown instruction'

    if inst == None:
        inst = 'unknown instruction'
    
    return inst

def rSeq(inst, rs, rt, rd, sa):
    if inst in rCase1:
        line = f'${rd}, ${rs}, ${rt}'
    elif inst in rCase2:
        line = f'${rs}, ${rt}'
    elif inst in rCase3:
        if inst == 'jalr':
            line = f'${rd}, ${rs}'
        elif inst == 'syscall':
            line = ''
    elif inst in rCase4:
        line = f'${rs}'
    elif inst in rCase5:
        line = f'${rd}'
    elif inst in rCase6:
        line = f'${rd}, ${rt}, {sa}'
    elif inst in rCase7:
        line = f'${rd}, ${rt}, ${rs}'
    else:
        line = ''
    return line



# opcode로 instructino명 return
def iSwitch(o1, o2):
    if o1 == '000':
        inst = {'100':'beq','101':'bne'}.get(o2)
    elif o1 == '001':
        inst = {'000':'addi','001':'addiu','010':'slti','011':'sltiu','100':'andi','101':'ori','110':'xori', '111':'lui'}.get(o2)
    elif o1 == '100':
        inst = {'000':'lb','001':'lh','011':'lw','100':'lbu','101':'lhu'}.get(o2)
    elif o1 == '101':
        inst = {'000':'sb','001':'sh','011':'sw'}.get(o2)
    else:
        inst = 'unknown instruction'

    if inst == None:
        inst = 'unknown instruction'

    return inst

def iSeq(inst, rs, rt, imm):

    if inst in iCase1:
        line = f'${rt}, ${rs}, {imm}'
    elif inst in iCase2:
        line = f'${rt}, ${rs}, {imm}'
    elif inst in iCase3:
        line = f'${rt}, {imm}(${rs})'
    elif inst in iCase4:
        line = f'${rt}, {imm}'
    else:
        line = ''

    return line

def jSeq(target):
    line = f'{target}'
    return line

def twocom(binary):
    if binary[0] == '0':
        num = int(binary,2)
    elif binary[0] == '1':
        num = int(binary,2) - 1
        if len(binary) == 16:
            num ^= 0xFFFF
        elif len(binary) == 26:
            num ^= 0xFFFFFF
        num *= -1

    return num

# for items in t1_bitlist:
for idx, items in enumerate(test_bitlist):
    opcode = items[0:6]
    if opcode == '000000': # opcode = 000000 rtype
        func1 = items[26:29]
        func2 = items[29:32]
        instType = 'r'
        inst = rSwitch(func1, func2)
        
    elif opcode[0:5] == '00001': #jtype
        instType = 'j'
        if opcode[5] == '0':
            inst = 'j'
        elif opcode[5] == '1':
            inst = 'jal'
        else:
            inst = 'unknown instruction'

    elif opcode[0:4] == '0100': #unknown
        instType = 'un'
        inst = 'unknown instruction'
    
    else: # itype
        op1 = opcode[0:3]
        op2 = opcode[3:6]
        instType = 'i'
        inst = iSwitch(op1, op2)
    
    if instType == 'r':
        rs = int(items[6:11],2)
        rt = int(items[11:16],2)
        rd = int(items[16:21],2)
        sa = int(items[21:26],2)

        reg = rSeq(inst, rs, rt, rd, sa)
        # if inst in rCase1:
        #     print(f'inst: {idx} {binaryToHex(items)} {inst} ${rd}, ${rs}, ${rt}')        
        
    elif instType == 'i':
        rs = int(items[6:11],2)     # 5bit
        rt = int(items[11:16],2)    # 5bit
        imm = twocom(items[16:32])   # 16bit

        reg = iSeq(inst, rs, rt, imm)    
    
    elif instType == 'j':
        target = twocom(items[6:32])
        reg = jSeq(target)
    
    else:
        pass

    print(f'inst {idx}: {binaryToHex(items)} {inst} '+reg)
    # print("inst: {} {} {}".format(idx, binaryToHex(items), inst))

# for item in t1_bitlist:
#     print(binaryToHex(item))

# for i, v in enumerate(t1_bitlist):
#     print("inst: {} {} {}".format(i, binaryToHex(v), inst))
