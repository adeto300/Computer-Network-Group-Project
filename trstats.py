"""
Sample DocString. ..
"""
import argparse
import json
import os
import sys
import subprocess
import time
import shutil

from datetime import datetime
from pathlib import Path
from statistics import mean, median

import plotly.express as px

import pandas as pd
import re

SPEED_PATTERN = '(\d*\.\d+|\d+) ms'

subprocess.call('dir', shell=True)

prev_hop_list = []
check_stamp = None


#checks file in directory whether it already exist
def check_file(ifile):
    global check_stamp
    if os.path.exists(ifile):
        file, ext = os.path.splitext(ifile)
        nfile = f"{file} {check_stamp}{ext}"
        os.rename(ifile, nfile)


#get datetime
def get_stamp():
    return str(datetime.now())[:-7].replace(':', '')

#writes traceroute output to file
def traceroute_to_file(data, ofile):
    with open(ofile, 'w') as outfile:
        # outfile.write(f"{msg}\n")
        outfile.write(data)

#convert traceroute output to json file
def traceroute_to_json(jfile, tr_dict_list=None):
    global check_stamp
    check_file(jfile)
    with open(jfile, 'w', encoding='utf-8') as outfile:
        json.dump(tr_dict_list, outfile, indent=4)

#checks delay between traceroute
def check_delay(i, args):
    if i < args.NUM_RUNS:
        if args.RUN_DELAY:
            delay = args.RUN_DELAY
            time.sleep(delay)


def trace_hops(trlist: list):
    global prev_hop_list
    for i, line in enumerate(trlist):
        if 'traceroute' not in line:
            hop_list = [i for i in line.replace('*', '').strip().split('  ')]
            if i == 0 or i == len(trlist) - 1:
                # tr_listings.append(hop_list)
                yield '  '.join(hop_list)
            else:
                if not hop_list[0].isdigit():
                    if prev_hop_list[0].isdigit() and hop_list[0].isdigit():
                        # tr_listings.append(prev_hop_list)
                        yield '  '.join(prev_hop_list)
                    else:
                        prev_hop_list += hop_list
                else:
                    # tr_listings.append(prev_hop_list)
                    yield '  '.join(prev_hop_list)
                    prev_hop_list = hop_list

#function to oprocess traceout output
def process_tr_output(output):
    # global
    tr_dict_list = []
    for k, tr_output in output.items():
        trlist = tr_output.splitlines()
        tr_listings = list(trh for trh in trace_hops(trlist) if trh and len(trh) > 0)
        for line in tr_listings:
            # logger.info(f"{line = }")
            hop_dict = {}
            # speeds = [float(i.split(' ')[0]) for i in line if i.endswith('ms')]
            speeds = re.findall(SPEED_PATTERN, line)
            speeds = [float(s) for s in speeds]
            line = re.sub(SPEED_PATTERN, '', line).strip()
            # logger.info(f"{speeds = }")
            hop_dict['hop'], hop_dict['hosts'], hop_dict['speeds'] = line.split('  ')[0], line.split('  ')[1:], speeds

            tr_dict_list.append(hop_dict)
            # logger.info('=' * 88)
            # logger.info(hop_dict)

    return tr_dict_list


def multi_tr_pro(multi_tr_list, file):
    """Combines all traceroute outputs together"""
    global check_stamp
    combined_dict = {}
    for i, d in enumerate(multi_tr_list):
        d_i = d['hop']
        if d_i in combined_dict:
            for k, v in d.items():
                if k in ('hosts', 'speeds', ):
                    
                    combined_dict[d_i][k] = combined_dict[d_i][k] + v
        else:
            combined_dict[d_i] = {}
            combined_dict[d_i]['hop'] = d['hop']
            combined_dict[d_i]['hosts'] = d['hosts']
            combined_dict[d_i]['speeds'] = d['speeds']

    check_file(file)
    traceroute_to_json(file, list(combined_dict.values()))
    return combined_dict


def read_text_file(file_path):
    """Reads a text file"""
    
    with open(file_path, 'r') as f:
        # next(f)
        data=f.read()
    return data

def OutputPath(dirs):
    """defines and makes required directories"""
    if(not os.path.exists(dirs)):
        os.mkdir(dirs)

