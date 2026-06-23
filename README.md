# CryoSPARC to RELION Pipeline

A quick guide on how to move CryoSPARC particles into RELION for continuation of cryo-EM postprocessing, specifically with CryoSPARC-curated particles. 

## What to do in the Cryosparc web interface

- In the Builder tab, select the job Restack Particles
- Input extracted particles (from particle extraction, 2D classification, etc.)
- Run the job
- Once the job is finish, open it
- Proceed to the 'Outputs' tab
- Download the following outputs (circled in blue):
    - particle.blob (cryosparc_project_restacked_particles.cs)
    - particles.ctf (cryosparc_project_job_passthrough_particles (n))
    - particles.pick_stats (cryosparc_project_job_passthrough_particles (n))
    - particles.alignments2D (cryosparc_project_job_passthrough_particles (n))
    - particles.filament (cryosparc_project_job_passthrough_particles (n))
    - particles.location (cryosparc_project_job_passthrough_particles (n))
- Copy the directory name of the innermost directory, found in the (directory is circled in orange, in this case the innermost directory is 'J521'). This will be referred to as the 'job'. If the word 'job' is used in any pathway directories, replace it with this directory name. 

![cryosparc_interface_should_be_here](https://github.com/Gabriel-EspinozaDiaz/cryosparc-to-RELION_pipeline/blob/main/cryosparc_interface_example.png)

## What to do in Terminal 

- Make a directory to store your particles

```bash
mkdir Cryosparc_to_RELION_Pipeline
```

- Move the particle files into a directory
- Move to the directory
- Activate a virtual environment (recommended)
- Run the following command to download all dependencies

```bash
curl -O https://github.com/Gabriel-EspinozaDiaz/cryosparc-to-RELION_pipeline/blob/main/requirements.txt
curl -O https://github.com/Gabriel-EspinozaDiaz/cryosparc-to-RELION_pipeline/blob/main/mrc2mrcs.py
pip install -r requirements.txt
```

- Run this command to prepare the files from processing, and process them using csparc2star and mrc2mrcs. In each instance where 'project' and 'job' appear, the terms must be replaced with the relevant job and project IDs. This will output the file 'relion_incompatible_particles.star'

```bash
for f in *; do tmp="${f//[()]/}"; mv "$f" "${tmp// /_}"; done
csparc2star.py --inverty cryosparc_project_job_passthrough_particles_1.cs cryosparc_project_job_passthrough_particles_2.cs cryosparc_project_job_passthrough_particles_3.cs cryosparc_project_job_passthrough_particles_4.cs cryosparc_project_job_passthrough_particles_5.cs cryosparc_project_job_passthrough_particles.cs cryosparc_project_restacked_particles.cs relion_incompatible_particles.star
python mrc2mrcs.py relion_incompatible_particles.star relion_compatible_particles.star
```

- If you are running RELION from your own computer, proceed to SUBSECTION A. If you are using RELION on a cluster through ssh, proceed to SUBSECTION B. 

### SUBSECTION A: For users running RELION on a personal computer

- create a new project directory for relion

```bash 
mkdir relion-project-directory
cd relion-project-directory
relion
```

- confirm that you would like to start a new relion project
- exit relion gui


- Copy the restack directory directly to the 'job' directory

```bash
cp -r ./pathway/to/job/restack ./pathway/to/relion-project-directory/job/restack
```

- move to the restack directory, and run the following command to reformat the filenames

```bash
cd ./pathway/to/relion-project-directory/job/restack
for f in *restacked.mrc; do mv -- "$f" "${f}s"; done
```

- move the star file to the relion directory

```bash 
mv ./pathway/to/relion_compatible_particles.star ./pathway/to/relion_directory/relion_compatible_particles.star
```

- reopen the RELION gui

```bash
relion
```

- Select the 'Import' job
- In the 'Movies/mics' tab, select 'No' for the 'Import raw micrographs/movies' field
- In the 'Others' tab, select 'Yes' for the 'Import other node types' field
- input the pathway to relion_compatible_particles.star in the 'Input File' field
- Select 'Particle STAR file (.star)' in the 'Node type' field
- Run the job

### SUBSECTION B: For users running RELION on a cluster

- enter the login node by secure protocol

```bash 
ssh username@login-node-server-address
```

- create a new project directory 

```bash 
mkdir relion-project-directory
cd relion-project-directory
relion
```

- confirm that you would like to start a new relion project
- exit relion gui
- make a directory named after 'job' (the same name from the cryosparc details panel)

```bash
mkdir 'job'
```

- exit the cluster

```bash
exit
```

- Copy the restack directory through secure protocol from the cryosparc master node to the relion login node

```bash
scp -r username@cryosparc-master-node-address:pathway/to/job/restack ./restack
scp -r ./restack username@login-node-server-address:pathway/to/relion-project-directory/job/restack
```





