#!/usr/bin/env python3
import math
import os
import re
import subprocess

command = "nft list ruleset"
re_counter = r'counter packets (\d+) bytes (\d+)'
size_name = ("", "K", "M", "G", "T")


def tabulator(text, min_field=10):
    tabs_to_append = min_field - len(text)
    return_string = (text if (tabs_to_append <= 0) else text + " " * tabs_to_append)
    return return_string


def convert_size(size_bytes, one_k=1024, minimal=0):
    try:
        size = int(size_bytes)
    except ValueError:
        return size_bytes
    if size == 0:
        return "0"
    if size < minimal:
        return str(size)
    tp_i = int(math.floor(math.log(size, one_k)))
    tp_p = math.pow(1024, tp_i)
    tp_s = round(size / tp_p, 2)
    tp_s = str(tp_s)
    return f"{tp_s.rstrip('0').rstrip('.') if '.' in tp_s else tp_s}{size_name[tp_i]}"


def main():
    nft_run = subprocess.run(command, shell=True, capture_output=True)
    res = nft_run.stdout.decode().split('\n')
    table = ""
    chain = ""
    for line in res:
        line = line.replace('{', '')
        line = line.replace('}', '')
        line = line.replace(';', '')
        line = line.strip()
        if line.startswith('table'):
            table = line.split()[1].upper()
        elif line.startswith('chain'):
            chain = line.split()[1].upper()
        elif line.startswith('type') and 'policy' in line:
            policy = line.split('policy')[1].strip().upper()
            print(f"\n{chain} {table} (policy {policy})")
            print(f"{tabulator('pkts')} {tabulator('bytes')} {tabulator('action', 7)}")
        elif line.startswith('set'):
            chain = ""
        else:
            if line and chain:
                counter_hit = "-"
                counter_bytes = "-"
                action = ""
                match = None
                if 'counter packets' in line:
                    res = re.search(re_counter, line)
                    counter_hit = convert_size(res.group(1), one_k=1000, minimal=500000)
                    counter_bytes = convert_size(res.group(2))

                    match_slit = line.split('counter packets')
                    if len(match_slit)>1:
                        match = match_slit[0]
                    else:
                        match = ""
                if 'accept' in line:
                    action = "ACCEPT"
                elif 'reject' in line:
                    action = "REJECT"
                elif 'drop' in line:
                    action = "DROP"
                if not table_first_line_printed:
                  print(f"{tabulator('pkts')} {tabulator('bytes')} {tabulator('action', 7)}")
                  table_first_line_printed = True
                print(f"{tabulator(counter_hit)} {tabulator(counter_bytes)} {tabulator(action, 7)} {match if match!=None else line}")



if __name__ == '__main__':
    if os.geteuid() != 0:
        exit("You need to have root privileges to run this script.")
    main()
