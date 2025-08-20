pragma circom 2.1.5;

// Toy circuit: checks that `score < 0.5` implies allow == 1, else 0.
// Inputs are public for demo; a real design would keep model internals private.
template PolicyCheck() {
    signal input score;       // e.g., 0..1 scaled by 1000
    signal input threshold;   // 500
    signal output allow;      // 1 if score < threshold else 0
    signal less;
    less <== threshold - score;
    // enforce: less > 0 -> allow == 1; else allow == 0
    // This is a toy; real circuits encode comparisons differently.
    allow <== less > 0;
}
component main = PolicyCheck();
