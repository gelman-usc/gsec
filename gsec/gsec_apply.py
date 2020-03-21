import sys, os, argparse
import subprocess
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError
ROOT = os.path.dirname(os.getcwd())


import csv
import pickle
import sklearn
import pandas as pd
from pathlib import Path


def apply(
    pos_strat,
    pos_org,
    neg_strat,
    neg_org,
    file
):
    print('python3 gsec.py pos_strat pos_org neg_strat neg_org fastq_file')

    """
    pos_strat: (str) strategy for positive set
    pos_org: (str) organism for positive set
    neg_strat: (str) strategy for negative set
    neg_org: (str) organism for negative set
    file: (str) fastq file to be processed
    """

    # TODO will have to change for when there is an actual models.csv file
    # read csv, and split on "," the line
    
    csv_file = csv.reader(open(os.path.join(ROOT, 'gsec/models.csv')), delimiter=",")


    # loop through list of models
    for row in csv_file:
        print(row)
        # if current rows first and second col match pos & neg strats, use that model
        if pos_strat == row[0] and neg_strat == row[1]:
            print(row)
            model_pkl = row[2]
            k_vals = row[3]
            classifier = row[4]
    
    # open model
    with open(model_pkl, 'rb') as model_pkl:
        model = pickle.load(model_pkl)  

    # count kmers and create dataframe with result

    cmd = count(6, 1000, file)
    a = subprocess.Popen(cmd, stdout=subprocess.PIPE)

    if sys.version_info[0] < 3: 
        from StringIO import StringIO
    else:
        from io import StringIO

    b = StringIO(a.communicate()[0].decode('utf-8'))

    df = pd.read_csv(b, sep=",")

    # out = os.path.join(ROOT, 'temp')
    # df = pd.DataFrame()
    
    # basepath_bs = count(6, 1000, file, out)
    # entry = Path(basepath_bs)
    # print(entry)
    # if os.stat(entry).st_size != 0:
    #     df = file_shell(df,entry,0)
    # df.dropna(inplace=True)

    print(df)

    result = model.predict(df)  
    print(result)
    

    return 0; # success

    
def count(k, limit, fastq):
    """
    k (int): max kmer to count
    limit (int): limit number of reads to count for given file
    fastq (str): fastq file for read
    out (str): directory to save files
    """

    # check if stream_kmers is compiled
    if ('stream_kmers') not in os.listdir(os.path.join(ROOT, 'utils')):
        # compile
        comp = 'g++ {} -o {}'.format(
            os.path.join(ROOT, 'utils', 'stream_kmers.cpp'),
            os.path.join(ROOT, 'utils', 'stream_kmers')
            )
        print('COMPILING....')
        print(comp)
        subprocess.call(comp, shell=True)

    # shell commands to run
    # filename = os.path.join(out, '{}.txt'.format(fastq[:-6]))
    count_path = os.path.join(ROOT, 'utils', 'stream_kmers')
    fastq = os.path.join(ROOT, 'utils', fastq)
    count = "{} {} {}".format(count_path,
                                     str(k),
                                     str(limit))
    full = "cat " + fastq + " | " + count
    # subprocess.call(full, shell=True)
    return full

def file_shell(df,fname,ind):
    """
    helper function to append new data
    """
    df1 = pd.read_csv(fname, sep='\t', header=None)
    df1.set_index(0, inplace=True)
    df2 = df1.transpose()
    df2.index = [ind]
    df3 = df.append(df2)
    return df3

if __name__ == '__main__':
    main()


