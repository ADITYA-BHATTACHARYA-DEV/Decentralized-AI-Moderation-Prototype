const hre = require("hardhat");
const fs = require("fs");
async function main() {
  const AuditRegistry = await hre.ethers.getContractFactory("AuditRegistry");
  const reg = await AuditRegistry.deploy();
  await reg.deployed();
  console.log("AuditRegistry deployed to:", reg.address);
  fs.mkdirSync(__dirname + "/../abi", { recursive: true });
  fs.writeFileSync(__dirname + "/../abi/AuditRegistry.json", JSON.stringify(await hre.artifacts.readArtifact("AuditRegistry")));
  fs.writeFileSync(__dirname + "/../addresses.json", JSON.stringify({ AuditRegistry: reg.address }, null, 2));
}
main().catch((e)=>{ console.error(e); process.exit(1); });
