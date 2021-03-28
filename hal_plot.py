# script to plot hal-records
import sys
import getopt
import pandas as pd
import matplotlib.pyplot as plt


inputfile = ''
filter = ''
try:
    opts, args = getopt.getopt(sys.argv[1:], "hi:f:", ["input=", "filter="])
except getopt.GetoptError:
    print 'hal_plot.py -i <inputfile> -f <filter: zero | constant>'
    sys.exit(2)

for opt, arg in opts:
    if opt == '-h':
        print 'test.py -i <inputfile> -f <filter>'
        sys.exit()
    elif opt in ("-i", "--input"):
        inputfile = arg
    elif opt in ("-f", "--filter"):
        filter = arg

print 'Input file is: ', inputfile
print 'Filter is: ', filter


record = pd.read_csv(inputfile)
record.rename(columns={
    'in0': 'in0_Bli',
    'in1': 'in1_Bla',
    'in2': 'in2_Blo',
}, inplace=True)

record *= 0.8
i = 0
y_string = []
for column in record:
    if(i):
        if(filter == '' and len(args) == 0):
            record[column] += (i-1)
            y_string.append(column)
            i += 1
        elif(filter == 'zero' and record[column].max()):
            record[column] += (i-1)
            y_string.append(column)
            i += 1
        elif(filter == 'constant' and record[column].max() != record[column].min()):
            record[column] += (i-1)
            y_string.append(column)
            i += 1
        elif(column in args):
            record[column] += (i-1)
            y_string.append(column)
            i += 1
    else:
        i += 1


if(len(y_string)):
    record.plot(x="Time", y=y_string, figsize=(14, 10))
    plt.show()
else:
    print "Nothing to plot!"
