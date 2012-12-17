#!/usr/bin/env python

from das_utils import *

from optparse import OptionParser
import sys


instance="cms_dbs_ph_analysis_01"

def get_number_events( dataset_name ) :
    """Query DAS to get the number of events in the dataset"""
    query = "dataset dataset="+dataset_name+" instance="+instance
    data = das_query(query)
    which_data = 0
    if len(data) > 1 :
        for d in data :
            print data
        which_data = int(raw_input("Which dataset?"))
    return float(data[which_data]['dataset'][0]['nevents'])

def get_parent( dataset_name ) :
    """Query DAS to get the parent dataset"""
    query = "parent dataset="+dataset_name+" instance="+instance
    data = das_query(query)
    if len(data) > 1 :
        raise RuntimeError('More than one parent matches '+dataset_name)
    return data[0]['parent'][0]['name']

def get_weights( dataset_regex, lumi, xsec, other_filter="") :
    """Get event weights for datasets that match the regex for integrated luminosity lumi (in pb)"""
    query = build_dataset_query(dataset_regex, other_filter)
    datasets = das_query(query)
    if len(datasets) > 1 :
        # Make the user choose which dataset they're referring to
        print "Multiple datasets match input"
        for i, d in enumerate(datasets) :
            if len(d['dataset']) > 1 : 
                raise RuntimeError( "What's going on ?")
            print str(i)+") "+d['dataset'][0]['name']
        dataset_choice = int(raw_input("Select dataset: "))
    else :
        dataset_choice = 0
    dataset_name = datasets[dataset_choice]['dataset'][0]['name']
    print "Dataset "+dataset_name
    parent = get_parent( dataset_name )
    print "Parent "+parent
    parent_nevents = get_number_events( parent )
    print "Weight:", lumi*xsec/parent_nevents

def get_eff_xsec( dataset, xsec):
    """Get the effective cross section for a single event (in pb)"""
    query = build_dataset_query(dataset, "")
    datasets = das_query(query)
    if len(datasets) > 1 :
        # Make the user choose which dataset they're referring to
        print "Multiple datasets match input"
        for i, d in enumerate(datasets) :
            if len(d['dataset']) > 1 : 
                raise RuntimeError( "What's going on ?")
            print str(i)+") "+d['dataset'][0]['name']
        print "Choosing dataset 0"
        dataset_choice = 0
    else :
        dataset_choice = 0
    dataset_name = datasets[dataset_choice]['dataset'][0]['name']
    print "Dataset "+dataset_name
    parent = get_parent( dataset_name )
    print "Parent "+parent
    parent_nevents = get_number_events( parent )
    x_eff = xsec/parent_nevents
    print "xsec_eff:", x_eff
    return x_eff


if __name__ == '__main__':
    # command line options
    usage = "usage: %prog [options] dataset_regex"
    p = OptionParser(description="Get event weights for the dataset", usage=usage)
    p.add_option("-x", "--xsec", dest="xsec", help="Cross-section for the process")
    p.add_option("-l", "--lumi", dest="lumi", help="Integrated luminosity used to calculate weight")
    p.add_option("-f", "--filter", dest="filter", help="Other filter to add to DAS query", default="")
    opts, args = p.parse_args()

    if len(args) < 1 :
        p.print_help()
        sys.exit()

    dataset_regex = args[0]

    get_weights( dataset_regex, float(opts.lumi), float(opts.xsec), opts.filter)
