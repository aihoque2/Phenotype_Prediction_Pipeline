"""module for defining a class for running phenotype prediction jobs"""
from math import isnan
import os
from zipfile import ZipFile, ZIP_DEFLATED

import requests
import time
import pandas as pd
import yaml
import sys

"""
THESE ARE THE LIBRARIES THAT DON'T NEEED TO BE USED AT THE MOMENT (BUT MIGHT BE NEEDED LATER ON)

from nest.nest_py.jobs.knoweng.chronos_job import ChronosJob
from nest_py.jobs.db_utils import create_sc_record, get_file_record
from nest_py.jobs.knoweng.networks import get_merged_network_info
from nest_py.jobs.knoweng.data_cleanup import \
    DataCleanupJob, PipelineType, get_dict_from_id_to_name, \
    get_cleaned_spreadsheet_relative_path, get_gene_names_map_relative_path
"""

class PhenotypePredictionJob():
	"""subclass of ChronosJobs that handles phenotype prediction"""
	def __init__(self):
		pass	


	def runJobs(self):
		self.cleanup()
                run_data = {
                        "schedule": "R1//P3M",
                        "name": "Phenotype-prediction test",
                        "container":
                        {
                                "type": "DOCKER",
                                "image": "knowengdev/phenotype_prediction_pipeline:06_02_2017",
                                "volumes": [{"containerPath": "/mnt/knowdev/aihoque2", "hostPath": "/mnt/knowdev/aihoque2", "mode": "RW"}]
                        },
			"command": "cd /home/test && make env_setup && python3 ../src/phenotype_prediction.py -run_dir ./run_dir -run_file BENCHMARK_2_ElasticNet.yml && cp -r ./run_dir/results/* /mnt/knowdev/aihoque2/test_results && chmod 770 /mnt/knowdev/aihoque2/test_results/*",

                        "retries": "1",
                        "cpus": "1",
                        "mem": "500"
                }

		requests.post('http://knowdev.knowhub.org:4400/scheduler/iso8601', json=run_data)
		MAX_TIME = 60*5 # 10 minutes
		done = False
		start_time = time.time()
		exit_code = 1 # failure; we'll set it to 0 if success
		while(True):
			if self.isDone():
				exit_code = 0
        			break
			elif time.time() - start_time > MAX_TIME:
        			print('Failure: runtime exceeded MAX_TIME')
        			break
		self.cleanup()
		if exit_code == 0:
			print('Test complete: SUCCESS')
		else:
			print('Test complete: FAILURE')
		sys.exit(exit_code)


	def isDone(self):
		retval = False
		for name in os.listdir('/mnt/knowdev/aihoque2/test_results'):
			if name.startswith('features_test_clean'):
				retval = True
		return retval
	
	def cleanup(self):
                for name in os.listdir('/mnt/knowdev/aihoque2/test_results'):
                        if name.startswith('features_test_clean'):
				os.remove(os.path.join('/mnt/knowdev/aihoque2/test_results', name))


if __name__ == '__main__':
	PhenotypePredictionJob().runJobs()
