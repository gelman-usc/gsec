# create_model_new.py: This script takes an input of the data types
# from the query, creates a dataframe with the two datasets, and
# trains models to classify the two datatypes
#
# Authors: Nicolas Perez, Isaac Gelman, Natalie Abreu, Shannon Brownlee,
# Tomas Angelini, Laura Cao, Shreya Havaldar
#
# This software is Copyright (C) 2020 The University of Southern
# California. All Rights Reserved.
#
# Permission to use, copy, modify, and distribute this software and
# its documentation for educational, research and non-profit purposes,
# without fee, and without a written agreement is hereby granted,
# provided that the above copyright notice, this paragraph and the
# following three paragraphs appear in all copies.
#
# Permission to make commercial use of this software may be obtained
# by contacting:
#
# USC Stevens Center for Innovation
# University of Southern California
# 1150 S. Olive Street, Suite 2300
# Los Angeles, CA 90115, USA
#
# This software program and documentation are copyrighted by The
# University of Southern California. The software program and
# documentation are supplied "as is", without any accompanying
# services from USC. USC does not warrant that the operation of the
# program will be uninterrupted or error-free. The end-user
# understands that the program was developed for research purposes and
# is advised not to rely exclusively on the program for any reason.
#
# IN NO EVENT SHALL THE UNIVERSITY OF SOUTHERN CALIFORNIA BE LIABLE TO
# ANY PARTY FOR DIRECT, INDIRECT, SPECIAL, INCIDENTAL, OR
# CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF THE
# USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF THE UNIVERSITY
# OF SOUTHERN CALIFORNIA HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH
# DAMAGE. THE UNIVERSITY OF SOUTHERN CALIFORNIA SPECIFICALLY DISCLAIMS
# ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE. THE SOFTWARE PROVIDED

import pandas as pd
import numpy as nump
import os
from pathlib import Path
import time

# File paths
model_dir = os.path.dirname(os.path.realpath(__file__))

"""Assumption made on file directories:
 this script is in the same directory as genomics_data folder """

def clear_errors():
    """
    Clear previous errors from file so only new errors from current run
    are recorded
    """
    error_file = open(os.path.join(model_dir, "errors.txt"), "w+")
    error_file.write("project_name, file_name, error_type")
    error_file.close()

def dir_check():
    """
    Check directories
    """
    print("model directory: ", model_dir)
    print("data directory: ", data_dir)

def calculate_dimension(kmer_list):
    """
    Function takes list of kmers chosen for the dataset
    and calculates how many rows the corresponding txt files
    should have when processing
    """
    total_count = 0
    for i in kmer_list:
        total_count += pow(4,i)

    return total_count


def append_experiment(df,fname, kmer_count, label):
    """
    Append experiment of name "fname" to dataframe
    If number of rows in txt file doesn't match
    appropriate number of kmers, don't append.
    """
    df_new = pd.read_csv(fname, sep='\t', header=None)

    # case 1: kmer counts are missing
    if ((df_new.shape)[0] != kmer_count):
        error_file = open("errors.txt", "a+")
        error_file.write("\r%s, missing_kmers" % (fname.name))
        error_file.close()
        return df

    # case 2: all kmer counts are 0
    elif (df_new.iloc[:, 1].sum() == 0):
            error_file = open("errors.txt", "a+")
            error_file.write("\r%s, kmers_zeros" % (fname.name))
            error_file.close()
            return df
    else:
    # case 3: correct read
        df_new.set_index(0, inplace=True)
        df_new = df_new.transpose()
        df_new.index = [label]
        return df.append(df_new)




def load_data(data_name, df, kmer_count, label, data_dir):
    """
    Function loads a certain type of data
    for each experiment, call append_experiment
    append_experiment returns a dataframe with
    kmer data of most recent experiment
    appended to it
    """

    experiment_list = Path(os.path.join(data_dir, data_name))
    for experiment in experiment_list.iterdir():
        extension = experiment.suffix
        if os.stat(str(experiment)).st_size != 0 and extension == '.txt':
            df = append_experiment(df,
            experiment,
            kmer_count,
            label)
        else:
            error_file = open("errors.txt", "a+")
            error_file.write("\r%s, empty_file" % (experiment.name))

    return df

def create_dataframe(data_dir, first_data_type, second_data_type, kmer_list):
    """
    Function takes inputs the two data types to create the
    dataset from (e.g. wgs vs. rna), and returns a dataframe
    with the kmer counts of both datatypes
    """
    clear_errors()
    df = pd.DataFrame()
    kmer_count = calculate_dimension(kmer_list)

    df = load_data(first_data_type, df, kmer_count, 0, data_dir)
    # if(df.shape[0] < 20):
    #     print("Less than 20 counts in %s data file. Aborting" % first_data_type)
    #     return

    df = load_data(second_data_type, df, kmer_count, 1, data_dir)
    # if(df.shape[0] < 40):
    #     print("Less than 20 counts in %s data file. Aborting" %
    #     second_data_type)
    #     return

    print(df.shape)

    pd.set_option('display.max_rows', 900)

    print(df)

    return df

def efficiency_check(first_data_type, second_data_type, kmer_list, n):
    """
    Function runs the dataframe creation process n times and generates
    average runtime stats
    """
    abs_avg = 0
    abs_exp_per_min = 0

    for i in range(0,n):
        tmp_df = pd.DataFrame()
        start_time = time.time()
        tmp_df = create_dataframe(first_data_type, second_data_type, kmer_list)
        end_time = float(time.time() - start_time)
        num_experiments = float(len(tmp_df.index))

        avg = end_time / num_experiments
        exp_per_min = 1 / avg * 60

        abs_avg += avg
        abs_exp_per_min += exp_per_min

    abs_avg = abs_avg / n
    abs_exp_per_min = abs_exp_per_min / n

    print("Average loading time: %f seconds per experiment" % avg)
    print("Experiments to be processed per minute: %f" % exp_per_min)
