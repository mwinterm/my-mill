#script to plot hal-records
import pandas as pd
import matplotlib.pyplot as plt

record = pd.read_csv("hal_record0.csv")

record_size = record.shape
record *= 0.8

y_string = []
for i in range(record_size[1]-1):
    record["in" + str(i)] += i
    y_string.append("in" + str(i))

record.plot(x="Time", y=y_string)

