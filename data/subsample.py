import numpy as np
import sys

def subsample_file(filename, Nsub, Nheader=1):
    output_filename = filename.replace('.csv','_r%d.csv' % Nsub)

    inf = open(filename,'r')
    outf = open(output_filename,'w')

    for Nread, line in enumerate(inf):
        if (Nread < Nheader) | ( (Nread-Nheader) % Nsub == 0 ):
            outf.write(line)

    inf.close()
    outf.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Subsample a text file.')
    parser.add_argument('input_files', nargs='+',
                        help='input file(s) to subsample')
    parser.add_argument('--Nsub', type=int, default=100,
                        help='subsample factor')
    parser.add_argument('--Nheader', type=int, default=1,
                        help='number of header lines to directly copy')
    args = parser.parse_args()

    for fn in args.input_files:
        subsample_file(fn,args.Nsub,Nheader=args.Nheader)
        
