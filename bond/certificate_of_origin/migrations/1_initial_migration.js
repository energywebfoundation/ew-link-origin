var Migrations = artifacts.require("./Migrations.sol");

module.exports = function (deployer) {
  deployer.deploy(Migrations, { gasPrice: 0, from: "0x3B07F15EFb10f29B3fC222fb7E717e9Af0cC4243" });
};
