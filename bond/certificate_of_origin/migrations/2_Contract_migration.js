// Place your contract inputs here
var CoO = artifacts.require("CoO")

var UserLogic = artifacts.require("UserLogic")
var UserDB = artifacts.require("UserDB")

var AssetProducingRegistryLogic = artifacts.require("AssetProducingRegistryLogic")
var AssetProducingRegistryDB = artifacts.require("AssetProducingRegistryDB")

var AssetConsumingRegistryLogic = artifacts.require("AssetConsumingRegistryLogic")
var AssetConsumingRegistryDB = artifacts.require("AssetConsumingRegistryDB")

var CertificateLogic = artifacts.require("CertificateLogic")
var CertificateDB = artifacts.require("CertificateDB")

var UserLogicUpdate = artifacts.require("UserLogic")
var AssetProducingRegistryLogicUpdate = artifacts.require("AssetProducingRegistryLogic")
var CertificateLogicUpdate = artifacts.require("CertificateLogic")

var DemandLogic = artifacts.require("DemandLogic")
var DemandDB = artifacts.require("DemandDB")


// This is the actual migration function. All deployment is happening here
module.exports = async (deployer, network, accounts) => {
  //deploying CoO contract
  var cooInstance
  var certificateLogicInstance
  var userLogicInstance
  var assetProducingRegistryLogicInstance
  var assetConsumingLogicInstance
  var demandLogicInstance


  var certificateLogicUpdateInstance
  var userLogicUpdateInstance


  await deployer.deploy(CoO, { from: "0x3B07F15EFb10f29B3fC222fb7E717e9Af0cC4243", gasPrice: 0 }).then(
    async () => { cooInstance = await CoO.deployed() }
  ).then(async () => {
    await deployer.deploy(CertificateLogic, cooInstance.address, { gasPrice: 0, gas: 7000000, from: "0x3B07F15EFb10f29B3fC222fb7E717e9Af0cC4243" }).then(
      async () => { certificateLogicInstance = await CertificateLogic.deployed() }
    )
  }).then(async () => {
    await deployer.deploy(CertificateDB, CertificateLogic.address, { gasPrice: 0, gas: 7000000, from: "0x3B07F15EFb10f29B3fC222fb7E717e9Af0cC4243" }).then(
      async () => { await CertificateDB.deployed() }
    )
  }).then(async () => {
    await deployer.deploy(UserLogic, cooInstance.address, { gasPrice: 0, gas: 7000000, from: "0x3B07F15EFb10f29B3fC222fb7E717e9Af0cC4243" }).then(
      async () => { userLogicInstance = await UserLogic.deployed() }
    )
  }).then(async () => {
    await deployer.deploy(UserDB, UserLogic.address, { gasPrice: 0, gas: 7000000, from: "0x3B07F15EFb10f29B3fC222fb7E717e9Af0cC4243" }).then(
      async () => { await UserDB.deployed() }
    )
  }).then(async () => {
    await deployer.deploy(DemandLogic, cooInstance.address, { gasPrice: 0, gas: 8000000, from: "0x3B07F15EFb10f29B3fC222fb7E717e9Af0cC4243" }).then(
      async () => { demandLogicInstance = await DemandLogic.deployed() }
    )
  })

    .then(async () => {
      await deployer.deploy(DemandDB, DemandLogic.address, { gasPrice: 0, gas: 10000000, from: "0x3B07F15EFb10f29B3fC222fb7E717e9Af0cC4243" }).then(
        async () => { await DemandDB.deployed() }
      )
    })
    .then(async () => {
      await deployer.deploy(AssetProducingRegistryLogic, cooInstance.address, { gasPrice: 0, gas: 10000000, from: "0x3B07F15EFb10f29B3fC222fb7E717e9Af0cC4243" }).then(
        async () => { assetProducingRegistryLogicInstance = await AssetProducingRegistryLogic.deployed() }
      )
    }).then(async () => {
      await deployer.deploy(AssetProducingRegistryDB, assetProducingRegistryLogicInstance.address, { gasPrice: 0, gas: 10000000, from: "0x3B07F15EFb10f29B3fC222fb7E717e9Af0cC4243" }).then(
        async () => { await AssetProducingRegistryDB.deployed() }
      )
    })
    .then(async () => {
      await deployer.deploy(AssetConsumingRegistryLogic, cooInstance.address, { gasPrice: 0, gas: 10000000, from: "0x3B07F15EFb10f29B3fC222fb7E717e9Af0cC4243" }).then(
        async () => { assetConsumingRegistryLogicInstance = await AssetConsumingRegistryLogic.deployed() }
      )
    }).then(async () => {
      await deployer.deploy(AssetConsumingRegistryDB, assetConsumingRegistryLogicInstance.address, { gasPrice: 0, gas: 10000000, from: "0x3B07F15EFb10f29B3fC222fb7E717e9Af0cC4243" }).then(
        async () => { await AssetConsumingRegistryDB.deployed() }
      )
    })
    .then(async () => {
      console.log("init userlogic")
      await userLogicInstance.init(UserDB.address, { gasPrice: 0, from: "0x3B07F15EFb10f29B3fC222fb7E717e9Af0cC4243" })
    })
    .then(async () => {
      console.log("init AssetProducing")
      await assetProducingRegistryLogicInstance.init(AssetProducingRegistryDB.address, { gasPrice: 0, from: "0x3B07F15EFb10f29B3fC222fb7E717e9Af0cC4243" })
    })
    .then(async () => {
      console.log("init certlogic")
      await certificateLogicInstance.init(CertificateDB.address, { gasPrice: 0, from: "0x3B07F15EFb10f29B3fC222fb7E717e9Af0cC4243" })
    })
    .then(async () => {
      console.log("init demandlogic")
      await demandLogicInstance.init(DemandDB.address, { gasPrice: 0, from: "0x3B07F15EFb10f29B3fC222fb7E717e9Af0cC4243" })
    })
    .then(async () => {
      console.log("init assetconsuming")
      await assetConsumingRegistryLogicInstance.init(AssetConsumingRegistryDB.address, { gasPrice: 0, from: "0x3B07F15EFb10f29B3fC222fb7E717e9Af0cC4243" })
    })
    .then(async () => {
      console.log("init COO")
      await cooInstance.init(UserLogic.address, AssetProducingRegistryLogic.address, CertificateLogic.address, DemandLogic.address, AssetConsumingRegistryLogic.address, { gasPrice: 0, from: "0x3B07F15EFb10f29B3fC222fb7E717e9Af0cC4243" })
    })
    .then(async () => {
      // accounts[2] = assetAdmin
      console.log("setUser1")
      await userLogicInstance.setUser("0x583b3e16a27f3db4bdc4c1a5452eeed14619c8da",
        web3.fromAscii('John'),
        web3.fromAscii("Doe"),
        web3.fromAscii('Organization3'),
        web3.fromAscii('Main St'),
        web3.fromAscii('123'),
        web3.fromAscii('01234'),
        web3.fromAscii('Anytown'),
        web3.fromAscii('USA'),
        web3.fromAscii('AnyState'), { gasPrice: 0, from: "0x3B07F15EFb10f29B3fC222fb7E717e9Af0cC4243" })
    })
    .then(async () => {
      console.log("setUser2")
      // accounts[1] = userAdmin
      await userLogicInstance.setUser("0x71c31ff1faa17b1cb5189fd845e0cca650d215d3",
        web3.fromAscii('John-user'),
        web3.fromAscii("Doe-user"),
        web3.fromAscii('Organization1'),
        web3.fromAscii('Main St'),
        web3.fromAscii('123'),
        web3.fromAscii('01234'),
        web3.fromAscii('Anytown'),
        web3.fromAscii('USA'),
        web3.fromAscii('AnyState'), { gasPrice: 0, from: "0x3B07F15EFb10f29B3fC222fb7E717e9Af0cC4243" })
    })
    .then(async () => {
      console.log("setUser3")
      // accounts[2] = assetAdmin
      await userLogicInstance.setUser("0xcea1c413a570654fa85e78f7c17b755563fec5a5",
        web3.fromAscii('John-asset'),
        web3.fromAscii("Doe-asset"),
        web3.fromAscii('Organization2'),
        web3.fromAscii('Main St'),
        web3.fromAscii('123'),
        web3.fromAscii('01234'),
        web3.fromAscii('Anytown'),
        web3.fromAscii('USA'),
        web3.fromAscii('AnyState'), { gasPrice: 0, from: "0x3B07F15EFb10f29B3fC222fb7E717e9Af0cC4243" })
    })
    .then(async () => {
      // accounts[2] = assetAdmin
      console.log("setUser4")

      await userLogicInstance.setUser("0x51ba6877a2c4580d50f7ceece02e2f24e78ef123",
        web3.fromAscii('John-testadmin'),
        web3.fromAscii("Doe-testadmin"),
        web3.fromAscii('Organization5'),
        web3.fromAscii('Main St'),
        web3.fromAscii('123'),
        web3.fromAscii('01234'),
        web3.fromAscii('Anytown'),
        web3.fromAscii('USA'),
        web3.fromAscii('AnyState'), { gasPrice: 0, from: "0x3B07F15EFb10f29B3fC222fb7E717e9Af0cC4243" })
    })
    .then(async () => {
      // accounts[2] = assetAdmin
      console.log("setUser5")

      await userLogicInstance.setUser("0x3b07f15efb10f29b3fc222fb7e717e9af0cc4243",
        web3.fromAscii('John-owner'),
        web3.fromAscii("Doe-owner"),
        web3.fromAscii('Organization0'),
        web3.fromAscii('Main St'),
        web3.fromAscii('123'),
        web3.fromAscii('01234'),
        web3.fromAscii('Anytown'),
        web3.fromAscii('USA'),
        web3.fromAscii('AnyState'), { gasPrice: 0, from: "0x3B07F15EFb10f29B3fC222fb7E717e9Af0cC4243" })
    })
    .then(async () => {
      // accounts[2] = assetAdmin
      console.log("setUser6")
      await userLogicInstance.setUser("0x84a2c086ffa013d06285cdd303556ec9be5a1ff7",
        web3.fromAscii('John-tradadmin'),
        web3.fromAscii("Doe-tradeadmin"),
        web3.fromAscii('Organization9'),
        web3.fromAscii('Main St'),
        web3.fromAscii('123'),
        web3.fromAscii('01234'),
        web3.fromAscii('Anytown'),
        web3.fromAscii('USA'),
        web3.fromAscii('AnyState'), { gasPrice: 0, from: "0x3B07F15EFb10f29B3fC222fb7E717e9Af0cC4243" })
    })
    .then(async () => {
      // accounts[1] = userAdmin
      console.log("userAdmin")

      await userLogicInstance.setRoles("0x71c31ff1faa17b1cb5189fd845e0cca650d215d3", 2, { gasPrice: 0, from: "0x3B07F15EFb10f29B3fC222fb7E717e9Af0cC4243" })
    })
    .then(async () => {
      // accounts[2] = assetAdmin
      console.log("assetAdmin")

      await userLogicInstance.setRoles("0xcea1c413a570654fa85e78f7c17b755563fec5a5", 4, { gasPrice: 0, from: "0x3B07F15EFb10f29B3fC222fb7E717e9Af0cC4243" })
    })
    .then(async () => {
      console.log("agreementAdmin")

      // accounts[2] = agreement-Admin
      await userLogicInstance.setRoles("0x84a2c086ffa013d06285cdd303556ec9be5a1ff7", 8, { gasPrice: 0, from: "0x3B07F15EFb10f29B3fC222fb7E717e9Af0cC4243" })
    })
    .then(async () => {
      console.log("addTraderRole")

      // accounts[2] = agreement-Admin
      await userLogicInstance.addTraderRole("0x84a2c086ffa013d06285cdd303556ec9be5a1ff7", { gasPrice: 0, from: "0x3B07F15EFb10f29B3fC222fb7E717e9Af0cC4243" })
    })
    .then(async () => {
      console.log("addTraderRole")

      // accounts[2] = agreement-Admin
      await userLogicInstance.addTraderRole("0x71c31ff1faa17b1cb5189fd845e0cca650d215d3", { gasPrice: 0, from: "0x3B07F15EFb10f29B3fC222fb7E717e9Af0cC4243" })
    })
    .then(async () => {
      // accounts[2] = agreement-Admin
      console.log("addAssetManager")

      await userLogicInstance.addAssetManagerRole("0x71c31ff1faa17b1cb5189fd845e0cca650d215d3", { gasPrice: 0, from: "0x3B07F15EFb10f29B3fC222fb7E717e9Af0cC4243" })
    })
    .then(async () => {
      console.log("addTraderRole")

      // accounts[2] = agreement-Admin
      await userLogicInstance.addTraderRole("0x3b07f15efb10f29b3fc222fb7e717e9af0cc4243", { gasPrice: 0, from: "0x3B07F15EFb10f29B3fC222fb7E717e9Af0cC4243" })
    }).then(async () => {
      console.log("addAssetManager")

      // accounts[2] = agreement-Admin
      await userLogicInstance.addAssetManagerRole("0x3b07f15efb10f29b3fc222fb7e717e9af0cc4243", { gasPrice: 0, from: "0x3B07F15EFb10f29B3fC222fb7E717e9Af0cC4243" })
    })
    .then(async () => {
      console.log("matcher")

      // accounts[8] = matcher
      await userLogicInstance.addMatcherRole("0x343854a430653571b4de6bf2b8c475f828036c30", { gasPrice: 0, from: "0x3B07F15EFb10f29B3fC222fb7E717e9Af0cC4243" })
    })



}