#!/usr/bin/env python

"""
Tool to merge files in a given dataset(s)
"""

import das
import commands
import os
import tempfile

instance = "cms_dbs_ph_analysis_01"

def build_dataset_query(dataset_regex, other_filter="") :
    """Build the query to send to DAS"""
    query = "dataset dataset="
    query += dataset_regex
    query += " instance="
    query += instance
    query += " "+other_filter
    return query

def build_file_query(dataset, other_filter="") :
    """Build the query to send to DAS"""
    query = "file dataset="
    query += dataset
    query += " instance="
    query += instance
    query += " "+other_filter
    return query

def make_file_list( file_list ) :
    """Make a temporary file that contains a list of the files in filelist. Returns the name of the file."""
    filename = ""
    with tempfile.NamedTemporaryFile(delete=False) as f: #Need to delete the file manually when we're done with it
        filename = f.name
        for file_name in file_list :
            f.write(file_name)
            f.write("\n")
    return filename
        

def merge_files( file_list, output_file) :
    """Run the command to merge the files"""
    command = 'edmCopyPickMerge'
    command += " inputFiles_load="
    listfilename = make_file_list( file_list )
    command += listfilename
    command += " outputFile="+output_file
    success = commands.getstatusoutput(command)
    os.remove(listfilename)
    if success[0] :
        print command
        print success[1]
        raise RuntimeError('edmCopyPickMerge failed!')

def merge_files_from_dataset( dataset_name, directory ) :
    """Merge all files in the dataset into one local file"""
    print "Merging dataset "+dataset_name
    files = get_files_from_dataset( dataset_name )
    output_file = os.path.join(directory, dataset_name.replace("/","_")[1:]+".root")
    merge_files( files, output_file)

def get_files_from_dataset( dataset_name ) :
    """Return a list of all files in the given dataset"""
    query = build_file_query( dataset_name )
    das_results = das_query( query )
    results = []
    for result in das_results :
        if type(result['file']) == type([]) :
            results.append(result['file'][0]['name'])
        elif type(result['file']) == type({}) :
            results.append(result['file']['name'])
    return results

def das_query( query ) :
    """Run the DAS query"""
    host = "https://cmsweb.cern.ch"
    page = 0
    limit = 0
    result = das.get_data(host, query, page, limit, False) #set last argument to True for debug
    return eval(result)['data'] # get_data returns a string that we need to eval
    
def combine(dataset_regex, directory="./", other_filter="") :
    """Combine all files into one file for each dataset that matches the regex"""
    query = build_dataset_query(dataset_regex, other_filter)
    data = das_query(query)
    for datum in data :
        merge_files_from_dataset(datum['dataset'][0]['name'], directory)
