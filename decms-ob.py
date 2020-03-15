import sys
import os
import os.path
import shutil
from deobf.trace_reader import *
from deobf import intruction_mgr

def split_ins_str(ins_str):
    ins_str_p = ins_str.replace("\t", " ").lower()
    ins_p = ins_str_p.find(" ")
    mne = ins_str_p[0:ins_p].strip()
    op_str = ins_str_p[ins_p:].strip()
    return mne, op_str
#

def get_all_condi_jump_dests(trace_list):
    addr2dest = {}
    l = len(trace_list)
    for i in range(0, l):
        item = trace_list[i]
        ins_str = item["ins_str"].lower()
        addr = item["addr"]
        mne, op_str = split_ins_str(ins_str)
        if (is_jmp_condition_str(mne, op_str)):
            dest_item = trace_list[i+1]
            dest = dest_item["addr"]
            dests = None
            if addr in addr2dest:
                dests = addr2dest[addr]
            #
            else:
                dests = []
                addr2dest[addr] = dests
            #
            if (dest not in dests):
                dests.append(dest)
            #
        #
    
    #
    return addr2dest
#

#尽量去除控制流平坦化fla
if __name__ == "__main__":
    if (len(sys.argv)<3):
        print("usage %s <elf_path> <elf_out_path> <trace_path>")
        sys.exit(-1)
    #
    mgr = intruction_mgr.IntructionManger(True)

    mgr2 = intruction_mgr.IntructionManger(False)
    path = sys.argv[1]
    out_path = sys.argv[2]
    trace_path = sys.argv[3]
    libname = os.path.basename(path)
    trace_list = read_trace(trace_path)
    shutil.copy(path, out_path)
    #print(trace_list)
    i = 0
    n = len(trace_list)
    addr2dest = get_all_condi_jump_dests(trace_list)
    with open(out_path, "rb+") as f:
        for i in range(0, n):
            item = trace_list[i]
            ins_str = item["ins_str"]
            mne, op_str = split_ins_str(ins_str)
            addr = item["addr"]
            if (addr in addr2dest):
                dests = addr2dest[addr]
                if (len(dests) == 1):
                    #将所有只有一个目标地址的条件跳转直接改成，b xxxx，防止虚假条件跳转干扰ida分析
                    dest = dests[0]
                    asm_str = "b #0x%08x"%dest

                    print("addr [0x%08X] %s has one dest fix to %s"%(addr, ins_str, asm_str))
                    tub = mgr.asm(asm_str, addr)
                    bs = bytearray(tub[0])
                    f.seek(addr, 0)
                    f.write(bs)
                    continue
                #
            #

            should_fix = False
            fix_op = "b"
            clean_prev = False
            #所有thumb的bx都是假的
            if (mne == "bx" and op_str.find("lr") == -1 and op_str.find("pc") == -1 and op_str.find("lr") == -1):
                should_fix = True
                clean_prev = True
                fix_op = "b"
            #
            elif (mne.find("mov")>-1 and op_str.startswith("pc")):
                should_fix = True
                fix_op = "b"
            #
            elif (mne == "blx" and op_str[0] != "#"):
                #print("this is blx:%s"%ins_str)
                should_fix = True
                fix_op = "blx"
            #
            if (should_fix):
                nbytes_this = len(item["bytes"])
                if (nbytes_this == 4):
                    print("keep arm ins %s addr 0x%08X"%(ins_str, addr))
                    #观察知所有arm指令都会跳回thumb，所以不要patch,保留bx xxx
                    continue
                #
                print("[0x%08X][%s]"%(addr, ins_str))
                prev_id = i - 1
                next_id = i + 1
                next_item = trace_list[next_id]
                next_addr = next_item["addr"]
                nbytes = len(next_item["bytes"])
                if (next_id < n):
                    next_libname = next_item["libname"]
                    if (next_libname != libname):
                        first_ret_addr = 0
                        j = next_id+1
                        while True:
                            item_x = trace_list[j]
                            libname_x = item_x["libname"]
                            if (libname_x == libname):
                                first_ret_addr = item_x["addr"]
                                break
                            #
                            j = j+1
                        #
                        print("jump target %s addr 0x%08X from addr 0x%08X not in target so first return to target so addr [0x%08X] skip patch..." %(next_libname, next_addr, addr, first_ret_addr))
                        continue
                    #

                    #add_cref
                    #define fl_JF
                    if (clean_prev):
                        prev_item = trace_list[prev_id]
                        nprev = len(prev_item["bytes"])
                        b = bytearray([0]*nprev)
                        prev_addr = prev_item["addr"]
                        f.seek(prev_addr, 0)
                        print("zero 0x%08X size %d"%(prev_addr, nprev))
                        f.write(b)
                    #

                    asm_str = "%s #0x%08x"%(fix_op, next_addr)
                    bs = bytearray(mgr.asm(asm_str, addr)[0])
                    if (len(bs) != nbytes_this):
                        print("warning try to addr 0x%08X write nbytes %d, but actual len is %d, ins_str:[%s]!!!"%(addr, len(bs), nbytes_this, asm_str))
                        continue
                    #
                    print("write 0x%08X size %d ins_str:[%s]"%(addr, nbytes_this, asm_str))
                    f.seek(addr, 0)
                    f.write(bs)
                #
            #
        #
    #
#