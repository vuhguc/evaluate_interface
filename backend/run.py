import pandas as pd
import numpy as np

import backend.clustering as clustering
import backend.evaluation as evaluation

import os



def run_cluster(data):
	valid = True
	status_message = {'status':'success', 'message':''}
	validator = {}

	try:
		df = pd.read_csv(filepath_or_buffer=data.file.file)
		idx = df.iloc[:, 0].tolist()
		content = df.iloc[:, 2].tolist()
		human_label = df.iloc[:, 3].tolist()
		validator['file'] = True
	except:
		valid = False
		status_message['status'] = 'failure'
		status_message['message'] += 'Uploaded file format is not valid.\n'
		validator['file'] = False

	if data.auto_select_num_clusters != "True" and data.auto_select_num_clusters != "False":
		valid = False
		status_message['status'] = 'failure'
		status_message['message'] += 'Number of cluster selection must be either auto or manual.\n'
	auto_select_num_clusters = (data.auto_select_num_clusters == "True")

	if not auto_select_num_clusters:
		try:
			num_clusters = int(data.num_clusters)
			if num_clusters <= 0:
				raise Exception()
			validator['num_clusters'] = True
		except:
			valid = False
			status_message['status'] = 'failure'
			status_message['message'] += 'Number of clusters must be a positive integer.\n'
			validator['num_clusters'] = False

	try:
		max_features = int(data.max_features)
		if max_features <= 0:
			raise Exception()
		validator['max_features'] = True
	except:
		valid = False
		status_message['status'] = 'failure'
		status_message['message'] += 'Max features must be a positive integer.\n'
		validator['max_features'] = False

	try:
		min_df = float(data.min_df)
		if min_df < 0 or min_df > 1:
			raise Exception()
		validator['min_df'] = True
	except:
		valid = False
		status_message['status'] = 'failure'
		status_message['message'] += 'Min DF must be a real number between 0 and 1.\n'
		validator['min_df'] = False

	try:
		max_df = float(data.max_df)
		if max_df < 0 or max_df > 1:
			raise Exception()
		validator['max_df'] = True
	except:
		valid = False
		status_message['status'] = 'failure'
		status_message['message'] += 'Max DF must be a real number between 0 and 1.\n'
		validator['max_df'] = False

	if validator['min_df'] and validator['max_df'] and min_df > max_df:
		valid = False
		status_message['status'] = 'failure'
		status_message['message'] += 'Min DF must not be greater than Max DF.\n'
		validator['min_df'] = False
		validator['max_df'] = False

	if data.use_idf != "True" and data.use_idf != "False":
		valid = False
		status_message['status'] = 'failure'
		status_message['message'] += 'Use IDF must be either True or False.\n'
	use_idf = (data.use_idf == "True")

	try:
		min_ngram = int(data.min_ngram)
		if min_ngram <= 0:
			raise Exception()
		validator['min_ngram'] = True
	except:
		valid = False
		status_message['status'] = 'failure'
		status_message['message'] += 'Min n-gram size must be a positive integer.\n'
		validator['min_ngram'] = False

	try:
		max_ngram = int(data.max_ngram)
		if max_ngram <= 0:
			raise Exception()
		validator['max_ngram'] = True
	except:
		valid = False
		status_message['status'] = 'failure'
		status_message['message'] += 'Max n-gram size must be a positive integer.\n'
		validator['max_ngram'] = False

	if validator['min_ngram'] and validator['max_ngram'] and min_ngram > max_ngram:
		valid = False
		status_message['status'] = 'failure'
		status_message['message'] += 'Min n-gram size must not be greater than Max n-gram size.\n'
		validator['min_ngram'] = False
		validator['max_ngram'] = False

	if not valid:
		return valid, status_message, validator, None, None, None, None, None, None

	linkage_matrix = clustering.generate_linkage_matrix(
		content=content,
		max_features=max_features,
		min_df=min_df,
		max_df=max_df,
		use_idf=use_idf,
		min_ngram=min_ngram,
		max_ngram=max_ngram,
	)
	if auto_select_num_clusters:
		num_clusters = clustering.auto_select_num_clusters(linkage_matrix=linkage_matrix)
	machine_label = clustering.generate_clustering(
		linkage_matrix=linkage_matrix,
		num_clusters=num_clusters,
	)
	clustering_table = pd.DataFrame(
		data={df.columns.values[3]:human_label, 'Machine Labels':machine_label},
		index=idx,
	)
	clustering_table.index.name = df.columns.values[0]

	dendrogram_path = 'static/dendrogram.png'
	clustering.plot_dendrogram(
		linkage_matrix=linkage_matrix,
		num_clusters=num_clusters,
		idx=idx,
		dendrogram_path=dendrogram_path,
	)

	evaluation_functions = [
		evaluation.purity,
		evaluation.rand_index,
		lambda human_label, machine_label: evaluation.f_score(human_label=human_label, machine_label=machine_label, beta=0.5),
		lambda human_label, machine_label: evaluation.f_score(human_label=human_label, machine_label=machine_label, beta=1),
		lambda human_label, machine_label: evaluation.f_score(human_label=human_label, machine_label=machine_label, beta=1.5),
	]
	evaluation_data = evaluation.generate_evaluation(
		evaluation_functions=evaluation_functions,
		human_label=human_label,
		machine_labels=[machine_label],
	)
	evaluation_table = pd.DataFrame(
		data=np.array(evaluation_data),
		index=['Purity', 'Rand Index', 'F Score (beta=0.5)', 'F Score (beta=1)', 'F Score (beta=1.5)'],
		columns=['Hierarchical Clustering'],
	)
	evaluation_row_tooltips = [
		evaluation.purity_tooltips(),
		evaluation.rand_index_tooltips(),
		evaluation.f_score_tooltips(),
		evaluation.f_score_tooltips(),
		evaluation.f_score_tooltips(),
	]

	return valid, status_message, validator, auto_select_num_clusters, num_clusters, clustering_table, dendrogram_path, evaluation_table, evaluation_row_tooltips



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
		evaluation_table = pd.read_csv('evaluation_tables/' + data.filename + '_evaluation_table.csv')
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