import pandas as pd
import numpy as np

import modules.evaluation as evaluation

import os



def run_evaluate(data):
	valid = True
	status_message = {'status':'success', 'message':''}
	validator = {}

	try:
		df = pd.read_csv('new_aa_csvs/' + data.filename + '.csv')
		idx = df.iloc[:, 0].tolist()
		human_label = df.iloc[:, 1].tolist()
		machine_labels = [df.iloc[:, i].tolist() for i in range(2, len(df.columns))]
		validator['file'] = True
	except:
		valid = False
		status_message['status'] = 'failure'
		status_message['message'] += 'Uploaded file format is not valid.\n'
		validator['file'] = False

	if not valid:
		return valid, status_message, validator, None, None, None

	evaluation_functions = [
		evaluation.purity,
		evaluation.rand_index,
		evaluation.adjusted_rand_index,
		lambda human_label, machine_label: evaluation.f_score(human_label=human_label, machine_label=machine_label, beta=0.5),
		lambda human_label, machine_label: evaluation.f_score(human_label=human_label, machine_label=machine_label, beta=1),
		lambda human_label, machine_label: evaluation.f_score(human_label=human_label, machine_label=machine_label, beta=1.5),
	]
	evaluation_function_names = [
		'Purity',
		'Rand Index',
		'Adjusted Rand Index',
		'F Score (beta=0.5)',
		'F Score (beta=1)',
		'F Score (beta=1.5)'
	]
	clustering_names = df.columns.values[2:].tolist()
	if os.path.isfile('evaluation_tables/' + data.filename + '_evaluation_table.csv'):
		evaluation_table = pd.read_csv('evaluation_tables/' + data.filename + '_evaluation_table.csv', index_col=0)
		evaluation_data = evaluation_table.values.tolist()
		for row in evaluation_data:
			evaluation_data = evaluation_data[1:]
		print(evaluation_data)
	else:
		evaluation_data = evaluation.generate_evaluation(
			evaluation_functions=evaluation_functions,
			human_label=human_label,
			machine_labels=machine_labels,
		)
		evaluation_table = pd.DataFrame(
			data=np.array(evaluation_data),
			index=evaluation_function_names,
			columns=clustering_names,
		)
		evaluation_table.to_csv('evaluation_tables/' + data.filename + '_evaluation_table.csv')
	evaluation_row_tooltips = [
		evaluation.purity_tooltips(),
		evaluation.rand_index_tooltips(),
		evaluation.adjusted_rand_index_tooltips(),
		evaluation.f_score_tooltips(),
		evaluation.f_score_tooltips(),
		evaluation.f_score_tooltips(),
	]

	visualization_paths = [
		'static/' + data.filename + '_visualization_purity.png',
		'static/' + data.filename + '_visualization_rand_index.png',
		'static/' + data.filename + '_visualization_adjusted_rand_index.png',
		'static/' + data.filename + '_visualization_f_score_beta_05.png',
		'static/' + data.filename + '_visualization_f_score_beta_1.png',
		'static/' + data.filename + '_visualization_f_score_beta_15.png'
	]
	if not os.path.isfile(visualization_paths[0]):
		evaluation.visualize_evaluation(
			evaluation_data=evaluation_data,
			evaluation_function_names=evaluation_function_names,
			clustering_names=clustering_names,
			visualization_paths=visualization_paths,
		)

	return valid, status_message, validator, evaluation_function_names, evaluation_table, evaluation_row_tooltips, visualization_paths