import unittests
import sys

def task_test():
    def integration_test_action():
        # printing to stderr so that doit does not capture the output
        print("### Integration tests are not yet implemented ###", file=sys.stderr)

    for kind, action in [('unit', unittests.run_all_unit_tests), ('integration', integration_test_action)]:
        yield {
            'name': kind,
            'actions': [action]
        }