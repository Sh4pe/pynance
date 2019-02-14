from __future__ import print_function
import unittest
import sys
import glob
import os.path


def task_test():
    return {
        'actions': ['pytest --cov=./ --doctest-modules'],
        'verbosity': 2
    }


def task_graphviz():
    graph_dir = os.path.join(*["docs", "graphs"])
    graph_dot_files = glob.glob(os.path.join(graph_dir, "*.dot"))

    for graph_dot_file in graph_dot_files:
        base = os.path.basename(graph_dot_file)
        graph_name = os.path.splitext(base)[0]
        graph_image_file = os.path.join(graph_dir, "png", graph_name+".png")

        yield {
            'name': graph_name,
            'actions': ['dot -Tpng %s -o %s' % (graph_dot_file, graph_image_file)]
        }


def task_dash_app():
    return {
        'actions': [['python', 'run_dash.py']],
        'verbosity': 2
    }


def task_notebook():
    return {
        'actions': [['jupyter', 'notebook', '--notebook-dir=notebooks']],
        'verbosity': 2
    }
