import json
import numpy as np
import matplotlib.pyplot as plt

from utils import moving_average
from utils import mean_confidence_interval
from predict import incremental_prediction
from cobweb3 import Cobweb3Tree
from dummy import DummyTree

window = 30 
num_runs = 10 
num_examples = 150

with open('data_files/iris.json') as fin:
    irises = json.load(fin)

############################## GENERATE PREDICTIONS ##########################

naive_accuracy = incremental_prediction(DummyTree(), irises,
                                  run_length=num_examples,
                                  runs=num_runs, attr="class")
cobweb_accuracy = incremental_prediction(Cobweb3Tree(), irises,
                                  run_length=num_examples,
                                  runs=num_runs, attr="class")

############################## PLOT RESULTS ##################################

cobweb_data = [[] for i in range(len(cobweb_accuracy[0]))]
naive_data = [[] for i in range(len(naive_accuracy[0]))]

for run in cobweb_accuracy:
    for i,v in enumerate(run):
        cobweb_data[i].append(v)
for run in naive_accuracy:
    for i,v in enumerate(run):
        naive_data[i].append(v)

cobweb_y = np.array([mean_confidence_interval(l)[0] for l in cobweb_data])
naive_y = np.array([mean_confidence_interval(l)[0] for l in naive_data])

cobweb_y_smooth = moving_average(cobweb_y, window)
naive_y_smooth = moving_average(naive_y, window)

x = np.array([1+i for i in range(len(cobweb_y_smooth))])

cobweb_lower = np.array([mean_confidence_interval(l)[1] for l in
                         cobweb_data])
naive_lower = np.array([mean_confidence_interval(l)[1] for l in
                        naive_data])

cobweb_lower_smooth = moving_average(cobweb_lower, window)
naive_lower_smooth = moving_average(naive_lower, window)

#cobweb_lower_smooth = [max(0, v) for v in cobweb_lower_smooth]
#naive_lower_smooth = [max(0, v) for v in naive_lower_smooth]

cobweb_upper = np.array([mean_confidence_interval(l)[2]
                         for l in cobweb_data])
naive_upper = np.array([mean_confidence_interval(l)[2]
                        for l in naive_data])

cobweb_upper_smooth = moving_average(cobweb_upper, window)
naive_upper_smooth = moving_average(naive_upper, window)

#cobweb_upper_smooth = [min(1, v) for v in cobweb_upper_smooth]
#naive_upper_smooth = [min(1, v) for v in naive_upper_smooth]

plt.fill_between(x, cobweb_lower_smooth, cobweb_upper_smooth, alpha=0.5,
                 facecolor="green")
plt.fill_between(x, naive_lower_smooth, naive_upper_smooth, alpha=0.5,
                 facecolor="red")

plt.plot(x, cobweb_y_smooth, label="COBWEB/3", color="green")
plt.plot(x, naive_y_smooth, label="Naive Predictor", color="red")

plt.gca().set_ylim([0.00,1.0])
plt.gca().set_xlim([1,len(naive_y_smooth)-1])
plt.title("Incremental Iris Classification Prediction Accuracy")
plt.xlabel("# of Training Examples")
plt.ylabel("Avg. Probability of True Class (Accuracy)")
plt.legend(loc=4)

plt.show()
