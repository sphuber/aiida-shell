(examples-lammps)=

# LAMMPS

In this example, we show how to run simulations with the popular molecular dynamics program
[LAMMPS](https://www.lammps.org/) through `aiida-shell`. A complete script can be
[downloaded here](include/scripts/gromacs.py). Below we will go through the script step-by-step, followed by some tips
for basic analysis of the results.

:::{warning}
This example purely serves to illustrate how to use `aiida-shell`.
There is no guarantee that LAMMPS is used correctly or in the most efficient way.
:::

The most basic LAMMPS invocation looks as follows:

:::{code-block} console
lmp -in input.file
:::

The `lmp` executable is called passing the `input.file` file as an input using the `-in` command line option:

For the purposes of this example, we will take the
[input script for one of the official benchmarks](https://www.lammps.org/bench.html#lj). The complete input script can
be [downloaded here](https://www.lammps.org/inputs/in.lj.txt). We start our example script with some imports and by
defining the [input script](https://www.lammps.org/inputs/in.lj.txt):

:::{literalinclude} include/scripts/lammps.py
:lines: 1-36
:caption: Initial imports and script definition simulating the NVE ensemble for a simple Lennard-Jones fluid.
:::

The next step is to call the `lmp` for this input script. To do so, we use the `launch_shell_job` function of
`aiida-shell`:

:::{literalinclude} include/scripts/lammps.py
:lines: 38-44
:caption: Run the `lmp` executable for the example script through `aiida-shell`.
:::

The first argument is the command that should be executed, which is `lmp` in this example. The `arguments` argument
takes any command line options that should be passed. As shown in the introduction, this _should_ be `-in input.file`.
The difference here is that the script we want to run is not a file on disk, but defined in memory assigned to the
`script` variable. Therefore, the input script filename in the `arguments` is replaced by the `{script}` placeholder.
The actual script is then added to the `nodes` dictionary, where the content of the `script` is wrapped in AiiDA's
`SinglefileData` node class. This allows the script to be stored in the provenance graph. When `launch_shell_job` is
called, it will ensure that the content of the `script` is copied to a file inside the working directory where `lmp` is
invoked and the `{script}` placeholder is replaced with the filename.

The `launch_shell_job` function returns a tuple of two elements once the command has completed:

- `results`: A dictionary of the outputs produced by the command
- `node`: The node that represents the execution of the command in AiiDA's provenance graph

These outputs can be used to inspect the results of the executed command:

:::{literalinclude} include/scripts/lammps.py
:lines: 45-48
:caption: Printing the state of the completed command and its results
:::

The output should look something like the following:

```console
Calculation terminated: ProcessState.FINISHED
Outputs:
stderr: SinglefileData<100>
stdout: SinglefileData<101>
```

The numbers between the `<>` brackets are the pks of the output nodes. In this case, there are just two `SinglefileData`
nodes that contain the output that was written to the `stdout` and `stderr` file descriptors. Their content can be
retrieved by loading the node through its pk using AiiDA's `load_node` function, and then calling the `get_content`
method:

:::{code-block} python
from aiida.orm import load_node
node = load_node(101)
print(node.get_content())
:::

This should print the output written by LAMMPS which looks something like the following:

:::{code-block} console
LAMMPS (20 Nov 2019)
Lattice spacing in x,y,z = 1.6796 1.6796 1.6796
Created orthogonal box = (0 0 0) to (33.5919 33.5919 33.5919)
  1 by 1 by 1 MPI processor grid
Created 32000 atoms
  create_atoms CPU = 0.00462803 secs
Neighbor list info ...
  update every 20 steps, delay 0 steps, check no
  max neighbors/atom: 2000, page size: 100000
  master list distance cutoff = 2.8
  ghost atom cutoff = 2.8
  binsize = 1.4, bins = 24 24 24
  1 neighbor lists, perpetual/occasional/extra = 1 0 0
  (1) pair lj/cut, perpetual
      attributes: half, newton on
      pair build: half/bin/atomonly/newton
      stencil: half/bin/3d/newton
      bin: standard
Setting up Verlet run ...
  Unit style    : lj
  Current step  : 0
  Time step     : 0.005
Per MPI rank memory allocation (min/avg/max) = 13.82 | 13.82 | 13.82 Mbytes
Step Temp E_pair E_mol TotEng Press
       0         1.44   -6.7733681            0   -4.6134356   -5.0197073
     100    0.7574531   -5.7585055            0   -4.6223613   0.20726105
Loop time of 2.32985 on 1 procs for 100 steps with 32000 atoms

Performance: 18541.947 tau/day, 42.921 timesteps/s
100.0% CPU use with 1 MPI tasks x no OpenMP threads

MPI task timing breakdown:
Section |  min time  |  avg time  |  max time  |%varavg| %total
---------------------------------------------------------------
Pair    | 1.9495     | 1.9495     | 1.9495     |   0.0 | 83.67
Neigh   | 0.30639    | 0.30639    | 0.30639    |   0.0 | 13.15
Comm    | 0.026903   | 0.026903   | 0.026903   |   0.0 |  1.15
Output  | 0.0001828  | 0.0001828  | 0.0001828  |   0.0 |  0.01
Modify  | 0.040458   | 0.040458   | 0.040458   |   0.0 |  1.74
Other   |            | 0.006424   |            |       |  0.28

Nlocal:    32000 ave 32000 max 32000 min
Histogram: 1 0 0 0 0 0 0 0 0 0
Nghost:    19657 ave 19657 max 19657 min
Histogram: 1 0 0 0 0 0 0 0 0 0
Neighs:    1.20283e+06 ave 1.20283e+06 max 1.20283e+06 min
Histogram: 1 0 0 0 0 0 0 0 0 0

Total # of neighbors = 1202833
Ave neighs/atom = 37.5885
Neighbor list builds = 5
Dangerous builds not checked
Total wall time: 0:00:02
:::
