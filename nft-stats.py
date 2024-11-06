#!/usr/bin/env python3
import math
import os
import re
import subprocess
import argparse

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


def run_command(args):
    command = "nft list ruleset"
    if args.table:
        command = f"nft list table {args.table}"
    if args.chain:
        command = f"nft list chain filter {args.chain}"
    if args.debug:
        print(f"## Command used : {command}")
    nft_run = subprocess.run(command, shell=True, capture_output=True)
    res = nft_run.stdout.decode().split('\n')
    if args.debug:
        print("## OUTPUT :")
        print(res)
    return res


def clear_line(line):
    line = line.replace('{', '')
    line = line.replace('}', '')
    line = line.replace(';', '')
    line = line.strip()
    return line

def nft_stats(command_result):
    table = ""
    chain = ""
    table_first_line_printed = False
    iter_res = iter(command_result)
    for line in iter_res:
        line = clear_line(line)
        if line.startswith('table'):
            table = f"{line.split()[1].upper()} {line.split()[2].upper()}"
        elif line.startswith('chain'):
            chain = line.split()[1]
            next_line = clear_line(next(iter_res));
            if next_line.startswith('type') and 'policy' in next_line:
                policy = next_line.split('policy')[1].strip().upper()
                print(f"\nchain {chain.upper()} {table} (policy {policy})")
                table_first_line_printed = False
            else:
                print(f"\nchain {chain}")
                table_first_line_printed = False
        elif line.startswith('set'):
            chain = ""
        else:
            if line and chain:
                counter_hit = "-"
                counter_bytes = "-"
                action = ""
                match = None
                res = re.search(re_counter, line)
                if res:
                    counter_hit = convert_size(res.group(1), one_k=1000, minimal=500000)
                    counter_bytes = convert_size(res.group(2))
                    match = re.sub(re_counter, '', line)

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


def main():
    parser = argparse.ArgumentParser(description='Show well formated statitics for NFT output')
    parser.add_argument('--chain', '-c', type=str, required=False, help="Show specific Chain")
    parser.add_argument('--table', '-t', type=str, required=False, help="Show specific Table")
    parser.add_argument('--debug', '-d', action="store_true", help="Debug mode")
    args = parser.parse_args()

    out = run_command(args)
    nft_stats(out)


if __name__ == '__main__':
    if os.geteuid() != 0:
        exit("You need to have root privileges to run this script.")
    main()
