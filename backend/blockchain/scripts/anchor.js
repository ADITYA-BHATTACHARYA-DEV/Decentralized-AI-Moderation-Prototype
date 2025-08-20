const { ethers } = require("hardhat");
const fs = require("fs");
async function main() {
  const addrs = JSON.parse(fs.readFileSync(__dirname + "/../addresses.json"));
  const artifact = JSON.parse(fs.readFileSync(__dirname + "/../abi/AuditRegistry.json"));
  const [signer] = await ethers.getSigners();
  const reg = new ethers.Contract(addrs.AuditRegistry, artifact.abi, signer);
  const merkle = "0x" + "11".repeat(32);
  const model = "0x" + "22".repeat(32);
  const tx = await reg.anchor(merkle, model, "demo-content");
  console.log("Anchored tx:", (await tx.wait()).transactionHash);
}
main().catch((e)=>{ console.error(e); process.exit(1); });
