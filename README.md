# Cryosparc to RELION Pipeline

A quick guide on how to move Cryosparc particles into RELION for continuation of 

## What to do in Cryosparc

- In the Builder tab, select the job Restack Particles
- Input extracted particles (from particle extraction, 2D classification, etc.)
- Run the job
- Once the job is finished, download the following outputs:
    - particle.blob (cryosparc_Pn_restacked_particles.cs)
    - particles.ctf (cryosparc_Pn_Jn_passthrough_particles (n))
    - particles.pick_stats (cryosparc_Pn_Jn_passthrough_particles (n))
    - particles.alignments2D (cryosparc_Pn_Jn_passthrough_particles (n))
    - particles.filament (cryosparc_Pn_Jn_passthrough_particles (n))
    - particles.location (cryosparc_Pn_Jn_passthrough_particles (n))

## What to do in the Compiler

- Activate a virtual environment (guide here for anyone new to this)
- Run the following command to download all requirements

    - CONDA:

    - 

