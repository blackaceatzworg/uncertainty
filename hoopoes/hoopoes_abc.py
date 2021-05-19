import os
import tempfile
import numpy as np
import pyabc
import pickle
from time import strftime
import matplotlib.pyplot as plt
#from matplotlib.colors import LinearSegmentedColormap
#mpl.cm.viridis

import pyrun

# Let ID be the timestamp of the history matching run that the prior is based on
id = '210125_151327'

def model(x):
    y = pyrun.run_solo((x['scout_prob'], x['survival_prob']))
    return {'y': y}

def distance(result, data):
    # data is 0
    return pyrun.error(result['y'])


def run():
    prior = pyabc.Distribution(scout_prob=pyabc.RV("uniform", 0, 0.5),
                               survival_prob=pyabc.RV("uniform", 0.9603, 0.0349))

    abc = pyabc.ABCSMC(model, prior, distance)

    db_path = ("sqlite:///" +
               os.path.join(tempfile.gettempdir(), "test.db"))
    observation = 0
    abc.new(db_path, {"data": observation})

    history = abc.run(max_nr_populations=4)

    #TODO change the save method
    # save abc history
    results = []
    for t in range(history.max_t+1):
        df, w = history.get_distribution(m=0, t=t)
        results.append({'df': df, 'w': w})
    with open('results/%s/abc_history.pkl' % id, 'wb') as pfile:
        pickle.dump(results, pfile)
    return history


def plot(history=None):
    if history is None:
        with open('results/%s/abc_history.pkl' % id, 'rb') as pfile:
            results = pickle.load(pfile)
            print(len(results))
            df = results[-1]['df']
            w = results[-1]['w']
    else:
        df, w = history.get_distribution(m=0, t=history.max_t)
    # plot posterior
    fig, ax = plt.subplots()
    pyabc.visualization.plot_kde_2d(
        df, w, x="scout_prob", y="survival_prob",
        xmin=0, xmax=0.5, ymin=0.95, ymax=1,
        ax=ax, shading="auto", cmap='magma')
    plt.xlabel('scouting probability', fontsize=16)
    plt.ylabel('survival probability', fontsize=16)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.show()
    #plt.savefig('results/%s/abc_posterior.pdf' % id)

    if history is not None:
        # plot sampling info
        _, arr_ax = plt.subplots(3)
        pyabc.visualization.plot_sample_numbers(history, ax=arr_ax[0])
        pyabc.visualization.plot_epsilons(history, ax=arr_ax[1])
        pyabc.visualization.plot_effective_sample_sizes(history, ax=arr_ax[2])

        #plt.gcf().set_size_inches((12, 8))
        plt.gcf().tight_layout()
        #plt.show()
        #plt.savefig('results/%s/abc_analysis.pdf' % id)

if __name__ == '__main__':
    history = run()
    # db = shelve.open('results/%s/abc_history.shelf' % id)
    # history = db['history']
    # db.close()
    plot()
