// Copyright 2018 Energy Web Foundation
// This file is part of the Origin Application brought to you by the Energy Web Foundation,
// a global non-profit organization focused on accelerating blockchain technology across the energy sector, 
// incorporated in Zug, Switzerland.
//
// The Origin Application is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
// This is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY and without an implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details, at <http://www.gnu.org/licenses/>.
//
// @authors: slock.it GmbH, Martin Kuechler, martin.kuchler@slock.it

var UserLogic = artifacts.require("UserLogic");
var AssetProducingRegistryLogic = artifacts.require("AssetProducingRegistryLogic")
var AssetProducingRegistryDB = artifacts.require("AssetProducingRegistryDB");
var CertificateLogic = artifacts.require("CertificateLogic");
var CoO = artifacts.require("CoO");

contract('RoleManagement', async function (accounts) {

  var UserLog,
    AssetLog,
    AssetDb,
    coo;

  it("should get the instances", async function () {
    UserLog = await UserLogic.deployed();
    AssetLog = await AssetProducingRegistryLogic.deployed()
    AssetDb = await AssetProducingRegistryDB.deployed()
    coo = await CoO.deployed()

    assert.isNotNull(UserLog)
    assert.isNotNull(AssetLog)
    assert.isNotNull(AssetDb)
    assert.isNotNull(coo)
  })

  it("should have initialized accounts[1] as userAdmin", async function () {
    // accounts[3] was never set, so he should not have any rights
    assert.isFalse(await UserLog.isRole(0, accounts[1]))
    assert.isTrue(await UserLog.isRole(1, accounts[1]))
    assert.isFalse(await UserLog.isRole(2, accounts[1]))
    assert.isFalse(await UserLog.isRole(3, accounts[1]))

  })

  it("should have initialized accounts[2] as assetAdmin", async function () {
    // accounts[3] was never set, so he should not have any rights
    assert.isFalse(await UserLog.isRole(0, accounts[2]))
    assert.isFalse(await UserLog.isRole(1, accounts[2]))
    assert.isTrue(await UserLog.isRole(2, accounts[2]))
    assert.isFalse(await UserLog.isRole(3, accounts[2]))

  })

  it("should have initialized accounts[9] as tradeAdmin", async function () {
    // accounts[3] was never set, so he should not have any rights
    assert.isFalse(await UserLog.isRole(0, accounts[9]))
    assert.isFalse(await UserLog.isRole(1, accounts[9]))
    assert.isFalse(await UserLog.isRole(2, accounts[9]))
    assert.isTrue(await UserLog.isRole(3, accounts[9]))

  })

  it("should not have inizialized accounts[3] with an admin-role", async function () {
    // accounts[3] was never set, so he should not have any rights
    assert.isFalse(await UserLog.isRole(0, accounts[3]))
    assert.isFalse(await UserLog.isRole(1, accounts[3]))
    assert.isFalse(await UserLog.isRole(2, accounts[3]))
    assert.isFalse(await UserLog.isRole(3, accounts[3]))
    assert.isFalse(await UserLog.isRole(4, accounts[3]))
    assert.isFalse(await UserLog.isRole(5, accounts[3]))

  })

  it("should be possible for an account to be both user- and assetAdmin at the same time", async function () {
    // accounts[3] was never set, so he should not have any rights
    await UserLog.setRoles(accounts[3], 6)

    assert.isFalse(await UserLog.isRole(0, accounts[3]))
    assert.isTrue(await UserLog.isRole(1, accounts[3]))
    assert.isTrue(await UserLog.isRole(2, accounts[3]))
  })

  /*
    it("should not allow other users to grant roles", async function () {
      assert.isFalse(await UserLog.isRole(0, accounts[5]))
      assert.isFalse(await UserLog.isRole(1, accounts[5]))
      assert.isFalse(await UserLog.isRole(2, accounts[5]))
  
      let failed = false
      try {
        let tx = await UserLog.setRoles(accounts[5], 1, { from: accounts[3] })
        if (tx.receipt.status == '0x00') failed = true
      }
      catch (ex) {
        failed = true
      }
      assert.isTrue(failed)
  
      assert.isFalse(await UserLog.isRole(0, accounts[5]))
      assert.isFalse(await UserLog.isRole(1, accounts[5]))
      assert.isFalse(await UserLog.isRole(2, accounts[5]))
    })*/

  it("should be able to register new TopAdmins", async function () {

    await UserLog.setRoles(accounts[5], 1)

    assert.isTrue(await UserLog.isRole(0, accounts[5]))
    assert.isFalse(await UserLog.isRole(1, accounts[5]))
    assert.isFalse(await UserLog.isRole(2, accounts[5]))
  })


  it("should only coo-Owner allow call setRoles roles", async function () {

    await UserLog.setRoles(accounts[3], 0)

    assert.isFalse(await UserLog.isRole(0, accounts[3]))
    assert.isFalse(await UserLog.isRole(1, accounts[3]))
    assert.isFalse(await UserLog.isRole(2, accounts[3]))
  })

  it("should not allow userAdmins to grant roles", async function () {

    try {
      await UserLog.setRoles(accounts[9], 0, { from: accounts[1] })
    } catch (ex) { }
    assert.isFalse(await UserLog.isRole(0, accounts[9]))
    assert.isFalse(await UserLog.isRole(1, accounts[9]))
    assert.isFalse(await UserLog.isRole(2, accounts[9]))

  })

  it("should not allow assetAdmins to grant roles", async function () {

    try {
      await UserLog.setRoles(accounts[9], 0, { from: accounts[2] })
    } catch (ex) { }
    assert.isFalse(await UserLog.isRole(0, accounts[3]))
    assert.isFalse(await UserLog.isRole(1, accounts[3]))
    assert.isFalse(await UserLog.isRole(2, accounts[3]))

  })

  it("should not allow users to revoke roles", async function () {

    let failed = false
    try {
      let tx = await UserLog.setRoles(accounts[5], 1, { from: accounts[3] })
      if (tx.receipt.status == '0x00') failed = true
    }
    catch (ex) {
      failed = true
    }
    assert.isTrue(failed)

  })

  /*
  it("should not allow userAdmins to revoke roles", async function () {

    let failed = false
    try {
      let tx = await UserLog.setRoles(accounts[5], 1, { from: accounts[1] })
      if (tx.receipt.status == '0x00') failed = true
    }
    catch (ex) {
      failed = true
    }
    assert.isTrue(failed)

  })*/

  it("should not allow assetAdmins to revoke roles", async function () {

    let failed = false
    try {
      let tx = await UserLog.setRoles(accounts[5], 1, { from: accounts[2] })
      if (tx.receipt.status == '0x00') failed = true
    }
    catch (ex) {
      failed = true
    }
    assert.isTrue(failed)

  })

  /*
    it("should allow TopAdmins to revoke roles", async function () {
  
      assert.isTrue(await UserLog.isRole(0, accounts[5]))
      assert.isFalse(await UserLog.isRole(1, accounts[5]))
      assert.isFalse(await UserLog.isRole(2, accounts[5]))
  
      await UserLog.setRoles(accounts[3], 0, { from: accounts[5] })
  
      assert.isFalse(await UserLog.isRole(0, accounts[3]))
      assert.isFalse(await UserLog.isRole(1, accounts[3]))
      assert.isFalse(await UserLog.isRole(2, accounts[3]))
    })
  */
  it("should return the correct role for TopAdmin", async function () {

    // accounts[0] deployed the contracts, so he is TopAdmin by default
    assert.isTrue(await UserLog.isRole(0, accounts[0]))
    assert.isTrue(await UserLog.isRole(1, accounts[0]))
    assert.isTrue(await UserLog.isRole(2, accounts[0]))
  })

  it("should return the correct role for userAdmin", async function () {
    // accounts[1] was set as userAdmin, so he should only have user-Rights
    assert.isFalse(await UserLog.isRole(0, accounts[1]))
    assert.isTrue(await UserLog.isRole(1, accounts[1]))
    assert.isFalse(await UserLog.isRole(2, accounts[1]))
  })

  it("should return the correct role for assetAdmins", async function () {
    // accounts[2] was set as assetAdmin, so he should only have user-Rights
    assert.isFalse(await UserLog.isRole(0, accounts[2]))
    assert.isFalse(await UserLog.isRole(1, accounts[2]))
    assert.isTrue(await UserLog.isRole(2, accounts[2]))
  })

  it("should return the correct role for non existing users", async function () {
    // accounts[7] was never set, so he should not have any rights
    assert.isFalse(await UserLog.isRole(0, accounts[7]))
    assert.isFalse(await UserLog.isRole(1, accounts[7]))
    assert.isFalse(await UserLog.isRole(2, accounts[7]))
  })

  it("should prevent owner from removing TopAdmin", async function () {

    // admin rights before 
    assert.isTrue(await UserLog.isRole(0, accounts[0]))
    assert.isTrue(await UserLog.isRole(1, accounts[0]))
    assert.isTrue(await UserLog.isRole(2, accounts[0]))

    await UserLog.setRoles(accounts[0], 0)

    // admin should still have the rights
    assert.isTrue(await UserLog.isRole(0, accounts[0]))
    assert.isTrue(await UserLog.isRole(1, accounts[0]))
    assert.isTrue(await UserLog.isRole(2, accounts[0]))
  })

  it("should change adminrights when changing ownership of Coo-contract", async function () {

    // admin rights before 
    assert.isTrue(await UserLog.isRole(0, accounts[0]))
    assert.isTrue(await UserLog.isRole(1, accounts[0]))
    assert.isTrue(await UserLog.isRole(2, accounts[0]))

    await coo.changeOwner(accounts[4])

    assert.isTrue(await UserLog.isRole(0, accounts[4]))
    assert.isTrue(await UserLog.isRole(1, accounts[4]))
    assert.isTrue(await UserLog.isRole(2, accounts[4]))

  })

  it("should change adminrights back whenchanging ownership of Coo-contract back", async function () {

    assert.isFalse(await UserLog.isRole(0, accounts[0]))
    assert.isFalse(await UserLog.isRole(1, accounts[0]))
    assert.isFalse(await UserLog.isRole(2, accounts[0]))

    await coo.changeOwner(accounts[0], { from: accounts[4] })

    assert.isTrue(await UserLog.isRole(0, accounts[0]))
    assert.isTrue(await UserLog.isRole(1, accounts[0]))
    assert.isTrue(await UserLog.isRole(2, accounts[0]))

    assert.isFalse(await UserLog.isRole(0, accounts[4]))
    assert.isFalse(await UserLog.isRole(1, accounts[4]))
    assert.isFalse(await UserLog.isRole(2, accounts[4]))
  })

  it("should allow userAdmin to register new users", async function () {
    //  let user = await UserLog.getFullUser(accounts[4])
    let user = await UserLog.getFullUser(accounts[4])
    assert.equal(user[0], '0x0000000000000000000000000000000000000000000000000000000000000000')
    assert.equal(user[1], '0x0000000000000000000000000000000000000000000000000000000000000000')
    assert.equal(user[2], '0x0000000000000000000000000000000000000000000000000000000000000000')
    assert.equal(user[3], '0x0000000000000000000000000000000000000000000000000000000000000000')
    assert.equal(user[4], '0x0000000000000000000000000000000000000000000000000000000000000000')
    assert.equal(user[5], '0x0000000000000000000000000000000000000000000000000000000000000000')
    assert.equal(user[6], '0x0000000000000000000000000000000000000000000000000000000000000000')
    assert.equal(user[7], '0x0000000000000000000000000000000000000000000000000000000000000000')
    assert.equal(user[8], '0x0000000000000000000000000000000000000000000000000000000000000000')
    assert.equal(user[9].toNumber(), 0)
    assert.isFalse(user[10])

    let tx = await UserLog.setUser(accounts[4],
      web3.fromAscii('John'),
      web3.fromAscii("Doe"),
      web3.fromAscii('testorganization'),
      web3.fromAscii('Main St'),
      web3.fromAscii('123'),
      web3.fromAscii('01234'),
      web3.fromAscii('Anytown'),
      web3.fromAscii('USA'),
      web3.fromAscii('AnyState'), { from: accounts[1] })

    user = await UserLog.getFullUser(accounts[4])
    assert.equal(web3.toAscii(user[0]).replace(/\0/g, ''), 'John', 'user[0] failed after')
    assert.equal(web3.toAscii(user[1]).replace(/\0/g, ''), 'Doe', 'user[1] failed after')
    assert.equal(web3.toAscii(user[2]).replace(/\0/g, ''), 'testorganization', 'user[2] failed after')
    assert.equal(web3.toAscii(user[3]).replace(/\0/g, ''), 'Main St', 'user[3] failed after')
    assert.equal(web3.toAscii(user[4]).replace(/\0/g, ''), '123', 'user[3] failed after')
    assert.equal(web3.toAscii(user[5]).replace(/\0/g, ''), '01234', 'user[5] failed after')
    assert.equal(web3.toAscii(user[6]).replace(/\0/g, ''), 'Anytown', 'user[6] failed after')
    assert.equal(web3.toAscii(user[7]).replace(/\0/g, ''), 'USA', 'user[7] failed after')
    assert.equal(web3.toAscii(user[8]).replace(/\0/g, ''), 'AnyState', 'user[8] failed after')
    assert.equal(user[9].toNumber(), 0)
    assert.isTrue(user[10])
  })


  it("should allow userAdmin to modify a user", async function () {
    let user = await UserLog.getFullUser(accounts[4])
    assert.equal(web3.toAscii(user[0]).replace(/\0/g, ''), 'John', 'user[0] failed after')
    assert.equal(web3.toAscii(user[1]).replace(/\0/g, ''), 'Doe', 'user[1] failed after')
    assert.equal(web3.toAscii(user[2]).replace(/\0/g, ''), 'testorganization', 'user[2] failed after')
    assert.equal(web3.toAscii(user[3]).replace(/\0/g, ''), 'Main St', 'user[3] failed after')
    assert.equal(web3.toAscii(user[4]).replace(/\0/g, ''), '123', 'user[3] failed after')
    assert.equal(web3.toAscii(user[5]).replace(/\0/g, ''), '01234', 'user[5] failed after')
    assert.equal(web3.toAscii(user[6]).replace(/\0/g, ''), 'Anytown', 'user[6] failed after')
    assert.equal(web3.toAscii(user[7]).replace(/\0/g, ''), 'USA', 'user[7] failed after')
    assert.equal(web3.toAscii(user[8]).replace(/\0/g, ''), 'AnyState', 'user[8] failed after')
    assert.equal(user[9].toNumber(), 0)
    assert.isTrue(user[10])

    let tx = await UserLog.setUser(accounts[4],
      web3.fromAscii('John2'),
      web3.fromAscii("Doe2"),
      web3.fromAscii('testorganization2'),
      web3.fromAscii('Main St2'),
      web3.fromAscii('1232'),
      web3.fromAscii('012342'),
      web3.fromAscii('Anytown2'),
      web3.fromAscii('USA2'),
      web3.fromAscii('AnyState2'), { from: accounts[1] })

    user = await UserLog.getFullUser(accounts[4])
    assert.equal(web3.toAscii(user[0]).replace(/\0/g, ''), 'John2', 'user[0] failed after')
    assert.equal(web3.toAscii(user[1]).replace(/\0/g, ''), 'Doe2', 'user[1] failed after')
    assert.equal(web3.toAscii(user[2]).replace(/\0/g, ''), 'testorganization2', 'user[2] failed after')
    assert.equal(web3.toAscii(user[3]).replace(/\0/g, ''), 'Main St2', 'user[3] failed after')
    assert.equal(web3.toAscii(user[4]).replace(/\0/g, ''), '1232', 'user[3] failed after')
    assert.equal(web3.toAscii(user[5]).replace(/\0/g, ''), '012342', 'user[5] failed after')
    assert.equal(web3.toAscii(user[6]).replace(/\0/g, ''), 'Anytown2', 'user[6] failed after')
    assert.equal(web3.toAscii(user[7]).replace(/\0/g, ''), 'USA2', 'user[7] failed after')
    assert.equal(web3.toAscii(user[8]).replace(/\0/g, ''), 'AnyState2', 'user[8] failed after')
    assert.equal(user[9].toNumber(), 0)
    assert.isTrue(user[10])

  })

  it("should allow userAdmin to deaciviate an account", async function () {

    let user = await UserLog.getFullUser(accounts[4])
    assert.equal(web3.toAscii(user[0]).replace(/\0/g, ''), 'John2', 'user[0] failed after')
    assert.equal(web3.toAscii(user[1]).replace(/\0/g, ''), 'Doe2', 'user[1] failed after')
    assert.equal(web3.toAscii(user[2]).replace(/\0/g, ''), 'testorganization2', 'user[2] failed after')
    assert.equal(web3.toAscii(user[3]).replace(/\0/g, ''), 'Main St2', 'user[3] failed after')
    assert.equal(web3.toAscii(user[4]).replace(/\0/g, ''), '1232', 'user[3] failed after')
    assert.equal(web3.toAscii(user[5]).replace(/\0/g, ''), '012342', 'user[5] failed after')
    assert.equal(web3.toAscii(user[6]).replace(/\0/g, ''), 'Anytown2', 'user[6] failed after')
    assert.equal(web3.toAscii(user[7]).replace(/\0/g, ''), 'USA2', 'user[7] failed after')
    assert.equal(web3.toAscii(user[8]).replace(/\0/g, ''), 'AnyState2', 'user[8] failed after')
    assert.equal(user[9].toNumber(), 0)
    assert.isTrue(user[10])

    await UserLog.deactivateUser(accounts[4])
    user = await UserLog.getFullUser(accounts[4])
    assert.equal(web3.toAscii(user[0]).replace(/\0/g, ''), 'John2', 'user[0] failed after')
    assert.equal(web3.toAscii(user[1]).replace(/\0/g, ''), 'Doe2', 'user[1] failed after')
    assert.equal(web3.toAscii(user[2]).replace(/\0/g, ''), 'testorganization2', 'user[2] failed after')
    assert.equal(web3.toAscii(user[3]).replace(/\0/g, ''), 'Main St2', 'user[3] failed after')
    assert.equal(web3.toAscii(user[4]).replace(/\0/g, ''), '1232', 'user[3] failed after')
    assert.equal(web3.toAscii(user[5]).replace(/\0/g, ''), '012342', 'user[5] failed after')
    assert.equal(web3.toAscii(user[6]).replace(/\0/g, ''), 'Anytown2', 'user[6] failed after')
    assert.equal(web3.toAscii(user[7]).replace(/\0/g, ''), 'USA2', 'user[7] failed after')
    assert.equal(web3.toAscii(user[8]).replace(/\0/g, ''), 'AnyState2', 'user[8] failed after')
    assert.equal(user[9].toNumber(), 0)
    assert.isFalse(user[10])

  })

  it("should not allow assetAdmin to register new users", async function () {
    let user = await UserLog.getFullUser(accounts[6])
    assert.equal(user[0], '0x0000000000000000000000000000000000000000000000000000000000000000')
    assert.equal(user[1], '0x0000000000000000000000000000000000000000000000000000000000000000')
    assert.equal(user[2], '0x0000000000000000000000000000000000000000000000000000000000000000')
    assert.equal(user[3], '0x0000000000000000000000000000000000000000000000000000000000000000')
    assert.equal(user[4], '0x0000000000000000000000000000000000000000000000000000000000000000')
    assert.equal(user[5], '0x0000000000000000000000000000000000000000000000000000000000000000')
    assert.equal(user[6], '0x0000000000000000000000000000000000000000000000000000000000000000')
    assert.equal(user[7], '0x0000000000000000000000000000000000000000000000000000000000000000')
    assert.equal(user[8], '0x0000000000000000000000000000000000000000000000000000000000000000')
    assert.equal(user[9].toNumber(), 0)
    assert.isFalse(user[10])

    let failed = false
    try {
      let tx = await UserLog.setUser(accounts[6],
        web3.fromAscii('John'),
        web3.fromAscii("Doe"),
        web3.fromAscii('testorganization'),
        web3.fromAscii('Main St'), 123,
        web3.fromAscii('01234'),
        web3.fromAscii('Anytown'),
        web3.fromAscii('USA'),
        web3.fromAscii('AnyState'), { from: accounts[2] })
      if (tx.receipt.status == '0x00') failed = true
    } catch (ex) {
      failed = true
    }
    assert.isTrue(failed)
    user = await UserLog.getFullUser(accounts[6])
    assert.equal(user[0], '0x0000000000000000000000000000000000000000000000000000000000000000')
    assert.equal(user[1], '0x0000000000000000000000000000000000000000000000000000000000000000')
    assert.equal(user[2], '0x0000000000000000000000000000000000000000000000000000000000000000')
    assert.equal(user[3], '0x0000000000000000000000000000000000000000000000000000000000000000')
    assert.equal(user[4], '0x0000000000000000000000000000000000000000000000000000000000000000')
    assert.equal(user[5], '0x0000000000000000000000000000000000000000000000000000000000000000')
    assert.equal(user[6], '0x0000000000000000000000000000000000000000000000000000000000000000')
    assert.equal(user[7], '0x0000000000000000000000000000000000000000000000000000000000000000')
    assert.equal(user[8], '0x0000000000000000000000000000000000000000000000000000000000000000')
    assert.equal(user[9].toNumber(), 0)
    assert.isFalse(user[10])
  })


  it("should not allow assetAdmin to deaciviate an account", async function () {

    let user = await UserLog.getFullUser(accounts[3])
    assert.equal(web3.toAscii(user[0]).replace(/\0/g, ''), 'John', 'user[0] failed after')
    assert.equal(web3.toAscii(user[1]).replace(/\0/g, ''), 'Doe', 'user[1] failed after')
    assert.equal(web3.toAscii(user[2]).replace(/\0/g, ''), 'Organization3', 'user[2] failed after')
    assert.equal(web3.toAscii(user[3]).replace(/\0/g, ''), 'Main St', 'user[3] failed after')
    assert.equal(web3.toAscii(user[4]).replace(/\0/g, ''), '123', 'user[3] failed after')
    assert.equal(web3.toAscii(user[5]).replace(/\0/g, ''), '01234', 'user[5] failed after')
    assert.equal(web3.toAscii(user[6]).replace(/\0/g, ''), 'Anytown', 'user[6] failed after')
    assert.equal(web3.toAscii(user[7]).replace(/\0/g, ''), 'USA', 'user[7] failed after')
    assert.equal(web3.toAscii(user[8]).replace(/\0/g, ''), 'AnyState', 'user[8] failed after')
    assert.equal(user[9].toNumber(), 0)
    assert.isTrue(user[10])

    let failed = false
    try {
      await UserLog.deactivateUser(accounts[3], { from: accounts[2] })

      if (tx.receipt.status == '0x00') failed = true
    } catch (ex) {
      failed = true
    }
    assert.isTrue(failed)

    assert.equal(web3.toAscii(user[0]).replace(/\0/g, ''), 'John', 'user[0] failed after')
    assert.equal(web3.toAscii(user[1]).replace(/\0/g, ''), 'Doe', 'user[1] failed after')
    assert.equal(web3.toAscii(user[2]).replace(/\0/g, ''), 'Organization3', 'user[2] failed after')
    assert.equal(web3.toAscii(user[3]).replace(/\0/g, ''), 'Main St', 'user[3] failed after')
    assert.equal(web3.toAscii(user[4]).replace(/\0/g, ''), '123', 'user[3] failed after')
    assert.equal(web3.toAscii(user[5]).replace(/\0/g, ''), '01234', 'user[5] failed after')
    assert.equal(web3.toAscii(user[6]).replace(/\0/g, ''), 'Anytown', 'user[6] failed after')
    assert.equal(web3.toAscii(user[7]).replace(/\0/g, ''), 'USA', 'user[7] failed after')
    assert.equal(web3.toAscii(user[8]).replace(/\0/g, ''), 'AnyState', 'user[8] failed after')
    assert.equal(user[9].toNumber(), 0)
    assert.isTrue(user[10])

  })

  it("should not allow users to create a new user", async function () {

    let user = await UserLog.getFullUser(accounts[7])
    assert.equal(user[0], '0x0000000000000000000000000000000000000000000000000000000000000000')
    assert.equal(user[1], '0x0000000000000000000000000000000000000000000000000000000000000000')
    assert.equal(user[2], '0x0000000000000000000000000000000000000000000000000000000000000000')
    assert.equal(user[3], '0x0000000000000000000000000000000000000000000000000000000000000000')
    assert.equal(user[4], '0x0000000000000000000000000000000000000000000000000000000000000000')
    assert.equal(user[5], '0x0000000000000000000000000000000000000000000000000000000000000000')
    assert.equal(user[6], '0x0000000000000000000000000000000000000000000000000000000000000000')
    assert.equal(user[7], '0x0000000000000000000000000000000000000000000000000000000000000000')
    assert.equal(user[8], '0x0000000000000000000000000000000000000000000000000000000000000000')
    assert.equal(user[9].toNumber(), 0)
    assert.isFalse(user[10])

    let failed = false
    try {
      let tx = await UserLog.setUser(accounts[7],
        web3.fromAscii('John'),
        web3.fromAscii("Doe"),
        web3.fromAscii('testorganization'),
        web3.fromAscii('Main St'),
        web3.fromAscii('123'),
        web3.fromAscii('01234'),
        web3.fromAscii('Anytown'),
        web3.fromAscii('USA'),
        web3.fromAscii('AnyState'), { from: accounts[6] })
      if (tx.receipt.status == '0x00') failed = true
    } catch (ex) {
      failed = true
    }
    assert.isTrue(failed)
    user = await UserLog.getFullUser(accounts[7])
    assert.equal(user[0], '0x0000000000000000000000000000000000000000000000000000000000000000')
    assert.equal(user[1], '0x0000000000000000000000000000000000000000000000000000000000000000')
    assert.equal(user[2], '0x0000000000000000000000000000000000000000000000000000000000000000')
    assert.equal(user[3], '0x0000000000000000000000000000000000000000000000000000000000000000')
    assert.equal(user[4], '0x0000000000000000000000000000000000000000000000000000000000000000')
    assert.equal(user[5], '0x0000000000000000000000000000000000000000000000000000000000000000')
    assert.equal(user[6], '0x0000000000000000000000000000000000000000000000000000000000000000')
    assert.equal(user[7], '0x0000000000000000000000000000000000000000000000000000000000000000')
    assert.equal(user[8], '0x0000000000000000000000000000000000000000000000000000000000000000')
    assert.equal(user[9].toNumber(), 0)
    assert.isFalse(user[10])
  })

  it("should not allow users to deaciviate an account", async function () {

    let user = await UserLog.getFullUser(accounts[3])
    assert.equal(web3.toAscii(user[0]).replace(/\0/g, ''), 'John', 'user[0] failed after')
    assert.equal(web3.toAscii(user[1]).replace(/\0/g, ''), 'Doe', 'user[1] failed after')
    assert.equal(web3.toAscii(user[2]).replace(/\0/g, ''), 'Organization3', 'user[2] failed after')
    assert.equal(web3.toAscii(user[3]).replace(/\0/g, ''), 'Main St', 'user[3] failed after')
    assert.equal(web3.toAscii(user[4]).replace(/\0/g, ''), '123', 'user[3] failed after')
    assert.equal(web3.toAscii(user[5]).replace(/\0/g, ''), '01234', 'user[5] failed after')
    assert.equal(web3.toAscii(user[6]).replace(/\0/g, ''), 'Anytown', 'user[6] failed after')
    assert.equal(web3.toAscii(user[7]).replace(/\0/g, ''), 'USA', 'user[7] failed after')
    assert.equal(web3.toAscii(user[8]).replace(/\0/g, ''), 'AnyState', 'user[8] failed after')
    assert.equal(user[9].toNumber(), 0)
    assert.isTrue(user[10])

    let failed = false
    try {
      await UserLog.deactivateUser(accounts[3], { from: accounts[6] })

      if (tx.receipt.status == '0x00') failed = true
    } catch (ex) {
      failed = true
    }
    assert.isTrue(failed)

    assert.equal(web3.toAscii(user[0]).replace(/\0/g, ''), 'John', 'user[0] failed after')
    assert.equal(web3.toAscii(user[1]).replace(/\0/g, ''), 'Doe', 'user[1] failed after')
    assert.equal(web3.toAscii(user[2]).replace(/\0/g, ''), 'Organization3', 'user[2] failed after')
    assert.equal(web3.toAscii(user[3]).replace(/\0/g, ''), 'Main St', 'user[3] failed after')
    assert.equal(web3.toAscii(user[4]).replace(/\0/g, ''), '123', 'user[3] failed after')
    assert.equal(web3.toAscii(user[5]).replace(/\0/g, ''), '01234', 'user[5] failed after')
    assert.equal(web3.toAscii(user[6]).replace(/\0/g, ''), 'Anytown', 'user[6] failed after')
    assert.equal(web3.toAscii(user[7]).replace(/\0/g, ''), 'USA', 'user[7] failed after')
    assert.equal(web3.toAscii(user[8]).replace(/\0/g, ''), 'AnyState', 'user[8] failed after')
    assert.equal(user[9].toNumber(), 0)
    assert.isTrue(user[10])

  })

  it("should not be able as assetAdmin to register new assets when the user has no AssetOwner-Role", async function () {
    try {
      tx = await AssetLog.registerAsset(accounts[9], accounts[3], 0, 1234567890, 100000, 1, 0, true, { from: accounts[2] })
      let rightsAfter = ((await UserLog.getRolesRights(accounts[3])).toNumber())
    } catch (ex) { }
    assert.isFalse(await UserLog.isRole(0, accounts[3]))
    assert.isFalse(await UserLog.isRole(1, accounts[3]))
    assert.isFalse(await UserLog.isRole(2, accounts[3]))
    assert.isFalse(await UserLog.isRole(3, accounts[3]))
    assert.isFalse(await UserLog.isRole(4, accounts[3]))


  })

  it("should be possible to add the assetOwner role to an user", async function () {

    await UserLog.setRoles(accounts[3], 16)

    assert.isFalse(await UserLog.isRole(0, accounts[3]))
    assert.isFalse(await UserLog.isRole(1, accounts[3]))
    assert.isFalse(await UserLog.isRole(2, accounts[3]))
    assert.isFalse(await UserLog.isRole(3, accounts[3]))
    assert.isTrue(await UserLog.isRole(4, accounts[3]))


  })

  it("should be able as assetAdmin to register new assets", async function () {

    await AssetLog.createAsset({ from: accounts[2] })
    await AssetLog.initGeneral(
      0,
      accounts[9],
      accounts[0],
      1234567890,
      true,
      { from: accounts[2] })

    await AssetLog.initProducingProperties(0,
      1,
      1000,
      1,
      web3.fromAscii("N.A."),
      web3.fromAscii("N.A."), { from: accounts[2] })

    await AssetLog.initLocation(
      0,
      web3.fromAscii("Germany"),
      web3.fromAscii("Saxony"),
      web3.fromAscii("123412"),
      web3.fromAscii("Mittweida"),
      web3.fromAscii("Markt"),
      web3.fromAscii("16a"),
      web3.fromAscii("0.1232423423"),
      web3.fromAscii("0.2342342445"),
      { from: accounts[2] }

    )


  })

  it("should be able as assetAdmin to update a smartmeter", async function () {
    let tx = await AssetLog.updateSmartMeter(0, '0x0000000000000000000000000000000000000002')
  })

  it("should be able as assetAdminto reitre an asset", async function () {
    let tx = await AssetLog.setActive(0, false, { from: accounts[2] })
    //   assert.equal(tx.receipt.status, '0x01')
  })

  it("should not allow userAdmin to register new assets", async function () {
    let failed = false
    try {
      let tx = await AssetLog.registerAsset('0x0000000000000000000000000000000000000001', accounts[3], 0, new Date().getMilliseconds(), 1000, 10000, 10, true, { from: accounts[1] })
      // 0x00 = transaction failed
      assert.equal(tx.receipt.status, '0x00')
      if (tx.receipt.status == '0x00') failed = true
    } catch (ex) {
      failed = true
    }
    assert.isTrue(failed)
  })

  it("should not allow userAdmiuns to update a smartmeter", async function () {
    //   let tx = await AssetLog.registerAsset('0x0000000000000000000000000000000000000001', accounts[3], 0, new Date().getMilliseconds(), 1000, 10000, 10, true, '0x0000000000000000000000000000000000000000000000000000000000000000', { from: accounts[2] })
    let failed = false
    try {
      let tx = await AssetLog.updateSmartMeter(0, '0x0000000000000000000000000000000000000002', { from: accounts[1] })
      if (tx.receipt.status == '0x00') failed = true
    } catch (ex) {
      failed = true
    }
    assert.isTrue(failed)
  })

  it("should not allow userAdmins to retire an asset", async function () {
    let failed = false
    try {
      let tx = await AssetLog.retireAsset(1, { from: accounts[1] })
      if (tx.receipt.status == '0x00') failed = true
    } catch (ex) {
      failed = true
    }
    assert.isTrue(failed)
  })

  it("should not allow users to register new assets", async function () {
    let failed = false
    try {
      let tx = await AssetLog.registerAsset('0x0000000000000000000000000000000000000001', accounts[3], 0, new Date().getMilliseconds(), 1000, 10000, 10, true, { from: accounts[4] })
      if (tx.receipt.status == '0x00') failed = true
    } catch (ex) {
      failed = true
    }
    assert.isTrue(failed)
  })

  it("should not allow users to retire an asset", async function () {
    let failed = false
    try {
      let tx = await AssetLog.retireAsset(1, { from: accounts[4] })
      if (tx.receipt.status == '0x00') failed = true
    } catch (ex) {
      failed = true
    }
    assert.isTrue(failed)
  })

  it("should not allow users to update a smartmeter", async function () {
    let failed = false
    try {
      let tx = await AssetLog.updateSmartMeter(1, '0x0000000000000000000000000000000000000002', { from: accounts[4] })
      if (tx.receipt.status == '0x00') failed = true

    } catch (ex) {
      failed = true
    }
    assert.isTrue(failed)
  })


  it("should not be possible to access a non existing role", async function () {

    let failed = false
    try {
      await UserLog.isRole(99, accounts[3])

    } catch (e) {
      failed = true
    }
    assert.isTrue(failed)

  })


  it.skip("revoking a certificate", async function () { })



})