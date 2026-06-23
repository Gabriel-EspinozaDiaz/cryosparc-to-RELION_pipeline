# Cryosparc to RELION Pipeline

A quick guide on how to move Cryosparc particles into RELION for continuation of 

## What to do in Cryosparc

- In the Builder tab, select the job Restack Particles
- Input extracted particles (from particle extraction, 2D classification, etc.)
- Run the job
- Once the job is finish, open it
- Proceed to the 'Outputs' tab
- Download the following outputs (circled in blue):
    - particle.blob (cryosparc_Pn_restacked_particles.cs)
    - particles.ctf (cryosparc_Pn_Jn_passthrough_particles (n))
    - particles.pick_stats (cryosparc_Pn_Jn_passthrough_particles (n))
    - particles.alignments2D (cryosparc_Pn_Jn_passthrough_particles (n))
    - particles.filament (cryosparc_Pn_Jn_passthrough_particles (n))
    - particles.location (cryosparc_Pn_Jn_passthrough_particles (n))
- Copy the directory name of the innermost directory, found in the (directory is circled in orange, in this case the innermost directory is 'J521'). This will be referred to as the 'job'

## What to do in Terminal

- Organise the particle files into a directory
- Navigate to the directory
- Activate a virtual environment (recommended)
- Run the following command to download all dependencies

```bash
curl -O https://raw.githubusercontent.com///main/requirements.txt
pip install -r requirements.txt
```

- Run this command to convert all of the files included, with all of filenames that you've just downloaded in place of the  <particles-n> 

```bash

```

### For Personal Computer Users

- create a new project directory for relion

```bash 
mkdir relion-project-directory
cd relion-project-directory
relion
```

- confirm that you would like to start a new relion project
- exit relion gui


- Copy the restack directory directly to 

```bash
cp -r ./pathway/to/job/restack ./pathway/to/relion/project/directory/restack
```

### For Cluster Users

- enter the login node by secure protocol

```bash 
ssh username@login-node-server-address
```

- create a new project

```bash 
mkdir relion-project-directory
cd relion-project-directory
relion
```

- confirm that you would like to start a new relion project
- exit relion gui
- Copy the restack directory through secure protocol from the cryosparc master node to the relion login node

```bash
scp -r username@cryosparc-master-node-address:pathway/to/job/restack ./restack
scp -r ./restack username@login-node-server-address:pathway/to/relion/directory/restack
```





