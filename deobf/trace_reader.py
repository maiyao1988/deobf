import os
import sys
from deobf.tracer import *

#TODO 与Tracer合并
def read_trace(trace_path):
    ins_list = []
    with open(trace_path, "r") as f:
        for line in f:
            line = line.strip()
            
            dic = {}
            sa = line.split(":")
            part = sa[0]
            start = part.rfind("]")+1
            addr = int(part[start:], 16)
            dic["addr"] = addr
            ncomma = line.find(":")+1
            comment = line.find(";")
            if (comment < 0):
                comment = len(line)
            #
            ins_str = line[ncomma:comment]
            dic["ins_str"] = ins_str.replace('\t', ' ').strip()

            dic["bytes"] = get_ins_bytes_by_line(line)

            p2 = line.find("[")
            p1 = 1

            dic["libname"] = line[p1:p2].strip()
            ins_list.append(dic)

            p_base = line.find("[")+1
            p_end = line.find("]")
            base_addr_str = line[p_base:p_end]
            dic["base"] = int(base_addr_str, 16)
            
        #
    #
    return ins_list
#