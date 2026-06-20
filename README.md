# cryoSPARC → RELION Particle Stack Transfer

A step-by-step pipeline (plus helper scripts) for exporting an extracted particle
stack from **cryoSPARC** and importing it into **RELION** for downstream jobs such as
2D/3D classification, subset selection, or polishing.

The conversion itself is done with **`csparc2star.py`** from
[Daniel Asarnow's `pyem`](https://github.com/asarnow/pyem). The extra scripts and
notes in this repo exist because a clean `.cs → .star` conversion is rarely enough on
its own: the optics metadata is often incomplete, the particle stacks have to be
mirrored on the RELION machine, and RELION refuses to read 2D stacks unless they have
the `.mrcs` extension. This README walks through every one of those gotchas in the
order you'll actually hit them.

> **Who this is for:** anyone moving particles from cryoSPARC to RELION. If you've
> never set up a Python/conda environment before, start at **Part 1A**. If you have,
> skip to **Part 1B** and then **Part 2**.

---

## What's in this repository

| File | What it does |
|------|--------------|
| `CHANGEME_rename_mrc_to_mrcs.py` | Renames the extracted `batch_*_restacked.mrc` files to `.mrcs` (the format RELION requires for 2D image stacks). |
| `CHANGEME_update_star_mrcs.py` | Applies a regex over the `.star` file so every `.mrc` reference in the image/micrograph column is rewritten to `.mrcs`, matching the renamed files. |
| `README.md` | This file. |

> ⚠️ **Rename these two scripts** to match what you actually committed, then update
> the `CHANGEME_...` references throughout this README. The names above are
> placeholders.

---

## The short version (overview)

1. **Convert** the cryoSPARC `.cs` file(s) to a RELION `.star` file with
   `csparc2star.py ... --inverty`.
2. **Fix the optics metadata** if RELION complains that defocus / box size /
   pixel-size values are missing.
3. **Mirror the particle stacks** on the machine running RELION, recreating the exact
   directory paths written inside the `.star` file.
4. **Convert `.mrc` → `.mrcs`** (both the files *and* the references inside the
   `.star` file).
5. **Import into RELION** and run your job (e.g. Subset Selection).

Each step below also lists the error you'll see if you skip it, so you can jump
straight to the fix.

---

## Prerequisites

- Access to the cryoSPARC project/job directory containing your extracted particles
  (the `*_restacked_particles.cs` / `particles.cs` and `passthrough_particles.cs`
  files, plus the extracted `.mrc` stacks).
- Access to the machine/cluster where RELION runs, with somewhere to put the mirrored
  particle stacks.
- A working `conda`/`mamba` (or `miniforge`) installation — see Part 1.
- RELION **3.1 or newer** (the optics-group `.star` format described here is a 3.1+
  thing).

---

## Part 1 — Setting up your environment

`csparc2star.py` ships inside the `pyem` package. You install `pyem` into an isolated
**virtual environment** so its dependencies don't collide with anything else on the
system.

### Part 1A — "I've never done this before"

A *virtual environment* is just a self-contained folder of Python packages. You
create one, "activate" it, install your tools into it, and activate it again whenever
you want to use those tools. Nothing you do inside it affects the rest of your
computer.

**Step 1 — Get conda (via Miniforge).**
If you don't already have `conda`, install **Miniforge**, which gives you `conda` and
the faster `mamba` and is pre-configured for the `conda-forge` channel that `pyem`
needs:

- Download and install from <https://github.com/conda-forge/miniforge>.
- Close and reopen your terminal afterwards. You should see `(base)` at the start of
  your prompt — that means conda is active.

**Step 2 — Install pyem (the easy way).**
The simplest install puts `pyem` straight into a fresh environment from
`conda-forge`:

```bash
# create an environment called "pyem" and install the package into it
conda create -n pyem -c conda-forge python=3.11 pyem
```

> If you used Miniforge/mamba you can drop the `-c conda-forge` and use `mamba`:
> `mamba create -n pyem python=3.11 pyem`

**Step 3 — Activate it.**
Every time you want to run the conversion, first do:

```bash
conda activate pyem
```

Your prompt changes to `(pyem)` — now `csparc2star.py` is on your `PATH`. Check it
works:

```bash
csparc2star.py -h
```

If you see the help/usage text, you're ready for **Part 2**. To leave the environment
later, run `conda deactivate`.

> **Common install snag:** errors about packages not being found (`pyfftw`, `healpy`,
> `pathos`, …) almost always mean conda isn't using the `conda-forge` channel. Either
> use Miniforge (recommended) or add the channel explicitly:
> ```bash
> conda config --add channels conda-forge
> conda config --set channel_priority strict
> ```

### Part 1B — "I know what I'm doing" (TL;DR)

Quick install from conda-forge:

```bash
mamba install pyem          # into any existing env (Python ≥ 3.9)
# or: conda install -c conda-forge pyem
```

Development install (editable, with the CLI scripts on your `PATH`):

```bash
mamba create -n pyem python=3.11
mamba activate pyem
mamba install numba numpy scipy matplotlib seaborn pandas pathos pyfftw healpy natsort starfile ipython
git clone https://github.com/asarnow/pyem.git
cd pyem
pip install --no-dependencies -e .
export PATH=$(realpath pyem/cli):$PATH
```

> **Optional shortcut:** the [`cs2star`](https://github.com/brisvag/cs2star) wrapper
> automates much of Part 2 — it traverses a cryoSPARC job directory, symlinks the
> `.mrc` files while renaming them to `.mrcs`, and updates the corresponding column in
> the `.star` file. It's worth a look if you'd rather not run the steps below by hand,
> though it still relies on `pyem` under the hood.

---

## Part 2 — The conversion pipeline

Run all of this with your `pyem` environment **activated** (`conda activate pyem`).

### Step 1 — Convert `.cs` → `.star`

```bash
csparc2star.py \
    cryosparc_P167_restacked_particles.cs \
    passthrough_particles.cs \
    particles_blob.star \
    --inverty
```

- `--inverty` flips the Y axis, which is the standard correction needed when going
  from cryoSPARC to RELION. Keep it unless you have a specific reason not to.
- **Include the `passthrough_particles.cs` file** (second positional argument). This
  is the single most common fix for missing CTF/defocus values — the passthrough file
  is where cryoSPARC keeps a lot of that per-particle metadata. The original version
  of this pipeline passed only the restacked file and got **"Defocus values not
  found"** as a result.
- If your refinement box size differs from the extracted particle box size, add
  `--boxsize <N>`.

### Step 2 — Fix the optics metadata (if needed)

RELION 3.1+ expects a `data_optics` block at the top of the `.star` file. If it's
incomplete, importing fails with errors like *"box sizes not available"* or
*"not all necessary variables defined in `_optics.star`: rlnPixelSize, rlnVoltage and
rlnSphericalAberration"*.

**Preferred fix:** redo Step 1 with the passthrough file and `--boxsize` — that
usually populates the optics block automatically.

**Fallback (manual):** if values are still missing, open the `.star` file and make
sure the `data_optics` block contains a value for every one of these columns:

```
_rlnImagePixelSize
_rlnOpticsGroup
_rlnImageSize
_rlnImageDimensionality
_rlnVoltage
_rlnSphericalAberration
```

These are constant across the dataset (e.g. one voltage, one pixel size), so each is a
single repeated value for the optics group. Use your microscope/acquisition parameters
for voltage, spherical aberration, and pixel size; `_rlnImageSize` is your box size in
pixels and `_rlnImageDimensionality` is `2` for a 2D particle stack.

> If RELION still rejects a star file that looks correct, try running it through
> `relion_convert_star` to regenerate it in the current 3.1+ format.

### Step 3 — Merge multiple `.cs` files into one `.star` (if applicable)

If your particles are spread across several `.cs` files, merge them into a single
`.star` file so RELION imports them as one stack. **Exclude the 2D and 3D alignment
`.cs` files** from this merge — you want the particle/blob metadata, not the alignment
outputs.

### Step 4 — Mirror the particle stacks on the RELION machine

The `.star` file stores a **path** to each `.mrc` stack, not the image data itself.
RELION reads those paths literally, so the stacks must exist on the RELION machine at
**exactly** the paths written in the file. If they don't, your job fails with errors
like *"Could not find the restack files."*

Do this:

1. Copy/download the extracted `.mrc` stacks from wherever cryoSPARC wrote them onto
   the machine running RELION.
2. Recreate the **same directory structure** that appears in the
   `rlnImageName` / `rlnMicrographName` column of the `.star` file. Symlinks are fine
   and save disk space:
   ```bash
   # example: link the extracted stacks into your RELION project, mirroring the path
   ln -s /path/to/cryosparc/extract/job/*.mrc /path/to/relion/project/<mirrored/path>/
   ```

> In the original setup these were two specific hosts (stacks generated on one
> machine, RELION run on another). Substitute your own hostnames/paths — the principle
> is the same: **the files must sit where the `.star` file says they do.**

### Step 5 — Convert `.mrc` → `.mrcs`

RELION will not use `.mrc` files as 2D image stacks — it requires the `.mrcs`
extension. You'll see Subset Selection (or any 2D job) fail until you fix this. There
are **two halves** to the fix, and you need both:

**5a. Rename the actual files** on the RELION machine:

```bash
python CHANGEME_rename_mrc_to_mrcs.py /path/to/mirrored/stacks/
```

<details>
<summary>What this is doing (the one-liner equivalent)</summary>

```bash
for f in *.mrc; do mv -- "$f" "${f}s"; done
```
The Python script does the same thing safely across a directory; prefer it over the
one-liner so the behaviour is reproducible for other users.
</details>

**5b. Update the references inside the `.star` file** so they point at `.mrcs`
instead of `.mrc`:

```bash
python CHANGEME_update_star_mrcs.py particles_blob.star
```

This regex-rewrites every `*.mrc` in the image/micrograph column to `*.mrcs`. If you
rename the files (5a) but not the references (5b), or vice versa, RELION still won't
find the stacks.

### Step 6 — Import into RELION and run your job

1. In RELION, **Import** the final `.star` file.
2. Run your downstream job — e.g. **Subset Selection** for 2D class cleanup.

If the import succeeds and the job finds its particles, the transfer worked.

---

## Troubleshooting (errors → fixes)

These are the failures encountered while building this pipeline, in roughly the order
they tend to appear:

| Symptom | Cause | Fix |
|---------|-------|-----|
| `csparc2star.py` prints **"Defocus values not found"** | CTF/defocus metadata wasn't in the input | Include `passthrough_particles.cs` in the conversion (Step 1). |
| RELION import: *"box sizes not available"* / missing `rlnPixelSize`, `rlnVoltage`, `rlnSphericalAberration` | Incomplete `data_optics` block | Re-convert with the passthrough file + `--boxsize`, or manually add the optics columns (Step 2). Try `relion_convert_star` if it persists. |
| RELION **import fails** even though the file looks complete | Star file not in 3.1+ optics format | Ensure the `data_optics` block is present and complete (Step 2). |
| Job fails: **"Could not find the restack files"** | Stacks aren't on the RELION machine at the paths in the `.star` file | Mirror the stacks and recreate the directory structure (Step 4). |
| Subset Selection (or any 2D job) **fails on the image format** | RELION needs `.mrcs`, not `.mrc`, for 2D stacks | Rename files **and** update the `.star` references (Step 5a + 5b). |

---

## Notes & credits

- Conversion is performed by **`csparc2star.py`** from **pyem** by Daniel Asarnow.
  Please cite it if you use this pipeline:
  > Asarnow, D., Palovcak, E., Cheng, Y. *UCSF pyem v0.5.* Zenodo (2019).
  > https://doi.org/10.5281/zenodo.3576630
- pyem documentation and wiki: <https://github.com/asarnow/pyem>
- Optional automation wrapper: <https://github.com/brisvag/cs2star>

This repository documents one working route through a process that has many
machine- and dataset-specific details. Paths, hostnames, and exact parameters
(voltage, pixel size, box size) will differ for your setup — change them accordingly.