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
var UserDB = artifacts.require("UserDB");

contract('UserDB', function (accounts) {

  var UserLog,
    UserDb;

  it("should get the instances", async function () {
    UserLog = await UserLogic.deployed();
    UserDb = await UserDB.deployed();

    assert.isNotNull(UserLog)
    assert.isNotNull(UserDb)
  })

  it("should be owned by the logic-contract", async function () {
    assert.notEqual(UserLogic, '0x0000000000000000000000000000000000000000')
    assert.equal(await UserDb.owner.call(), UserLogic.address)
  })

  it("should not create a user", async function () {
    let failed = false
    try {
      let tx = await UserDb.setUser(accounts[4],
        web3.fromAscii('John'),
        web3.fromAscii("Doe"),
        web3.fromAscii('testorganization'),
        web3.fromAscii('Main St'), 123,
        web3.fromAscii('01234'),
        web3.fromAscii('Anytown'),
        web3.fromAscii('USA'),
        web3.fromAscii('AnyState'))
      if (tx.receipt.status == '0x00') failed = true

    } catch (ex) {
      failed = true
    }
    assert.isTrue(failed)

  })

  it("should not be able to give a role to a given user", async function () {

    let failed = false
    try {
      let tx = await UserDb.setRoles(accounts[5], 7)
      if (tx.receipt.status == '0x00') failed = true
    } catch (ex) {
      failed = true
    }
    assert.isTrue(failed)

  })

  it("should not be possible to call the setUseraActive function", async function () {
    let failed = false
    try {
      let tx = await UserDb.setUseraActive(accounts[3], false)
      if (tx.receipt.status == '0x00') failed = true
    } catch (ex) {
      failed = true
    }
    assert.isTrue(failed)
  })

  it("should not be possible to call the setUseraActive function", async function () {
    let failed = false
    try {
      let tx = await UserDb.setUseraActive(accounts[3], false)
      if (tx.receipt.status == '0x00') failed = true
    } catch (ex) {
      failed = true
    }
    assert.isTrue(failed)
  })

  it("should not be possile to change the username", async function () {
    let failed = false
    try {
      let tx = await UserDb.setUserName(accounts[3], web3.fromAscii('John2'), web3.fromAscii('Doe2'))
      if (tx.receipt.status == '0x00') failed = true

    } catch (ex) {
      failed = true
    }
    assert.isTrue(failed)
  })

  it("should not be possile to change the organization", async function () {
    let failed = false
    try {
      let x = await UserDb.setOrganization(accounts[3], web3.fromAscii('testorganization2'))
      if (tx.receipt.status == '0x00') failed = true

    } catch (ex) {
      failed = true
    }
    assert.isTrue(failed)
  })

  it("should not be possile to change the address", async function () {
    let failed = false
    try {
      let tx = await UserDb.setAddress(accounts[3], web3.fromAscii('Main St 2'), 1, web3.fromAscii('0123456'), web3.fromAscii('AnyCity2'), web3.fromAscii('USA2'), web3.fromAscii('AnyState'))
      if (tx.receipt.status == '0x00') failed = true
    } catch (ex) {
      failed = true
    }
    assert.isTrue(failed)
  })
})