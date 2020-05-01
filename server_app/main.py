import os
import sys
cur_dir = os.path.dirname(__file__)
os.chdir(cur_dir)
sys.path.append(cur_dir)

import web
from modules.run import run_evaluate
import os



urls = (
	'/', 'Index',
)
global_render = web.template.render('templates')
render = web.template.render('templates', base='base.html', globals={'global_render':global_render})
app = web.application(urls, globals())



def get_filenames():
	result = []
	for r, d, f in os.walk('new_aa_csvs/'):
		for file in f:
			result.append(file.split('.csv')[0])
	return result



class Index:
	def GET(self):
		filenames = get_filenames()
		data = web.input(filename=filenames[0])
		valid, status_message, validator, evaluation_function_names, evaluation_table, evaluation_row_tooltips, visualization_paths = run_evaluate(data=data)
		return render.evaluate_results(status_message, evaluation_function_names, evaluation_table, evaluation_row_tooltips, visualization_paths, filenames, data.filename)

	def POST(self):
		filenames = get_filenames()
		data = web.input(filename=filenames[0])
		valid, status_message, validator, evaluation_function_names, evaluation_table, evaluation_row_tooltips, visualization_paths = run_evaluate(data=data)
		return render.evaluate_results(status_message, evaluation_function_names, evaluation_table, evaluation_row_tooltips, visualization_paths, filenames, data.filename)



if __name__ == '__main__':
	app.run()
else:
	application = app.wsgifunc()