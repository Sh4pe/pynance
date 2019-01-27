import unittests
import sys
import glob
import os.path

def task_test():
    def integration_test_action():
        # printing to stderr so that doit does not capture the output
        print("### Integration tests are not yet implemented ###", file=sys.stderr)

    for kind, action in [('unit', unittests.run_all_unit_tests), ('integration', integration_test_action)]:
        yield {
            'name': kind,
            'actions': [action]
        }

def task_graphviz():
    graph_dir = "docs\\graphs\\"
    graph_dot_files = glob.glob(os.path.join(graph_dir, "*.dot"))

    for graph_dot_file in graph_dot_files:
        base = os.path.basename(graph_dot_file)
        graph_name = os.path.splitext(base)[0]
        graph_image_file = os.path.join(graph_dir, "png", graph_name+".png") 

        yield {
            'name': graph_name, 
            'actions': ['dot -Tpng %s -o %s' % (graph_dot_file, graph_image_file)]
        }

def task_notebook():
    return {
        'actions': [['jupyter', 'notebook', '--notebook-dir=notebooks']],
        'verbosity': 2
    }
