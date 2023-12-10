(examples-gromacs)=

# GROMACS

[GROMACS](https://www.gromacs.org/) is a free and open-source software suite for high-performance molecular dynamics and
output analysis. In this example, we will follow the example of
[mdtutorials.com](http://www.mdtutorials.com/gmx/lysozyme/index.html) which downloads the Lysozyme protein from the
[RCSB protein data bank](https://www.rcsb.org/) and shows how to use GROMACS to setup a simulation of its dynamics when
solvated in a box of water and ions. For brevity's sake, we will follow the tutorial up until the equilibration stage.
The script shown below can be [downloaded here](include/scripts/gromacs.py).

:::{warning}
This example purely serves to illustrate how to use `aiida-shell`.
There is no guarantee that GROMACS is used correctly or in the most efficient way.
:::

The first step is to download the protein:

:::{literalinclude} include/scripts/gromacs.py
:lines: 1-10
:::

We use the `urllib` module of the standard library to open the file and wrap it in AiiDA's `SinglefileData` data type,
which allows it to be stored in the provenance graph. The first step is to perform some simple pre-processing. The
downloaded file defines the protein as embedded in crystalline water, which we don't need for our purposes and therefore
we remove it. Water molecules are marked by the `HOH` residue in the file, so we simply write a function that loops over
the lines in the PDB file and removes any line that contains `HOH`.

:::{literalinclude} include/scripts/gromacs.py
:lines: 13-25
:::

Calling the `remote_water_from_pdb` with the original `lysozyme_pdb` returns the modified `lysozyme` file (which is also
an instance of `SinglefileData`).

:::{note}
We mark the function `remove_water_from_pdb` with AiiDA's `calcfunction` decorator. This ensures the act of modifying
the originally downloaded protein file is captured in the provenance graph.
:::

Next, we run GROMACS' `gmx pdb2gmx` command to convert the file from the `.pdb` to GROMACS' native `.gro` format. If we
were to execute this directly on the command line, it would look like:

:::{code-block} console
gmx pdb2gmx -f lysozyme.pdb -o output.gro -water spce -ff oplsaa
:::

When wrapping this in `aiida-shell`, the main question is how we pass the protein PDB file to the command, as that is
stored in AiiDA's provenance graph and is not a file on disk. We simply replace the file name with the `{protein}`
placeholder and then add the lysozyme `SinglefileData` nodes in the `nodes` dictionary. The `launch_shell_job` will
automatically copy the content of the `SinglefileData` to the working directory where the command is executed and
substitute the `{protein}` lysozyme with the filename to which the content was copied:

:::{literalinclude} include/scripts/gromacs.py
:lines: 28-36
:caption: Run `gmx pdb2gmx` to convert the PDB to GROMACS .gro format.
:::

:::{note}
The `nodes` argument takes a dictionary with an arbitrary number of `SinglefileData` nodes whose content is copied to
the working directory where the command is executed. If the key of the node appears as a placeholder in the `arguments`
argument, it is replaced with its filename.
:::

The `gmx pdb2gmx` is expected to generate three outputs of interest:

- `output.gro`: The protein structure in
  [`.gro` format](https://manual.gromacs.org/current/reference-manual/file-formats.html#gro)
- `topol.top`: The [topology file](https://manual.gromacs.org/current/reference-manual/file-formats.html#top)
- `posre.itp`: The [include topology file](https://manual.gromacs.org/current/reference-manual/file-formats.html#itp)
  with position restraints

To capture these output files, they are declared using the `outputs` argument. `aiida-shell` will automatically wrap
these output files in a `SinglefileData` and store them as an output of the command in the provenance graph.

The next step is to create the simulation box around the protein using `gmx editconf`:

:::{literalinclude} include/scripts/gromacs.py
:lines: 39-47
:caption: Run `gmx editconf` to generate a cubic box around the protein.
:::

:::{tip}
GROMACS by default writes output to the `stderr` file descriptor. This is a bit unususal, as normally this is reserved
for errors. `aiida-shell` by default detects if the executed command wrote anything to `stderr` and if so, assigns the
[exit code `400` to the process](https://aiida.readthedocs.io/projects/aiida-core/en/latest/topics/processes/concepts.html#process-exit-codes),
indicating that it has failed. Since the command did not actually fail, this can be misleading. As a workaround, we set
the metadata option `redirect_stderr` to `True` which will instruct `aiida-shell` to redirect all output written to
`stderr` to the `stdout` descriptor instead.
:::

The `gmx editconf` command takes a GRO file defining the protein structure. In this example, this file was created by
the previous `gmx pdb2gmx` command. We can retrieve this output file from the results dictionary and directly assign it
to the `nodes` dictionary.

Now that the protein is placed in a simulation box, we can solvate the system in water:

:::{literalinclude} include/scripts/gromacs.py
:lines: 50-59
:caption: Run `gmx solvate` to solvate the protein in water.
:::

This command requires, in addition to the `.gro` file produced in the previous step, the `.top` topology file created by
the `gmx pdb2gmx` command.

The next step is to insert ions into the solution to neutralize the system. GROMACS provides the `gmx genion` command
for this, which runs actual molecular dynamics to optimize the positions of the added ions. It requires a
[`.tpr` file](https://manual.gromacs.org/current/reference-manual/file-formats.html#tpr) which defines the starting
structure and conditions of a simulation. Such a file is created using the `gmx grompp` pre-processing utility which
takes an [`.mdp` file](https://manual.gromacs.org/current/reference-manual/file-formats.html#mdp) defining the
parameters of the simulation:

:::{literalinclude} include/scripts/gromacs.py
:lines: 62-92
:caption: Define the input parameters for ion insertion.
:::

With the generated `.tpr` file in hand, we can now call `gmx genion` to insert the ions into the system:

:::{literalinclude} include/scripts/gromacs.py
:lines: 95-106
:caption: Run `gmx genion` to neutralize the system with counter ions.
:::

:::{note}
The `gmx genion` needs to know which type of residues should be replaced by the ions. Unfortunately, it does not allow
this to be specified with a command line option, but rather will prompt for it, providing a number of options. We want
to select the option `SOL` (solvent molecules) for this, but if we run the command normally through `aiida-shell`, the
command will hang, waiting for eternity for the prompt to be answered. To forward the prompt answer to `aiida-shell`,
we need to communicate it through the `stdin` descriptor. We add the desired response, `SOL` in this case, as a
`SinglefileData` node to the `nodes` dictionary. The key that is used, `stdin` in this example, should be specified
using the `filename_stdin` metadata option.
:::

The system is now properly neutralized and we can proceed to minimizing its energy. This is done using GROMACS' command
to run molecular dynamics `gmx mdrun`. Just like `gmx genion` this requires a `.tpr` file, which we prepare using
`gmx grompp`:

:::{literalinclude} include/scripts/gromacs.py
:lines: 109-139
:caption: Define the input parameters for energy minimization.
:::

With the `.tpr` created, we run `gmx mdrun` to run the energy minimization:

:::{literalinclude} include/scripts/gromacs.py
:lines: 142-152
:caption: Run `gmx mdrun` to run the energy minimization.
:::

As the final step in this example, we will performance some analysis on the energy minimization. We use `gmx energy` to
extract the system's potential energy during the simulation:

:::{literalinclude} include/scripts/gromacs.py
:lines: 155-164
:caption: Run `gmx energy` to extract the potential energy during the energy minimization.
:::

:::{note}
The `gmx energy` command prompts to determine which quantity to project. In this example, we first pass `10` which
corresponds to the potential energy, followed by `0` which finalizes the selection and completes the prompt.
:::

To visualize the extracted data, we define the `create_plot` function (once again decorated with `calcfunction` to
preserve provenance) and pass the `potential.xvg` output file generated by `gmx energy`:

:::{literalinclude} include/scripts/gromacs.py
:lines: 167-191
:::

The plot is saved to a stream in memory which is then passed to a `SinglefileData` node to store it in AiiDA's
provenance graph. The final result will look something like the following:

:::{figure} include/images/gromacs/potential_energy.png
:alt: potential energy

The evolution of the potential energy of the system during the energy minimization.
:::

:::{tip}
To extract the plot from the `SinglefileData` node, you can use the command `verdi node repo cat <PK> >
potential_energy.png`, where you replace `<PK>` with the pk of the `SinglefileData` node returned by the `create_plot`
function.
:::

To conclude this example, below is the provenance graph that was created by running the example script:

:::{figure} include/images/gromacs/provenance.png
:alt: provenance graph

The provenance grpah was generated using `verdi node graph generate <PK>`, where `<PK>` was replaced with the pk of the
`SinglefileData` node returned by the `create_plot` function.
:::
