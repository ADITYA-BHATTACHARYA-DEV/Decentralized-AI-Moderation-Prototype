// Open Merkle Proof Modal
function openMerkleModal(proof) {
    alert("Merkle Proof: " + proof.join("\n"));
}

// Countdown timer for VDF
function startVDFTimer(seconds, elementId) {
    let counter = seconds;
    const el = document.getElementById(elementId);
    const interval = setInterval(() => {
        el.innerText = `VDF Delay: ${counter}s`;
        counter--;
        if(counter < 0) clearInterval(interval);
    }, 1000);
}

// Open blockchain link
function openBlockchainLink(txHash) {
    window.open("https://blockchain.explorer/tx/" + txHash, "_blank");
}
