(examples-qe)=

# Quantum ESPRESSO

[Quantum ESPRESSO](https://www.quantum-espresso.org/) is a free and open-source an integrated suite of Open-Source computer codes for electronic-structure calculations and materials modeling at the nanoscale.
In this example, the electronic band structure of the gallium arsenide semiconductor is computed.
The script shown below can be [downloaded here](include/scripts/qe.py).

:::{warning}
This example purely serves to illustrate how to use `aiida-shell`.
There is no guarantee that Quantum ESPRESSO is used correctly or in the most efficient way.
:::

The workflow consists roughly of four calculations:

1. Computing the charge density of the system self-consistently
2. Computing the electronic structure along high-symmetry k-points
3. Post-processing the data to extract the electronic band structure
4. Plot the electronic band structure

Quantum ESPRESSO employs pseudopotentials to describe the effective potential of the system.
Each calculation requires a pseudopotential for each element that is part of the system.
For this example, we will use the pseudopotentials provided on the [website of Quantum ESPRESSO itself](https://pseudopotentials.quantum-espresso.org/upf_files/).
To make them available to the calculations, we download and store them in a `FolderData` node:

:::{literalinclude} include/scripts/qe.py
:lines: 1-16
:caption: Downloading pseudopotentials for Ga and As and storing them in AiiDA's provenance graph using a `FolderData` node.
:::

The next step is to launch the the self-consistent calculation.
Below we define the input script:
:::{literalinclude} include/scripts/qe.py
:lines: 19-43
:caption: Define the input script for the self-consistent field (SCF) calculation.
:::

Besides the input script itself, the calculation requires the pseudopotentials that we downloaded earlier.
We instruct `aiida-shell` to copy them to the working directory by adding the `FolderData` with pseudos to the `nodes` dictionary:
:::{literalinclude} include/scripts/qe.py
:lines: 46-57
:caption: Launch the self-consistent field (SCF) calculation.
:::
Quantum ESPRESSO's `pw.x` code does not expect the location of the pseudopotentials as a command line argument, so we don't have to add a placeholder for this node in the `arguments` input.
However, the input script does define the `CONTROL.pseudo_dir` setting, which allows to specify the location of the pseudopotentials.
In the script, this was set to `./pseudo`, so we need to make sure that the content of the `pseudos` node are copied to that subdirectory.
This is accomplished using the `filenames` input where we define the relative filepath target for the `pseudos` node.
As outputs, we expect the `output.xml` file and the `output.save` directory.

The next step is to compute the electronic structure along high-symmetry k-points.
Below we define the input script, where the only real difference is the explicit definition of the number of bands in `SYSTEM.nbnd` and the definition of the `K_POINTS`:

:::{literalinclude} include/scripts/qe.py
:lines: 60-90
:caption: Define the input script for the non self-consistent field (NSCF) calculation.
:::

The NSCF calculation requires the results of the SCF calculation, which were written to the `output.save` directory.
The SCF calculation registered this folder as an output and so its contents were retrieved as a `FolderData` and attached as an output node.
This node, retrieved from the results dictionary of the SCF calculation `results_scf['output_save']`, is passed as an entry in the `nodes` input:

:::{literalinclude} include/scripts/qe.py
:lines: 93-106
:caption: Launch the non self-consistent field (NSCF) calculation.
:::

With the bands computed, we need to extract them from the `output.save` directory in a format that allows them to be plotted.
Quantum ESPRESSO provides the `bands.x` utility exactly for this purpose:

:::{literalinclude} include/scripts/qe.py
:lines: 109-114
:caption: Define the input script for the bands post-processing.
:::

Once again, we provide the contents of the `output.save` directory, this time from the NSCF calculation, which were attached as a `FolderData` node to the outputs:

:::{literalinclude} include/scripts/qe.py
:lines: 118-129
:caption: Launch the bands post-processing.
:::

The `bands.x` utility will write the bands data to a file named `bands.dat.gnu` which is registered as an output.
This file, which will be attached as a `SinglefileData` node to the outputs, can be used together with the `stdout` content to plot the computed electronic band structure:

:::{literalinclude} include/scripts/qe.py
:lines: 133-171
:caption: Define and call a function to create a plot of the band structure.
:::

The resulting PNG file will look something like the following:

:::{figure} include/images/qe/band_structure.png
:alt: electronic band structure

The computed electronic band structure of GaAs using Quantum ESPRESSO's `pw.x` and `bands.x`.
:::


## Running with MPI

High-performances codes, like Quantum ESPRESSO, are often compatible with the Message Passing Interface (MPI).
Running the code with MPI, allows the calculation to be parallelized over multiple CPUs or nodes on a cluster.
By default, commands run through `aiida-shell` always run without MPI, but it can be explicitly enabled.

To enable the command to be run with MPI, simply set the `metadata.options.withmpi` input to `True`:
:::{code-block} python
:caption: Running the SCF calculation with MPI enabled, parallelizing over multiple processors.
from aiida import orm
from aiida_shell import launch_shell_job

results_scf, node_scf = launch_shell_job(
    'pw.x',
    arguments='-in {script}',
    nodes={
        'script': orm.SinglefileData.from_string(script_scf),
        'pseudos': pseudos
    },
    filenames={
        'pseudos': 'pseudo'
    },
    outputs=['output.xml', 'output.save'],
    metadata={
        'options': {
            'withmpi': True,
            'resources': {
                'num_machines': 2,
                'num_mpiprocs_per_machine': 3,
            }
        }
    }
)
:::

The `metadata.options.resources` allows to specify the desired resources:

* `num_machines` defines the number of machines to be used: a machine can also be thought of as a *nodes* on a typical high-performance computing cluster.
* `num_mpiprocs_per_machine` defines the number of processors to use per machine (or *node*).

When MPI is enabled, `aiida-shell` will prefix the command to run with `mpirun -np {tot_num_mpiprocs}`.
The `{tot_num_mpiprocs}` placeholder is replaced with the product of the `num_machines` and `num_mpiprocs_per_machine` keys of the `metadata.options.resources` input, i.e., in this example the MPI line would be `mpirun -np 6`.

The MPI run command `mpirun -np {tot_num_mpiprocs}` is the default but this can be configured.
To do so, a `Computer` instance needs to be created.
For example, imagine the localhost has the SLURM scheduler installed and we want to run `srun -n {tot_num_mpiprocs}` as the MPI command:
:::{code-block} python
:caption: Creating a `Computer` with a custom MPI run command.
from tempfile import gettempdir
from aiida.orm import Computer

computer = Computer(
    label='localhost-srun',
    hostname='localhost',
    description='Localhost using SLURM and `srun`',
    transport_type='core.local',
    scheduler_type='core.slurm',
    workdir=gettempdir(),
).store()
computer.set_mpirun_command('srun -n {tot_num_mpiprocs}')
computer.set_default_mpiprocs_per_machine(1)
computer.configure(safe_interval=0.0)
:::
The `scheduler_type` is set to `core.slurm` to use the scheduler plugin for SLURM and the custom MPI command is defined using the `set_mpirun_command` method.

:::{note}
Alternatively, the computer can be created and configured using the `verdi` command line interface.
Run `verdi computer setup --label localhost-srun` to create it, followed by `verdi computer configure core.local localhost-srun` to configure it.
:::

The new computer can now be specified in the `metadata.options.computer` input:
:::{code-block} python
:caption: Running the SCF calculation with MPI enabled on a specific `Computer` with a custom MPI command.
from aiida import orm
from aiida_shell import launch_shell_job

results_scf, node_scf = launch_shell_job(
    'pw.x',
    arguments='-in {script}',
    nodes={
        'script': orm.SinglefileData.from_string(script_scf),
        'pseudos': pseudos
    },
    filenames={
        'pseudos': 'pseudo'
    },
    outputs=['output.xml', 'output.save'],
    metadata={
        'options': {
            'computer': orm.load_computer('localhost-srun'),
            'withmpi': True,
            'resources': {
                'num_machines': 2,
                'num_mpiprocs_per_machine': 3,
            }
        }
    }
)
:::

## Running on a remote computer

By default, `aiida-shell` executes commands on the machine where the script is run, i.e. the *localhost*.
It is also possible to run commands on remote computers, for example a computer that can be connected to over SSH.
Just as in the previous section, a custom `Computer` can be created, where in this case, the `transport_type` is set to `core.ssh` to use the SSH transport plugin:
:::{code-block} python
:caption: Creating a `Computer` to connect to a remote computer over SSH.
from aiida.orm import Computer

computer = Computer(
    label='remote-computer',
    hostname='server.hostname.com',
    description='Remote computer over SSH',
    transport_type='core.ssh',
    scheduler_type='core.slurm',
    workdir='/some/scratch.directory',
).store()
:::
The `hostname` should be the fully qualified domain name at which the remote computer can be reached.

After creating the `Computer` instance, it needs to be configured such that AiiDA can authenticate and connect to the server.
The easiest is to use the CLI:
:::{code-block} console
:caption: Configuring the computer to connect over SSH
verdi computer configure core.ssh <LABEL>
:::
Here `<LABEL>` should be replaced with the label of the created computer, i.e., `remote-computer` in this example.

:::{tip}
Run `verdi computer test <LABEL>` to check that the computer was correctly set up and configured.
AiiDA runs a number of checks to make sure that all required functionality is working properly, such as opening a connection, communicating with the job scheduler, and creating new directories and files in the scratch directory.
:::

When the job is launched, AiiDA takes care of submitting it to the scheduler on the remote computer.
When the command finished, the outputs are automatically retrieved over SSH and stored in the provenance graph.