def main(argv=None):
    """Main funciton and entry point"""
    global prev_hop_list
    output ={}
    args = parse_trace_args()

    out_dir = str(Path(__file__).resolve().parent / 'trace_to_files_')
    json_out_dir = str(Path(__file__).resolve().parent / 'Outputs_of_')

    parts = OutputPath(f'{json_out_dir}{args.TEST_DIR if args.TEST_DIR else args.TARGET}')

    if args.TARGET:
        global check_stamp
        check_stamp = get_stamp()
        OutputPath(f'{out_dir}{args.TARGET}')
        
        jfile, jfyl_re = f'{out_dir}{args.TARGET}{os.sep}{args.TARGET} data.json', f'{out_dir}{args.TARGET}{os.sep}{args.TARGET} re.json'

        cfile = f'{json_out_dir}{args.TARGET}{os.sep}{args.OUTPUT if args.OUTPUT else args.TARGET}.json'

        #using subprocess to run the traceroute
        for i in range(1, args.NUM_RUNS + 1):
            tfile=f'{out_dir}{args.TARGET}{os.sep}{args.TARGET}({i}).txt'
            check_file(tfile)

            terminalInfo = subprocess.Popen(['traceroute', "-m", str(args.MAX_HOPS), args.TARGET], stdout=subprocess.PIPE)
            out, err = terminalInfo.communicate()
            terminalInfo = out.decode('unicode-escape') 
            print(terminalInfo)
        
            #rslt = subprocess.run(
            #    ['traceroute', "-m", str(args.MAX_HOPS), args.TARGET], shell=True, stdout=subprocess.PIPE
            #)

            #tr_output = rslt.stdout.decode('utf-8')
            traceroute_to_file(terminalInfo, tfile)
            output[i] = terminalInfo
            

            check_delay(i, args)

        multi_tr_list = process_tr_output(output)
        d4c = multi_tr_pro(multi_tr_list, jfyl_re)
        d4c = {i[0]: i[1] for i in sorted(d4c.items(), key=lambda x: int(x[0]))}

        #computes hop, avg, min, med and max
        computed = [{
            "hop": d["hop"], "hosts": list(set([h.strip() for h in d["hosts"] if h != ''])),
            "avg": round(mean(d["speeds"]), 3), "min": min(d["speeds"]), "med": round(median(sorted(d["speeds"])), 3),
            "max": max(d["speeds"]),
        } for i, d in d4c.items() if len(d["speeds"])>0]
        #logger.info('=' * 88)
        traceroute_to_json(jfile, multi_tr_list)
        if args.OUTPUT:
            check_file(cfile)
            traceroute_to_json(cfile, computed)

        dl = [{k: v for k, v in i.items() if k in ('hop', 'speeds',)} for i in d4c.values()]
        dc = pd.DataFrame(dl)

        df = dc.assign(speeds=dc["speeds"]).explode("speeds")

        os.remove(jfile)
        os.remove(jfyl_re)

        #plots graph to selected directory
        if args.GRAPH:
            fig  = px.box(df,y=df["speeds"], x=df["hop"])
            g_file=f'{json_out_dir}{args.TARGET}{os.sep}{args.GRAPH}.pdf'
            fig.write_image(g_file)

        return d4c
    
    

    if args.TEST_DIR:

        path = args.TEST_DIR

        #checks whetehr test directory is existing
        if not os.path.exists(path):
            print("Directory does not exist.")
            sys.exit()
        

        output ={}
        read_output=[]
        jfile, jfyl_re = f'{path} data.json', f'{path} re.json'

        for i, file in enumerate(os.listdir(path)):
            if file:
                file_path = f"{path}{os.sep}{file}"
        
                # call read text file function
                read_output=read_text_file(file_path) 
            output[i]=read_output

        multi_tr_list = process_tr_output(output)

        d4c = multi_tr_pro(multi_tr_list, jfyl_re)
        d4c = {i[0]: i[1] for i in sorted(d4c.items(), key=lambda x: int(x[0]))}

        #computes hop, avg, min, med and max
        computed = [{
            "hop": d["hop"], "hosts": list(set([h.strip() for h in d["hosts"] if h != ''])),
            "avg": round(mean(d["speeds"]), 3), "min": min(d["speeds"]), "med": round(median(sorted(d["speeds"])), 3),
            "max": max(d["speeds"]),
        } for i, d in d4c.items() if len(d["speeds"])>0]
        
        traceroute_to_json(jfile, multi_tr_list)

        #Output traceroute as a json file
        if args.OUTPUT:
            cfile = f'{json_out_dir}{args.TEST_DIR}{os.sep}{args.OUTPUT}.json'
            check_file(cfile)
            traceroute_to_json(cfile, computed)

        dl = [{k: v for k, v in i.items() if k in ('hop', 'speeds',)} for i in d4c.values()]
        df = pd.DataFrame(dl)

        df = df.assign(speeds=df.speeds).explode('speeds')

        os.remove(jfile)
        os.remove(jfyl_re)

        #plots the stat grapgh
        if args.GRAPH:
            fig  = px.box(df,y=df["speeds"], x=df["hop"])
            g_file=f'{json_out_dir}{args.TEST_DIR}{os.sep}{args.GRAPH}.pdf'
            fig.write_image(g_file)

        return d4c
    
    #shows help messages and exit, if there is nothing to run
    if not args.TEST_DIR and not args.TARGET:
        print("\n-h, --help       show this help message and exit \n")


#traceroute accepting optional argument
def parse_trace_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-n', dest='NUM_RUNS', default=1, metavar='NUM_RUNS', type=int, help='Number of times trace+route will run'
    )
    parser.add_argument(
        '-d', dest='RUN_DELAY', default=None, metavar='RUN_DELAY', type=float, help='Number of seconds to wait between two consecutive runs')
    parser.add_argument(
        '-m', dest='MAX_HOPS', default=52, metavar='MAX_HOPS', type=int, help='Number of times traceroute will run')
    parser.add_argument(
        '-o', dest='OUTPUT', default='data', metavar='OUTPUT', type=str, help='Path and name of output JSON file containing the stats')
    parser.add_argument(
        '-t', dest='TARGET', default=None, metavar='TARGET', type=str, help='A target domain name or IP address')
    parser.add_argument(
        '-g', dest='GRAPH', default='graph', metavar='GRAPH', type=str, help='Path and name of output PDF file containing stats graph')
    parser.add_argument(
        '--test', dest='TEST_DIR', default=None, metavar='TEST_DIR', type=str,
        help='Directory containing num_runs text files, each of which contains the output of a traceroute run. '
             'If present, this will override all other options and tcpdump will not be invoked. '
             'Stats will be computed over the  traceroute output stored in the text files')
    args = parser.parse_args()
    return args

#Main Program thread
if __name__ == "__main__":
    main(sys.argv[1:])
