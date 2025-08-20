#!/usr/bin/env bash
set -euo pipefail
circom circuits/policy.circom --r1cs --wasm --sym -o build
snarkjs groth16 setup build/policy.r1cs pot12_final.ptau build/policy_0000.zkey
snarkjs zkey export verificationkey build/policy_0000.zkey build/verification_key.json
