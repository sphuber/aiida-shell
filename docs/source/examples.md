# Examples

This page includes examples of real-life applications of `aiida-shell`. This should hopefully give a good idea of how
its functionality can be used and how it can be applied to other codes and use-cases.

:::{toctree}
:hidden: true
:maxdepth: 0
examples/lammps.md
examples/gromacs.md
examples/qe.md
:::

:::{card}
:link: examples-lammps
:link-type: ref

{{ logo_shell }} LAMMPS
^^^
Run a LAMMPS calculation simulating the NVE ensemble of a simple Lennard-Jones fluid.

Concepts covered:
* Run a command with `aiida-shell`
* Define command line arguments
* Pass a file as input
* Inspect results and output

+++
::::{list-table}

* - {fa}`fa-sharp fa-regular fa-clock aiida-green` 15 min
  - {fa}`fa-regular fa-lg fa-thermometer-0 aiida-green` [Beginner]{.aiida-green}
::::
:::

:::{card}
:link: examples-gromacs
:link-type: ref

{{ logo_shell }} GROMACS
^^^
Use GROMACS to minimize the energy of a lysozyme protein dissolved in water.

Concepts covered:
* Preparing and modifying inputs and outputs in Python
* Specifying output files
* Redirecting output streams such as `stderr`
* Using outputs of a command as inputs for another
* Deal with commands that prompt

+++
::::{list-table}
* - {fa}`fa-sharp fa-regular fa-clock aiida-orange` 30 min
  - {fa}`fa-regular fa-lg fa-thermometer-2 aiida-orange` [Intermediate]{.aiida-orange}
::::
:::

:::{card}
:link: examples-qe
:link-type: ref

{{ logo_shell }} Quantum ESPRESSO
^^^
Use Quantum ESPRESSO to compute the electronic band structure of the gallium arsenide semiconductor.

Concepts covered:
* Passing folders of files as input
* Retrieving folders as output
* Controlling file and folder names of inputs
* Running commands with MPI
* Running command on remote computers

+++
::::{list-table}

* - {fa}`fa-sharp fa-regular fa-clock aiida-red` 45 min
  - {fa}`fa-regular fa-lg fa-thermometer-4 aiida-red` [Advanced]{.aiida-red}
::::
:::
