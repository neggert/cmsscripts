import das
import json

instance="cms_dbs_ph_analysis_01"

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

def get_files_from_dataset( dataset_name ) :
    """Return a list of all files in the given dataset"""
    query = build_file_query( dataset_name )
    das_results = das_query( query )
    results = []
    for result in das_results :
        if type(result['file']) == type([]) :
            results.append(result['file'][0]['name'].encode('ascii', 'replace'))
        elif type(result['file']) == type({}) :
            results.append(result['file']['name'].encode('ascii', 'replace'))
    return results

def das_query( query ) :
    """Run the DAS query"""
    host = "https://cmsweb.cern.ch"
    page = 0
    limit = 0
    result = das.get_data(host, query, page, limit, False) #set last argument to True for debug
    return json.loads(result)['data'] # get_data returns a string that we need to eval
