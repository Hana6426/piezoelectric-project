#!/usr/bin/env bash
# Usage: ./scripts/run_scf.sh input.in > output.out

if [ $# -ne 1 ]; then
  echo "Usage: $0 input.in"
  exit 1
fi

mpirun -np 4 pw.x -in "$1"
