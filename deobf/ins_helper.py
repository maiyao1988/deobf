import os

_cond_oposite_map = {"eq":"ne", "cs":"cc", "mi":"pl", "vs":"vc", "hi":"ls", "ge":"lt", "gt":"le", "ne":"eq", "cc":"cs", "pl":"mi", "vc":"vs", "ls":"hi", "lt":"ge", "le":"ge"}

_b_cond_ins = ["b"+cond for cond in _cond_oposite_map] +  ["b"+cond +".w" for cond in _cond_oposite_map]

_reg_try = {"r0", "r1", "r2", "r3", "r4", "r5", "r6", "r7", "r8", "r9"}

def get_free_regs(codelist):
    global _reg_try
    reg_used = set()
    for ins in codelist:
        op_str = ins.op_str
        for reg in _reg_try:
            if (op_str.find(reg)>0):
                reg_used.add(reg)
            #
        #
    #
    return _reg_try - reg_used
#
def is_condition_mne(mne):
    global _cond_oposite_map

    for k in _cond_oposite_map:
        if (mne.endswith(k)):
            return True
        #
    #
    if (mne.startswith("it")):
        return True
    #
    return False
#
def is_jmp_condition(ins):
    global _b_cond_ins
    mne = ins.mnemonic
    return is_jmp_condition_str(mne, ins.op_str)
#

#FIXME bug here, going to remove
def is_jmp_condition_str(mne, op_str):

    global _b_cond_ins
    if (mne in _b_cond_ins):
        return True
    elif (mne in ("cbz", "cbnz")):
        return True
    #
    if (is_condition_mne(mne)):
        if (mne.startswith("pop") or mne.startswith("ldm")):
            if (op_str.find("pc") > -1):
                return True
        elif (mne.startswith("mov")):
            if (op_str.split()[0].strip() == "pc") and is_condition_mne(mne):
                return True
            #
        #
    #
#

#目的地址是立即数的跳转
def is_jmp_imm(ins):
    mne = ins.mnemonic
    return mne[0] == "b" and mne not in ("blx", "bl", "bic", "bics") or mne in ("cbz", "cbnz")
#

def is_table_jump_mne(mne):
    return mne in ("tbb", "tbb.w", "tbh", "tbh.w")
#

def is_table_jump(i):
    return is_table_jump_mne(i.mnemonic)
#

#判断是否无条件跳转,这种跳转只会产生一个分支
def is_jmp_no_ret_mne(mne, op_str):
    #b xxxx
    #mov pc, xxx
    #pop xxx, pc,xxx
    
    if (mne == "b" or mne == "b.w"):
        return True
    
    if (not is_condition_mne(mne)):
        if (mne.startswith("pop") or mne.startswith("ldm")):
            if (op_str.find("pc") > -1):
                return True
        elif (mne.startswith("mov")):
            if (op_str.split()[0].strip() == "pc"):
                return True
            #
        #
    #

    if (is_table_jump_mne(mne)):
        return True
    #
    return False
#

#判断是否无条件跳转,这种跳转只会产生一个分支
def is_jmp_no_ret(i):
    mne = i.mnemonic
    #b xxxx
    #mov pc, xxx
    #pop xxx, pc,xxx
    
    return is_jmp_no_ret_mne(mne, i.op_str)
#

#判断是否跳转，包括无条件和有条件跳转
def is_jmp_mne(mne, op_str):
    if (is_jmp_no_ret_mne(mne, op_str)):
        return True
    if mne[0] == "b" and mne not in ("bl", "blx", "bic", "bics"):
        return True
    #
    if mne in ("cbz", "cbnz"):
        return True
    #

    return False
#

#判断是否跳转，包括无条件和有条件跳转
def is_jmp(i):
    mne = i.mnemonic
    op_str = i.op_str
    return is_jmp_mne(mne, op_str)
#

def condi_oposite(cond):
    return _cond_oposite_map(cond)
#

#计算it指令覆盖范围，ittt为3,itt为2,it为1
def count_it(ins):
    mne = ins.mnemonic
    if (mne.startswith("it")):
        return len(mne)-1
    #
    return 0
#

def write_codes(f, address, max_size, insns, ins_mgr):
    f.seek(address, 0)
    next_addr = address
    byte_list = []
    size_left = max_size
    for code_str in insns:
        b = ins_mgr.asm(code_str, next_addr)[0]
        byte_list.extend(b)
        next_addr = next_addr + len(b)
        size_left = size_left - len(b)
        if (size_left < 0):
            #空间不足，报错
            #print("not enough size")
            return -1
        #
        #print("patch 0x%08X to %s[%r]"%(next_addr, code_str, [hex(x) for x in b]))
    #
    f.write(bytearray(byte_list))
    return next_addr
#

def clean_bytes(f, addr_from, addr_to):
    f.seek(addr_from, 0)
    nleft = addr_to - addr_from
    assert nleft>=0
    #print ("n left %d"%nleft)
    for _ in range(0, nleft):
        b = bytearray([0])
        f.write(b)
    #
#


def get_jmp_dest_str(mne, op_str):
    if (mne[0] == 'b'):
        if (op_str[0] == '#'):
            jmp_addr = int(op_str[1:], 16)
            return jmp_addr
        #
    #
    elif (mne in ("cbz", "cbnz")):
        sa = op_str.split(",")
        dest_str = sa[1].strip()
        assert dest_str[0] == '#'
        jmp_addr = int(dest_str[1:], 16)
        return jmp_addr
    #
    return None
#

def get_jmp_dest(i):
    return get_jmp_dest_str(i.mnemonic, i.op_str)
#

def get_block_codes(f, block, ins_mgr):
    codelist = []
    b=block
    size = b.end - b.start
    assert size > 0, "block %r size <=0"%b
    f.seek(b.start, 0)
    code_bytes = f.read(size)
    return ins_mgr.disasm(code_bytes, b.start)
#


def addr_in_blocks(addr, blocks):
    for b in blocks:
        if (b.start <= addr and b.end > addr):
            return True
        #
    #
    return False
#
