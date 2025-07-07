from setuptools import setup, find_packages

setup(
    name='epc_cli',
    version='0.4.0',
    packages=find_packages(),  # automatically finds epc_cli and submodules
    install_requires=[],
     scripts=[
        'bin/epc_automatic_submission',
        'bin/epc_epi_validation',
        'bin/epc_finalise_submission',
        'bin/epc_get_timeline',
        'bin/epc_iso_validation',
        'bin/epc_upload_csv',
        'bin/epc_upload_seq_data'
    ],
)
