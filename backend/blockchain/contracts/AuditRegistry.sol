// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract AuditRegistry {
    event Anchored(bytes32 indexed merkleRoot, bytes32 indexed modelHash, string contentId, address sender);

    function anchor(bytes32 merkleRoot, bytes32 modelHash, string calldata contentId) external {
        emit Anchored(merkleRoot, modelHash, contentId, msg.sender);
    }
}
