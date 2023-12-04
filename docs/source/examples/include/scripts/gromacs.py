#!/usr/bin/env runaiida
"""Simulation of lysozyme protein dynamics using GROMACS."""
import urllib.request

from aiida import engine, orm
from aiida_shell import launch_shell_job

# Download the lysozyme protein structure.
with urllib.request.urlopen('https://files.rcsb.org/download/1AKI.pdb') as handle:
    lysozyme_pdb = orm.SinglefileData(handle, filename='lysozyme.pdb')


@engine.calcfunction
def remove_water_from_pdb(protein: orm.SinglefileData) -> orm.SinglefileData:
    """Remove water molecules from a PDB file."""
    lines = protein.get_content().split('\n')
    lines_without_water = [line for line in lines if 'HOH' not in line]
    return orm.SinglefileData.from_string(
        '\n'.join(lines_without_water),
        filename=protein.filename,
    )


# Remove crystalline water from PDB by skipping any lines that contain `HOH` residue.
lysozyme = remove_water_from_pdb(lysozyme_pdb)

# Run `gmx pdb2gmx` to convert the PDB to GROMACS .gro format.
results_pdb2gmx, node_pdb2gmx = launch_shell_job(
    'gmx',
    arguments='pdb2gmx -f {protein} -o output.gro -water spce -ff oplsaa',
    nodes={
        'protein': lysozyme,
    },
    outputs=['output.gro', 'topol.top', 'posre.itp'],
    metadata={'options': {'redirect_stderr': True}},
)

# Run `gmx editconf` to generate a cubic box around the protein.
results_editconf, node_editconf = launch_shell_job(
    'gmx',
    arguments='editconf -f {gro} -o output.gro -c -d 1.0 -bt cubic',
    nodes={
        'gro': results_pdb2gmx['output_gro'],
    },
    outputs=['output.gro'],
    metadata={'options': {'redirect_stderr': True}},
)

# Run `gmx solvate` to solvate the protein in water.
results_solvate, node_solvate = launch_shell_job(
    'gmx',
    arguments='solvate -cp {gro} -cs spc216.gro -o output.gro -p {top}',
    nodes={
        'gro': results_editconf['output_gro'],
        'top': results_pdb2gmx['topol_top'],
    },
    outputs=['output.gro', 'topol.top'],
    metadata={'options': {'redirect_stderr': True}},
)

# Define the input parameters for ion insertion.
ions_mpd = orm.SinglefileData.from_string(
    """
    integrator      = steep
    emtol           = 1000.0
    emstep          = 0.01
    nsteps          = 50000
    nstlist         = 1
    cutoff-scheme   = Verlet
    ns_type         = grid
    coulombtype     = cutoff
    rcoulomb        = 1.0
    rvdw            = 1.0
    pbc             = xyz
    ld_seed         = 1
    gen_seed        = 1
    """,
    filename='ions.mdp',
)

# Run `gmx grompp` to pre-process the parameters for ion insertion.
results_grompp_genion, node_grompp_ion = launch_shell_job(
    'gmx',
    arguments='grompp -f {mdp} -c {gro} -p {top} -o output.tpr',
    nodes={
        'mdp': ions_mpd,
        'gro': results_solvate['output_gro'],
        'top': results_solvate['topol_top'],
    },
    outputs=['output.tpr'],
    metadata={'options': {'redirect_stderr': True}},
)

# Run `gmx genion` to neutralize the system with counter ions.
results_genion, node_genion = launch_shell_job(
    'gmx',
    arguments='genion -s {tpr} -o {gro} -p {top} -pname NA -nname CL -neutral',
    nodes={
        'gro': results_solvate['output_gro'],
        'top': results_solvate['topol_top'],
        'tpr': results_grompp_genion['output_tpr'],
        'stdin': orm.SinglefileData.from_string('SOL'),
    },
    outputs=['output.gro', 'topol.top'],
    metadata={'options': {'redirect_stderr': True, 'filename_stdin': 'stdin'}},
)

# Define the input parameters for energy minimization.
em_mdp = orm.SinglefileData.from_string(
    """
    integrator      = steep
    emtol           = 1000.0
    emstep          = 0.01
    nsteps          = 50000
    nstlist         = 1
    cutoff-scheme   = Verlet
    ns_type         = grid
    coulombtype     = PME
    rcoulomb        = 1.0
    rvdw            = 1.0
    pbc             = xyz
    ld_seed         = 1
    gen_seed        = 1
    """,
    filename='em.mdp',
)

# Run `gmx grompp` to pre-process the parameters for energy minimization.
results_grompp_em, node_grompp_em = launch_shell_job(
    'gmx',
    arguments='grompp -f {mdp} -c {gro} -p {top} -o output.tpr',
    nodes={
        'mdp': em_mdp,
        'gro': results_genion['output_gro'],
        'top': results_genion['topol_top'],
    },
    outputs=['output.tpr'],
    metadata={'options': {'redirect_stderr': True}},
)

# Run `gmx mdrun` to run the energy minimization.
results_em, node_em = launch_shell_job(
    'gmx',
    arguments='mdrun -v -deffnm output -s {tpr}',
    nodes={
        'gro': results_genion['output_gro'],
        'top': results_genion['topol_top'],
        'tpr': results_grompp_em['output_tpr'],
    },
    outputs=['output.edr'],
    metadata={'options': {'redirect_stderr': True}},
)

# Run `gmx energy` to extract the potential energy during the energy minimization.
results_energy, node_energy = launch_shell_job(
    'gmx',
    arguments='energy -f {edr} -o potential.xvg',
    nodes={
        'edr': results_em['output_edr'],
        'stdin': orm.SinglefileData.from_string('10\n0'),
    },
    outputs=['potential.xvg'],
    metadata={'options': {'redirect_stderr': True, 'filename_stdin': 'stdin'}},
)


@engine.calcfunction
def create_plot(xvg: orm.SinglefileData) -> orm.SinglefileData:
    """Plot the data of a XVG output file."""
    import io

    import matplotlib.pyplot as plt
    import numpy as np

    with xvg.as_path() as filepath:
        data = np.loadtxt(filepath, comments=['#', '@']).T

    plt.plot(*data)
    plt.xlabel('Energy minimization step')
    plt.ylabel('Potential energy [kJ/mol]')

    stream = io.BytesIO()
    plt.savefig(stream, format='png', bbox_inches='tight', dpi=180)
    stream.seek(0)

    return orm.SinglefileData(stream, filename='potential.png')


# Create a plot from the extracted potential energy of the system
plot = create_plot(results_energy['potential_xvg'])
print(plot.pk)
