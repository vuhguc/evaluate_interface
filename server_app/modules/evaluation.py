import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sklearn

def purity(human_label, machine_label):

	# filter out all points without human label or machine label
	human_label, machine_label = zip(*filter(lambda human_machine: not pd.isna(human_machine[0]) and not pd.isna(human_machine[1]), zip(human_label, machine_label)))

	# human_machine_counter is a dictionary of form {(i, j) : k}
	# k is number of points having human label i and machine label j
	human_machine_counter = {}

	# human_set is set of unique human labels
	human_set = set()

	# machine_set is set of unique machine labels
	machine_set = set()

	# num_correct_assignments is number of points correctly assigned to major human labels in their machine labels
	num_correct_assignments = 0

	# Iterate over all points to build up human_machine_counter, human_set, and machine_set
	for human, machine in zip(human_label, machine_label):
		if (human, machine) not in human_machine_counter:
			human_machine_counter[(human, machine)] = 0
		human_machine_counter[(human, machine)] += 1
		human_set.add(human)
		machine_set.add(machine)

	# With each machine label, find human label appearing most and add number of appearances to num_correct_assignments
	for machine in machine_set:
		max_appearances = 0
		for human in human_set:
			if (human, machine) in human_machine_counter:
				max_appearances = max(max_appearances, human_machine_counter[(human, machine)])
		num_correct_assignments += max_appearances

	# Return purity value computed by num_correct_assignments / number of points
	return float(num_correct_assignments) / len(human_label)



def tp_tn_fp_fn(human_label, machine_label):

	# filter out all points without human label or machine label
	human_label, machine_label = zip(*filter(lambda human_machine: not pd.isna(human_machine[0]) and not pd.isna(human_machine[1]), zip(human_label, machine_label)))

	# Initialize tp, tn, fp, fn
	tp, tn, fp, fn = 0, 0, 0, 0

	# human_counter is a dictionary of form {i : k}
	# k is number of points having human label i
	human_counter = {}

	# machine_counter is a dictionary of form {j : k}
	# j is number of points having machine label j
	machine_counter = {}

	# human_machine_counter is a dictionary of form {(i, j) : k}
	# k is number of points having human label i and machine label j
	human_machine_counter = {}

	# Iterate over all points to build up human_counter, machine_counter, and human_machine_counter
	for human, machine in zip(human_label, machine_label):
		if human not in human_counter:
			human_counter[human] = 0
		if machine not in machine_counter:
			machine_counter[machine] = 0
		if (human, machine) not in human_machine_counter:
			human_machine_counter[(human, machine)] = 0
		human_counter[human] += 1
		machine_counter[machine] += 1
		human_machine_counter[(human, machine)] += 1

	# Iterate over all points. With each point, increase tp, tn, fp, and fn by number of corresponding pairs having one element being currently iterated point
	# Let currently iterated point have human label i, machine label j, then:
	# tp += |(i, j)| - 1
	# tn += number of points - |i| - |j| + |(i, j)|
	# fp += |j| - |(i, j)|
	# fn += |i| - |(i, j)|
	for human, machine in zip(human_label, machine_label):
			tp += human_machine_counter[(human, machine)] - 1
			tn += len(human_label) - human_counter[human] - machine_counter[machine] + human_machine_counter[(human, machine)]
			fp += machine_counter[machine] - human_machine_counter[(human, machine)]
			fn += human_counter[human] - human_machine_counter[(human, machine)]

	# Divided tp, tn, fp, and fn by 2 because both pairs (x, y) and (y, x) are counted
	tp, tn, fp, fn = tp / 2, tn / 2, fp / 2, fn / 2

	return (tp, tn, fp, fn)



def rand_index(human_label, machine_label):
	tp, tn, fp, fn = tp_tn_fp_fn(human_label=human_label, machine_label=machine_label)
	return float(tp + tn) / (tp + tn + fp + fn)



def adjusted_rand_index(human_label, machine_label):
	human_label, machine_label = zip(*((human, machine) for human, machine in zip(human_label, machine_label) if not pd.isna(human) and not pd.isna(machine)))
	return sklearn.metrics.cluster.adjusted_rand_score(human_label, machine_label)



def f_score(human_label, machine_label, beta):
	tp, tn, fp, fn = tp_tn_fp_fn(human_label=human_label, machine_label=machine_label)
	p = float(tp) / (tp + fp)
	r = float(tp) / (tp + fn)
	return ((beta ** 2 + 1) * p * r) / (beta ** 2 * p + r)



def purity_tooltips():
	return 'Purity function is computed by the sum of appearances of the most common human label in each machine label divided by the number of points.'



def rand_index_tooltips():
	return 'Rand Index is computed by (TP + TN) / (TP + TN + FP + FN) where:\n\n' +\
		   'TP is true positive - the number of pairs of points (x, y) such that x and y have same machine label and same human label.\n\n' +\
		   'TN is true negative - the number of pairs of topics (x, y) such that x and y have different machine labels and different human labels.\n\n' +\
		   'FP is false positive - the number of pairs of points (x, y) such that x and y have same machine label and different human labels.\n\n' +\
		   'FN is false negative - the number of pairs of points (x, y) such that x and y have different machine label and same human labels.'




def adjusted_rand_index_tooltips():
	return ''



def f_score_tooltips():
	return 'F Score is computed by ((beta^2 + 1) * P * R) / (beta^2 * P + R), where:\n\n' +\
		    'P = TP / (TP + FP).\n\n' +\
		    'R = TP / (TP + FN).\n\n' +\
		    'TP is true positive - the number of pairs of points (x, y) such that x and y have same machine label and same human label.\n\n' +\
		    'TN is true negative - the number of pairs of topics (x, y) such that x and y have different machine labels and different human labels.\n\n' +\
		    'FP is false positive - the number of pairs of points (x, y) such that x and y have same machine label and different human labels.\n\n' +\
		    'FN is false negative - the number of pairs of points (x, y) such that x and y have different machine label and same human labels.\n\n' +\
		    'beta is a chosen constant weighing recall over precision.'



def visualize_evaluation(evaluation_data, evaluation_function_names, clustering_names, visualization_paths):
	for row_id in range(len(evaluation_data)):
		evaluation = evaluation_data[row_id]
		evaluation_function_name = evaluation_function_names[row_id]
		visualization_path = visualization_paths[row_id]
		fig, ax = plt.subplots()
		ax.plot(clustering_names, evaluation)
		ax.set(xlabel='Clustering', ylabel='Evaluation', title=evaluation_function_name)
		fig.savefig(visualization_path)
		plt.close(fig)



def generate_evaluation(evaluation_functions, human_label, machine_labels):
	return [[evaluation_function(human_label, machine_label) for machine_label in machine_labels] for evaluation_function in evaluation_functions]