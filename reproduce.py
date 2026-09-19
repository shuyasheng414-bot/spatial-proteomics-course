"""Execute the complete notebook using this Python environment; export HTML."""
from pathlib import Path
import hashlib
import json
import os
import sys
import nbformat
from nbclient import NotebookClient
from nbconvert import HTMLExporter
from jupyter_client.kernelspec import KernelSpecManager
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent


def main():
    runtime = ROOT / '.jupyter'
    runtime.mkdir(exist_ok=True)
    for name, folder in [('IPYTHONDIR', 'ipython'), ('JUPYTER_RUNTIME_DIR', 'runtime'),
                         ('JUPYTER_CONFIG_DIR', 'config'), ('MPLCONFIGDIR', 'matplotlib')]:
        location = runtime / folder
        location.mkdir(exist_ok=True)
        os.environ[name] = str(location)
    provenance = json.loads((ROOT / 'data/provenance.json').read_text(encoding='utf-8'))
    actual = hashlib.sha256((ROOT / 'data/tan2009_rep1.csv').read_bytes()).hexdigest()
    if actual != provenance['sha256']:
        raise ValueError('Data checksum mismatch; inspect data/provenance.json')
    notebook = nbformat.read(ROOT / 'spatial_proteomics.ipynb', as_version=4)
    # A temporary kernelspec guarantees we run the current interpreter,
    # without installing or changing a global Jupyter kernel.
    with TemporaryDirectory(prefix='kernel-', dir=runtime) as temp:
        kernel_dir = Path(temp) / 'course'
        kernel_dir.mkdir()
        spec = {'argv': [sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}'],
                'display_name': 'Course Python', 'language': 'python'}
        (kernel_dir / 'kernel.json').write_text(json.dumps(spec), encoding='utf-8')
        manager = KernelSpecManager(kernel_dirs=[temp])
        client = NotebookClient(notebook, timeout=300, kernel_name='course',
                                resources={'metadata': {'path': str(ROOT)}})
        client.create_kernel_manager()
        client.km.kernel_spec_manager = manager
        client.execute()
    notebook.metadata.kernelspec = {'display_name': 'Python 3', 'language':'python', 'name':'python3'}
    nbformat.validate(notebook)
    nbformat.write(notebook, ROOT / 'spatial_proteomics.ipynb')
    body, _ = HTMLExporter(template_name='lab').from_notebook_node(notebook)
    (ROOT / 'results/report.html').write_text(body, encoding='utf-8')
    print('Success: spatial_proteomics.ipynb and results/report.html')


if __name__ == '__main__':
    main()
