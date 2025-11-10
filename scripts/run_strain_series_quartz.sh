#!/usr/bin/env bash
# Skeleton for automating finite-strain runs for quartz

BASE_IN="quartz_relaxed.in"
STRAINS=("-0.01" "-0.005" "0.0" "0.005" "0.01")

for eps in "${STRAINS[@]}"; do
  tag=$(printf "%+0.3f" "$eps" | tr '+' 'p' | tr '-' 'm' | tr '.' '_')
  outdir="quartz/finite_strain/eps_${tag}"
  mkdir -p "$outdir"

  # TODO: generate strained CELL_PARAMETERS from BASE_IN for this eps
  # and write to $outdir/quartz_eps_${tag}.in

  # Example:
  # mpirun -np 4 pw.x -in "$outdir/quartz_eps_${tag}.in" > "$outdir/quartz_eps_${tag}.out"
done
