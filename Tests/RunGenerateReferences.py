import subprocess
import argparse
import os
from datetime import date
import shutil
import stat
import sys
import json
import pprint

import RunTestsCollection as rTC
import RunTestsSet as rTS
import MachineConfigs as machine_configs
import Helpers as helpers

def main():

    # Argument Parser.
    parser = argparse.ArgumentParser()

    # Add the Argument for which Test Collection to use.
    parser.add_argument('-tc', '--tests_collection', action='store', help='Specify the Test Collection.')

    # Parse the Arguments.
    args = parser.parse_args()

    # Verify the Tests Collections.
    try:
        json_data = rTC.read_and_verify_tests_collections_source(args.tests_collection)
    
    # Exception handling.
    except rTC.TestsCollectionError as tests_collection_error: 
        print(tests_collection_error.args)
        return None

    # Run the Tests Collections.
    try:
        tests_collections_results = rTC.run_tests_collections(json_data)

    # Exception handling.
    except rTC.TestsCollectionError as tests_collection_error:
        print(tests_collection_error.args)
        return None

    # Verify the Results.
    verify_result = rTC.verify_all_tests_collection_ran_successfully(tests_collections_results)

    if verify_result['Success'] is True :
        for current_test_collections in json_data['Tests Collections']:
            destination_reference_directory = os.path.join(machine_configs.machine_reference_directory, machine_configs.machine_name, json_data['Tests Collections'][current_test_collections]['Source Branch Target'])
            #Act on subdirectories so a machine's vulkan refrences aren't deleted by generating d3d12 references for example
            fullDir = os.path.join(os.getcwd(), 'TestsResults', json_data['Tests Collections'][current_test_collections]['Source Branch Target'], current_test_collections)
            for item in os.listdir(fullDir):
                subDir = os.path.join(destination_reference_directory, item)
                if not os.path.isfile(subDir):
                    helpers.directory_clean_or_make(subDir)
                    print('Moving FROM: ' + fullDir)
                    print('Moving TO: ' + subDir)
                    helpers.directory_copy(fullDir, destination_reference_directory)

    else:
        print("All tests did not run successfully. No references were generated.")

#
if __name__ == '__main__':
    main()
