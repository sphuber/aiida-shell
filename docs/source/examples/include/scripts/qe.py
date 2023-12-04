#!/usr/bin/env runaiida
"""Simulation of electronic band structure of GaAs using Quantum ESPRESSO."""
import urllib.request

from aiida import engine, orm
from aiida_shell import launch_shell_job

# Generate a folder with the required pseudopotentials
url_base = 'https://pseudopotentials.quantum-espresso.org/upf_files/'
pseudos = orm.FolderData()

with urllib.request.urlopen(f'{url_base}/Ga.pbe-dn-kjpaw_psl.1.0.0.UPF') as handle:
    pseudos.put_object_from_filelike(handle, 'Ga.UPF')

with urllib.request.urlopen(f'{url_base}/As.pbe-n-kjpaw_psl.1.0.0.UPF') as handle:
    pseudos.put_object_from_filelike(handle, 'As.UPF')

# The input script for the SCF calculation
script_scf = """\
&control
    calculation = 'scf'
    prefix = 'output'
    pseudo_dir = './pseudo/'
/
&system
    ibrav = 2
    nat = 2
    ntyp = 2
    celldm(1) = 10.86
    ecutwfc = 60
    ecutrho = 244
/
&electrons
/
ATOMIC_SPECIES
    Ga 69.72 Ga.UPF
    As 74.92 As.UPF
ATOMIC_POSITIONS
    Ga 0.00 0.00 0.00
    As 0.25 0.25 0.25
K_POINTS {automatic}
    8 8 8 0 0 0
"""

# Launch the SCF calculation using pw.x
results_scf, node_scf = launch_shell_job(
    'pw.x',
    arguments='-in {script}',
    nodes={
        'script': orm.SinglefileData.from_string(script_scf),
        'pseudos': pseudos,
    },
    filenames={
        'pseudos': 'pseudo',
    },
    outputs=['output.xml', 'output.save'],
)

# The input script for the NSCF calculation
script_nscf = """\
&control
    calculation = 'bands'
    prefix = 'output'
    pseudo_dir = './pseudo/'
/
&system
    ibrav = 2
    nat = 2
    ntyp = 2
    celldm(1) = 10.86
    ecutwfc = 60
    ecutrho = 244
    nbnd = 16
/
&electrons
/
ATOMIC_SPECIES
    Ga  69.72 Ga.UPF
    As  74.92 As.UPF
ATOMIC_POSITIONS
    Ga 0.00 0.00 0.00
    As 0.25 0.25 0.25
K_POINTS {crystal_b}
5
    0.000 0.50 00.000 20 !L
    0.000 0.00 00.000 30 !G
   -0.500 0.00 -0.500 10 !X
   -0.375 0.00 -0.675 30 !K,U
    0.000 0.00 -1.000 20 !G
"""

# Launch the NSCF calculation using pw.x
results_nscf, node_nscf = launch_shell_job(
    'pw.x',
    arguments='-in {script}',
    nodes={
        'script': orm.SinglefileData.from_string(script_nscf),
        'pseudos': pseudos,
        'results_scf': results_scf['output_save'],
    },
    filenames={
        'pseudos': 'pseudo',
        'results_scf': 'output.save',
    },
    outputs=['output.xml', 'output.save'],
)

# The input script for the bands post-processing
script_bands = """\
&bands
    prefix = 'output',
    filband = 'bands.dat',
    lsym = .true.
/
"""

# Launch the bands post-processing using bands.x
results_bands, node_bands = launch_shell_job(
    'bands.x',
    arguments='-in {script}',
    nodes={
        'script': orm.SinglefileData.from_string(script_bands),
        'results_nscf': results_nscf['output_save'],
    },
    filenames={
        'results_nscf': 'output.save',
    },
    outputs=['bands.dat.gnu'],
)


@engine.calcfunction
def plot_bands(bands: orm.SinglefileData, stdout_scf: orm.SinglefileData) -> orm.SinglefileData:
    """Plot the band structure."""
    import io
    import re

    import matplotlib.pyplot as plt
    import numpy as np

    with bands.as_path() as filepath:
        data = np.loadtxt(filepath)

    kpoints = np.unique(data[:, 0])
    bands = np.reshape(data[:, 1], (-1, len(kpoints)))
    xticks = [0, 0.8660, 1.8660, 2.2196, 3.2802]
    xlabels = ['L', r'$\Gamma$', 'X', 'U', r'$\Gamma$']

    fermi_energy = re.search(r'highest occupied level \(ev\):\s+(\d+\.\d+)', stdout_scf.get_content()).groups()[0]
    plt.axhline(float(fermi_energy), color='black', ls='--', lw=0.5, alpha=0.5)

    for band in bands:
        plt.plot(kpoints, band, color='black', alpha=0.5)

    for tick in xticks[1:-1]:
        plt.axvline(tick, color='black', ls='dotted', lw=0.5, alpha=0.5)

    plt.xlim(min(kpoints), max(kpoints))
    plt.xticks(ticks=xticks, labels=xlabels)
    plt.ylabel('Energy (eV)')

    stream = io.BytesIO()
    plt.savefig(stream, format='png', bbox_inches='tight', dpi=180)
    stream.seek(0)

    return orm.SinglefileData(stream, filename='bands.png')


# Create the electronic band structure plot
results = plot_bands(node_bands.outputs.bands_dat_gnu, node_scf.outputs.stdout)
print(results)
