# Computer-Network-Group-Project
Commang line traceroute using python
Group Member: 
Adetayo Okunoye

Title: 
To develop a command line tool for trace-route, parsing its output, and performing a statistical analysis 
of the trace-route results.

Objective:
This project will require using Python to create a command line tool that automatically executes traceroute multiple times towards a target domain name or IP address specified as command line parameter. 
Based on multiple trace-route executions, the program will need to derive latency statistics for each hop 
between the trace-route client and the target machine.
To allow for repeatable tests, the program will also allow reading pre- generated trace-route output 
traces stored on multiple text files (one text output trace per file). Based on this pre-generated output, 
the program will need to compute the latency statistics as for the case of live trace-route execution.

Description:
My command-line tool will need to support the following CLI arguments
usage: trstats.py [-h] [-n NUM_RUNS] [-d RUN_DELAY] [-m MAX_HOPS]
 -o OUTPUT -g GRAPH [-t TARGET] [--test TEST_DIR]
Run trace-route multiple times towards a given target host
optional arguments: 
-h, --help show this help message and exit
-n NUM_RUNS Number of times trace-route will run
-d RUN_DELAY Number of seconds to wait between two consecutive runs 
-m MAX_HOPS Number of times trace-route will run
-o OUTPUT Path and name of output JSON file containing the stats
-g GRAPH Path and name of output PDF file containing stats graph
-t TARGET A target domain name or IP address (required if --test
 is absent)
 
--test TEST_DIR Directory containing num_runs text files, each of which contains the output of a 
traceroute run. If present, this will override all other options and traceroute will not be invoked. Stats 
will be computed over the traceroute output stored in the text files
Essentially, the main task in this project is to write a Python3 wrapper around traceroute, so that you 
can programmatically run traceroute multiple times, read the latency statistics output by every run, and 
build a distribution of latency values over which to compute the required statistics. 
For instance, the main output of my program should be a file in JSON format that looks like this 
example:
[{'avg': 0.645,
'hop': 1,
'hosts': [['172.17.0.1', '(172.17.0.1)']], 'max': 2.441,
'med': 0.556,
'min': 0.013},
{'avg': 6.386,
'hop': 2,
'hosts': [['testwifi.here', '(192.168.86.1)']], 'max': 16.085,
'med': 5.385,
'min': 3.108},
{'avg': 26.045,
'hop': 3,
'hosts': [['96.120.4.5', '(96.120.4.5)']], 'max': 65.753,
'med': 20.298,
'min': 12.287},
{'avg': 26.819,
'hop': 4,
'hosts': [['96.110.205.9', '(96.110.205.9)']], 'max': 65.847,
'med': 20.51,
'min': 17.444},
...
{'avg': 168.84,
'hop': 18,
'hosts': [['124.83.228.222', '(124.83.228.222)']], 'max': 172.869,
'med': 166.869,
'min': 166.781}]

Where avg = average hop latency, max = maximum hop latency, med = median hop latency, min = 
minimum hop latency). Also, the program should will output a boxplot graph showing the latency
