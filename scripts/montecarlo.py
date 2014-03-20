#!/usr/bin/python

import itertools

import numpy as np

import setiptah.taxitheory.euclidean.distributions as distribs


if __name__ == '__main__' :
    import argparse
    import matplotlib.pyplot as plt
    
    parser = argparse.ArgumentParser()
    parser.add_argument( 'distrib_key', type=str ) #, default='PairUniform2' )
    args = parser.parse_args()
    
    distr = distribs.distributions[ args.distrib_key ]
    
    total = 0.
    c = itertools.count(1)
    for n in c :
        dem = distr.sample()
        total += distr.distance( distr.getTail(dem), distr.getHead(dem) )
        
        print total / n, n
        
    
    
    