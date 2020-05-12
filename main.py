import os
import sys
cur_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(cur_dir)
sys.path.append(cur_dir)

import web
from modules.run import run_evaluate
import os
import xml.etree.ElementTree as ET



urls = (
	'/', 'Index',
)
global_render = web.template.render('templates')
render = web.template.render('templates', base='base.html', globals={'global_render':global_render})
tree = ET.parse('config.xml')
root = tree.getroot()
local_or_server = root.find('local_or_server').text
app_name = root.find('app_name').text
if local_or_server not in {'local', 'server'}:
	sys.stderr.write('Error: Wrong config! <local_or_server> must be either local or server.\n')
	exit()
app = web.application(urls, globals())
application = app.wsgifunc()



def get_filenames():
	result = []
	for r, d, f in os.walk('new_aa_csvs/'):
		for file in f:
			result.append(file.split('.csv')[0])
	return result



def path_to_url(path):
	if local_or_server == 'local':
		return path
	else:
		return app_name + '/' + path



class Index:
	def GET(self):
		filenames = get_filenames()
		data = web.input(filename=filenames[0])
		valid, status_message, validator, evaluation_function_names, evaluation_table, evaluation_row_tooltips, visualization_paths = run_evaluate(data=data)
		visualization_urls = [path_to_url(visualization_path) for visualization_path in visualization_paths]
		return render.evaluate_results(status_message, evaluation_function_names, evaluation_table, evaluation_row_tooltips, visualization_urls, filenames, data.filename)

	def POST(self):
		filenames = get_filenames()
		data = web.input(filename=filenames[0])
		valid, status_message, validator, evaluation_function_names, evaluation_table, evaluation_row_tooltips, visualization_paths = run_evaluate(data=data)
		visualization_urls = [path_to_url(visualization_path) for visualization_path in visualization_paths]
		return render.evaluate_results(status_message, evaluation_function_names, evaluation_table, evaluation_row_tooltips, visualization_urls, filenames, data.filename)



if __name__ == '__main__':
	app.run()