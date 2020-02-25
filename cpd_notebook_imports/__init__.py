from IPython import get_ipython
from nbformat import read
from IPython.core.interactiveshell import InteractiveShell
import io, os, sys, types

import requests

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def find_notebook_cpd(fullname):
    """
    TODO:
    - docstring
    - deal with path?
    """
    path = fullname.rsplit('.', 1)
    notebook_name = path[-1]

    token = os.environ['USER_ACCESS_TOKEN']
    project_id = os.environ['PROJECT_ID']
    host = os.environ['RUNTIME_ENV_APSX_URL']
    headers = {'authorization': 'Bearer %s'%(token),
               'cache-control': "no-cache",
               'accept': 'application/json',
               'content-type': 'application/json'}
    # find path of notebook
    notebooks_metadata = requests.get(host + "/v2/asset_files/notebook",
                                      headers=headers,
                                      verify=False, # verify=False to ignore SSL issues
                                      params={"project_id": os.environ['PROJECT_ID']})
    notebooks_metadata = notebooks_metadata.json()['resources']
    metadata = [x for x in notebooks_metadata if x['path'].startswith('notebook/' + notebook_name)]
    if len(metadata) == 0:
        # this will only work if notebook has ONLY -, not if mix of - and _
        new_name = notebook_name.replace('_', '-')
        print(f'Didn\'t find {notebook_name}, trying {new_name}')
        metadata = [x for x in notebooks_metadata if x['path'].startswith('notebook/' + new_name)]
        if len(metadata):
            return None
    elif len(metadata) > 1:
        return None
    else:
        return metadata[0]['path']

class NotebookLoader(object):
    """Module Loader for Jupyter Notebooks"""
    def __init__(self, path=None):
        self.shell = InteractiveShell.instance()
        self.path = path

    def load_module(self, fullname):
        """import a notebook as a module"""
        path = find_notebook_cpd(fullname)

        print ("importing Jupyter notebook from %s" % path)
        
        token = os.environ['USER_ACCESS_TOKEN']
        project_id = os.environ['PROJECT_ID']
        host = os.environ['RUNTIME_ENV_APSX_URL']
        headers = {'authorization': 'Bearer %s'%(token),
                   'cache-control': "no-cache",
                   'accept': 'application/json',
                   'content-type': 'application/json'}
        # get notebook content
        notebook_content = requests.get(host + '/v2/asset_files/' +
                                        path,
                                        headers=headers,
                                        verify=False, # verify=False to ignore SSL issues
                                        params={'project_id': project_id})
        notebook_content = notebook_content.text
        # write to temporary file
        temp_path = '/tmp/temp_notebook.ipynb'
        with open(temp_path, 'w') as file:
            file.write(notebook_content)

        # load the notebook object
        with io.open(temp_path, 'r', encoding='utf-8') as f:
            nb = read(f, 4)
        
        os.remove(temp_path)

        # create the module and add it to sys.modules
        # if name in sys.modules:
        #    return sys.modules[name]
        mod = types.ModuleType(fullname)
        mod.__file__ = path
        mod.__loader__ = self
        mod.__dict__['get_ipython'] = get_ipython
        sys.modules[fullname] = mod

        # extra work to ensure that magics that would affect the user_ns
        # actually affect the notebook module's ns
        save_user_ns = self.shell.user_ns
        self.shell.user_ns = mod.__dict__

        try:
            for cell in nb.cells:
                if cell.cell_type == 'code':
                    # transform the input to executable Python
                    code = self.shell.input_transformer_manager.transform_cell(cell.source)
                    # run the code in the module
                    exec(code, mod.__dict__)
        finally:
            self.shell.user_ns = save_user_ns
        return mod

class NotebookFinder(object):
    """Module finder that locates Jupyter Notebooks"""
    def __init__(self):
        self.loaders = {}

    def find_module(self, fullname,  path=None):
        nb_path = find_notebook_cpd(fullname)
        if not nb_path:
            # the role of this function is to check that we can actually load
            return

        key = path
        if path:
            # lists aren't hashable
            key = os.path.sep.join(path)

        if key not in self.loaders:
            self.loaders[key] = NotebookLoader(path)
        return self.loaders[key]

if not any(isinstance(x, NotebookFinder) for x in sys.meta_path):
    sys.meta_path.append(NotebookFinder())


