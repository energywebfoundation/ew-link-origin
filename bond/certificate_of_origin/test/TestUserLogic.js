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
var CoO = artifacts.require("CoO");


contract('UserLogic', function (accounts) {

  var UserLog,
    UserDb;


  it("should get the instances", async function () {
    UserLog = await UserLogic.deployed();
    UserDb = await UserDB.deployed();
    coo = await CoO.deployed()

    assert.isNotNull(UserLog)
    assert.isNotNull(UserDb)
    assert.isNotNull(coo)
  })

  it("should initialized correctly", async function () {
    assert.equal(await UserLog.db.call(), UserDB.address)
  })

  it("should return true for already defined user ", async function () {
    assert.isTrue(await UserLog.doesUserExist(accounts[3]))
  })

  it("should return false for nonexisting user ", async function () {
    assert.isFalse(await UserLog.doesUserExist(accounts[4]))
  })
  /*
    it("should have 1 address in the accountList already", async function () {
      assert.equal(await UserDb.getAddressArrayLength(), 1)
    })
    */

  it("should only be possible to call init be call once", async function () {

    let failed = false
    try {
      let tx = await UserLog.init('0x0000000000000000000000000000000000000001')
      if (tx.receipt.status == '0x00') failed = true
    } catch (ex) {
      failed = true
    }
    assert.isTrue(failed)
    assert.equal(await UserLog.db.call(), UserDB.address)
  })

  it("should return a full User correctly", async function () {
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
  })

  it("should set a user correctly", async function () {

    let userBefore = await UserLog.getFullUser(accounts[4])

    await UserLog.setUser(accounts[4],
      web3.fromAscii('John'),
      web3.fromAscii("Doe"),
      web3.fromAscii('testorganization'),
      web3.fromAscii('Main St'),
      web3.fromAscii('123'),
      web3.fromAscii('01234'),
      web3.fromAscii('Anytown'),
      web3.fromAscii('USA'),
      web3.fromAscii('AnyState'))
    let userAfter = await UserLog.getFullUser(accounts[4])

    assert.equal(web3.toAscii(userBefore[0]).replace(/\0/g, ''), '', 'user[0] failed after')
    assert.equal(web3.toAscii(userBefore[1]).replace(/\0/g, ''), '', 'user[1] failed after')
    assert.equal(web3.toAscii(userBefore[2]).replace(/\0/g, ''), '', 'user[2] failed after')
    assert.equal(web3.toAscii(userBefore[3]).replace(/\0/g, ''), '', 'user[3] failed after')
    assert.equal(web3.toAscii(userBefore[4]).replace(/\0/g, ''), '', 'user[3] failed after')
    assert.equal(web3.toAscii(userBefore[5]).replace(/\0/g, ''), '', 'user[5] failed after')
    assert.equal(web3.toAscii(userBefore[6]).replace(/\0/g, ''), '', 'user[6] failed after')
    assert.equal(web3.toAscii(userBefore[7]).replace(/\0/g, ''), '', 'user[7] failed after')
    assert.equal(web3.toAscii(userBefore[8]).replace(/\0/g, ''), '', 'user[8] failed after')
    assert.equal(userBefore[9].toNumber(), 0)
    assert.isFalse(userBefore[10])


    assert.equal(web3.toAscii(userAfter[0]).replace(/\0/g, ''), 'John', 'user[0] failed after')
    assert.equal(web3.toAscii(userAfter[1]).replace(/\0/g, ''), 'Doe', 'user[1] failed after')
    assert.equal(web3.toAscii(userAfter[2]).replace(/\0/g, ''), 'testorganization', 'user[2] failed after')
    assert.equal(web3.toAscii(userAfter[3]).replace(/\0/g, ''), 'Main St', 'user[3] failed after')
    assert.equal(web3.toAscii(userAfter[4]).replace(/\0/g, ''), '123', 'user[3] failed after')
    assert.equal(web3.toAscii(userAfter[5]).replace(/\0/g, ''), '01234', 'user[5] failed after')
    assert.equal(web3.toAscii(userAfter[6]).replace(/\0/g, ''), 'Anytown', 'user[6] failed after')
    assert.equal(web3.toAscii(userAfter[7]).replace(/\0/g, ''), 'USA', 'user[7] failed after')
    assert.equal(web3.toAscii(userAfter[8]).replace(/\0/g, ''), 'AnyState', 'user[8] failed after')
    assert.equal(userAfter[9].toNumber(), 0)
    assert.isTrue(userAfter[10])
  })

  /*
  it("should have 2 addresses in the accountList", async function () {
    assert.equal(await UserDb.getAddressArrayLength(), 2)
  })
  */

  it("should be able to fully modify a user", async function () {
    let userBefore = await UserLog.getFullUser(accounts[4])

    await UserLog.setUser(accounts[4],
      web3.fromAscii('John2'),
      web3.fromAscii("Doe2"),
      web3.fromAscii('testorganization2'),
      web3.fromAscii('Main St2'),
      web3.fromAscii('1232'),
      web3.fromAscii('012342'),
      web3.fromAscii('Anytown2'),
      web3.fromAscii('USA2'),
      web3.fromAscii('AnyState2'))
    let userAfter = await UserLog.getFullUser(accounts[4])

    assert.equal(web3.toAscii(userBefore[0]).replace(/\0/g, ''), 'John', 'user[0] failed after')
    assert.equal(web3.toAscii(userBefore[1]).replace(/\0/g, ''), 'Doe', 'user[1] failed after')
    assert.equal(web3.toAscii(userBefore[2]).replace(/\0/g, ''), 'testorganization', 'user[2] failed after')
    assert.equal(web3.toAscii(userBefore[3]).replace(/\0/g, ''), 'Main St', 'user[3] failed after')
    assert.equal(web3.toAscii(userBefore[4]).replace(/\0/g, ''), '123', 'user[3] failed after')
    assert.equal(web3.toAscii(userBefore[5]).replace(/\0/g, ''), '01234', 'user[5] failed after')
    assert.equal(web3.toAscii(userBefore[6]).replace(/\0/g, ''), 'Anytown', 'user[6] failed after')
    assert.equal(web3.toAscii(userBefore[7]).replace(/\0/g, ''), 'USA', 'user[7] failed after')
    assert.equal(web3.toAscii(userBefore[8]).replace(/\0/g, ''), 'AnyState', 'user[8] failed after')
    assert.equal(userBefore[9].toNumber(), 0)
    assert.isTrue(userBefore[10])

    assert.equal(web3.toAscii(userAfter[0]).replace(/\0/g, ''), 'John2', 'user[0] failed after')
    assert.equal(web3.toAscii(userAfter[1]).replace(/\0/g, ''), 'Doe2', 'user[1] failed after')
    assert.equal(web3.toAscii(userAfter[2]).replace(/\0/g, ''), 'testorganization2', 'user[2] failed after')
    assert.equal(web3.toAscii(userAfter[3]).replace(/\0/g, ''), 'Main St2', 'user[3] failed after')
    assert.equal(web3.toAscii(userAfter[4]).replace(/\0/g, ''), '1232', 'user[3] failed after')
    assert.equal(web3.toAscii(userAfter[5]).replace(/\0/g, ''), '012342', 'user[5] failed after')
    assert.equal(web3.toAscii(userAfter[6]).replace(/\0/g, ''), 'Anytown2', 'user[6] failed after')
    assert.equal(web3.toAscii(userAfter[7]).replace(/\0/g, ''), 'USA2', 'user[7] failed after')
    assert.equal(web3.toAscii(userAfter[8]).replace(/\0/g, ''), 'AnyState2', 'user[8] failed after')
    assert.equal(userAfter[9].toNumber(), 0)
    assert.isTrue(userAfter[10])

  })

  it("should prevent changing the firstname to an empty value when calling specific set-Method", async function () {
    let userBefore = await UserLog.getFullUser(accounts[3])
    try {
      await UserLog.setUserName(accounts[3], web3.fromAscii(''), web3.fromAscii('Doe2'))
    } catch (ex) { }
    let userAfter = await UserLog.getFullUser(accounts[3])
    assert.deepEqual(userBefore, userAfter)
  })

  it("should prevent changing the surname to an empty value when calling specific set-Method", async function () {
    let userBefore = await UserLog.getFullUser(accounts[3])
    try {
      await UserLog.setUserName(accounts[3], web3.fromAscii('John'), web3.fromAscii(''))
    } catch (ex) { }
    let userAfter = await UserLog.getFullUser(accounts[3])
    assert.deepEqual(userBefore, userAfter)
  })

  it("should prevent changing the organization to an empty value when calling specific set-Method", async function () {
    let userBefore = await UserLog.getFullUser(accounts[3])
    try {
      await UserLog.setOrganization(accounts[3], web3.fromAscii(''))
    } catch (ex) { }
    let userAfter = await UserLog.getFullUser(accounts[3])
    assert.deepEqual(userBefore, userAfter)

  })

  it("should prevent changing the street to an empty value when calling specific set-Method", async function () {
    let userBefore = await UserLog.getFullUser(accounts[3])
    try {
      await UserLog.setOrganizationAddress(accounts[3],
        (''), 1232,
        web3.fromAscii('012342'),
        web3.fromAscii('Anytown2'),
        web3.fromAscii('USA2'),
        web3.fromAscii('AnyState2'))
    } catch (ex) { }
    let userAfter = await UserLog.getFullUser(accounts[3])
    assert.deepEqual(userBefore, userAfter)

  })


  it("should prevent changing the housenumber to 0 when calling specific set-Method", async function () {
    let userBefore = await UserLog.getFullUser(accounts[3])
    try {
      await UserLog.setOrganizationAddress(accounts[3],
        web3.fromAscii('Main St'), 0,
        web3.fromAscii('012342'),
        web3.fromAscii('Anytown2'),
        web3.fromAscii('USA2'),
        web3.fromAscii('AnyState2'))
    } catch (ex) { }
    let userAfter = await UserLog.getFullUser(accounts[3])
    assert.deepEqual(userBefore, userAfter)

  })

  it("should prevent changing the zip-code to 0 when calling specific set-Method", async function () {
    let userBefore = await UserLog.getFullUser(accounts[3])
    try {
      await UserLog.setOrganizationAddress(accounts[3],
        web3.fromAscii('Main St'), 123,
        (''),
        web3.fromAscii('Anytown2'),
        web3.fromAscii('USA2'),
        web3.fromAscii('AnyState2'))
    } catch (ex) { }
    let userAfter = await UserLog.getFullUser(accounts[3])
    assert.deepEqual(userBefore, userAfter)

  })


  it("should prevent changing the city to an empty value when calling specific set-Method", async function () {
    let userBefore = await UserLog.getFullUser(accounts[3])
    try {
      await UserLog.setOrganizationAddress(accounts[3],
        web3.fromAscii('Main St'), 123,
        web3.fromAscii('01234'),
        (''),
        web3.fromAscii('USA2'),
        web3.fromAscii('AnyState2'))
    } catch (ex) { }
    let userAfter = await UserLog.getFullUser(accounts[3])
    assert.deepEqual(userBefore, userAfter)

  })

  it("should prevent changing the country to an empty value when calling specific set-Method", async function () {
    let userBefore = await UserLog.getFullUser(accounts[3])
    try {
      await UserLog.setOrganizationAddress(accounts[3],
        web3.fromAscii('Main St'), 123,
        web3.fromAscii('01234'),
        web3.fromAscii('Anytown'),
        (''),
        web3.fromAscii('AnyState2'))
    } catch (ex) { }
    let userAfter = await UserLog.getFullUser(accounts[3])
    assert.deepEqual(userBefore, userAfter)

  })

  it("should prevent changing the first name to an empty value when calling the full set-Method", async function () {
    let userBefore = await UserLog.getFullUser(accounts[3])
    try {

      await UserLog.setUser(accounts[4],
        web3.fromAscii(''),
        web3.fromAscii("Doe2"),
        web3.fromAscii('testorganization2'),
        web3.fromAscii('Main St2'), 1232,
        web3.fromAscii('012342'),
        web3.fromAscii('Anytown2'),
        web3.fromAscii('USA2'),
        web3.fromAscii('AnyState2'))
    } catch (ex) { }
    let userAfter = await UserLog.getFullUser(accounts[3])
    assert.deepEqual(userBefore, userAfter)

  })

  it("should prevent changing the surname to an empty value when calling the full set-Method", async function () {
    let userBefore = await UserLog.getFullUser(accounts[3])
    try {

      await UserLog.setUser(accounts[4],
        web3.fromAscii('John2'),
        web3.fromAscii(''),
        web3.fromAscii('testorganization2'),
        web3.fromAscii('Main St2'), 1232,
        web3.fromAscii('012342'),
        web3.fromAscii('Anytown2'),
        web3.fromAscii('USA2'),
        web3.fromAscii('AnyState2'))
    } catch (ex) { }
    let userAfter = await UserLog.getFullUser(accounts[3])
    assert.deepEqual(userBefore, userAfter)

  })

  it("should prevent changing the organization to an empty value when calling the full set-Method", async function () {
    let userBefore = await UserLog.getFullUser(accounts[3])
    try {

      await UserLog.setUser(accounts[4],
        web3.fromAscii('John2'),
        web3.fromAscii('Doe2'),
        web3.fromAscii(''),
        web3.fromAscii('Main St2'), 1232,
        web3.fromAscii('012342'),
        web3.fromAscii('Anytown2'),
        web3.fromAscii('USA2'),
        web3.fromAscii('AnyState2'))
    } catch (ex) { }
    let userAfter = await UserLog.getFullUser(accounts[3])
    assert.deepEqual(userBefore, userAfter)

  })

  it("should prevent changing the street name to an empty value when calling the full set-Method", async function () {
    let userBefore = await UserLog.getFullUser(accounts[3])
    try {

      await UserLog.setUser(accounts[4],
        web3.fromAscii('John'),
        web3.fromAscii("Doe2"),
        web3.fromAscii('testorganization2'),
        web3.fromAscii(''), 1232,
        web3.fromAscii('012342'),
        web3.fromAscii('Anytown2'),
        web3.fromAscii('USA2'),
        web3.fromAscii('AnyState2'))
    } catch (ex) { }
    let userAfter = await UserLog.getFullUser(accounts[3])
    assert.deepEqual(userBefore, userAfter)

  })

  it("should prevent changing the housenumber to 0 when calling the full set-Method", async function () {
    let userBefore = await UserLog.getFullUser(accounts[3])
    try {

      await UserLog.setUser(accounts[4],
        web3.fromAscii('John2'),
        web3.fromAscii("Doe2"),
        web3.fromAscii('testorganization2'),
        web3.fromAscii('Main St2'), 0,
        web3.fromAscii('012342'),
        web3.fromAscii('Anytown2'),
        web3.fromAscii('USA2'),
        web3.fromAscii('AnyState2'))
    } catch (ex) { }
    let userAfter = await UserLog.getFullUser(accounts[3])
    assert.deepEqual(userBefore, userAfter)

  })

  it("should prevent changing the zip-code to an empty value when calling the full set-Method", async function () {
    let userBefore = await UserLog.getFullUser(accounts[3])
    try {

      await UserLog.setUser(accounts[4],
        web3.fromAscii('John2'),
        web3.fromAscii("Doe2"),
        web3.fromAscii('testorganization2'),
        web3.fromAscii('Main St2'), 1232,
        web3.fromAscii(''),
        web3.fromAscii('Anytown2'),
        web3.fromAscii('USA2'),
        web3.fromAscii('AnyState2'))
    } catch (ex) { }
    let userAfter = await UserLog.getFullUser(accounts[3])
    assert.deepEqual(userBefore, userAfter)

  })

  it("should prevent changing the cityname to an empty value when calling the full set-Method", async function () {
    let userBefore = await UserLog.getFullUser(accounts[3])
    try {

      await UserLog.setUser(accounts[4],
        web3.fromAscii(''),
        web3.fromAscii("Doe2"),
        web3.fromAscii('testorganization2'),
        web3.fromAscii('Main St2'), 1232,
        web3.fromAscii('012342'),
        web3.fromAscii(''),
        web3.fromAscii('USA2'),
        web3.fromAscii('AnyState2'))
    } catch (ex) { }
    let userAfter = await UserLog.getFullUser(accounts[3])
    assert.deepEqual(userBefore, userAfter)

  })

  it("should prevent changing the country to an empty value when calling the full set-Method", async function () {
    let userBefore = await UserLog.getFullUser(accounts[3])
    try {

      await UserLog.setUser(accounts[4],
        web3.fromAscii(''),
        web3.fromAscii("Doe2"),
        web3.fromAscii('testorganization2'),
        web3.fromAscii('Main St2'), 1232,
        web3.fromAscii('012342'),
        web3.fromAscii('Anytown2'),
        web3.fromAscii(''),
        web3.fromAscii('AnyState2'))
    } catch (ex) { }
    let userAfter = await UserLog.getFullUser(accounts[3])
    assert.deepEqual(userBefore, userAfter)

  })

  it("should change the username correctly", async function () {
    let userBefore = await UserLog.getFullUser(accounts[3])

    await UserLog.setUserName(accounts[3], web3.fromAscii('John2'), web3.fromAscii('Doe2'))

    let userAfter = await UserLog.getFullUser(accounts[3])

    assert.equal(web3.toAscii(userBefore[0]).replace(/\0/g, ''), 'John', 'user[0] failed after')
    assert.equal(web3.toAscii(userBefore[1]).replace(/\0/g, ''), 'Doe', 'user[1] failed after')
    assert.equal(web3.toAscii(userBefore[2]).replace(/\0/g, ''), 'Organization3', 'user[2] failed after')
    assert.equal(web3.toAscii(userBefore[3]).replace(/\0/g, ''), 'Main St', 'user[3] failed after')
    assert.equal(web3.toAscii(userBefore[4]).replace(/\0/g, ''), '123', 'user[3] failed after')
    assert.equal(web3.toAscii(userBefore[5]).replace(/\0/g, ''), '01234', 'user[5] failed after')
    assert.equal(web3.toAscii(userBefore[6]).replace(/\0/g, ''), 'Anytown', 'user[6] failed after')
    assert.equal(web3.toAscii(userBefore[7]).replace(/\0/g, ''), 'USA', 'user[7] failed after')
    assert.equal(web3.toAscii(userBefore[8]).replace(/\0/g, ''), 'AnyState', 'user[8] failed after')
    assert.equal(userBefore[9].toNumber(), 0)
    assert.isTrue(userBefore[10])

    assert.equal(web3.toAscii(userAfter[0]).replace(/\0/g, ''), 'John2', 'user[0] failed after')
    assert.equal(web3.toAscii(userAfter[1]).replace(/\0/g, ''), 'Doe2', 'user[1] failed after')
    assert.equal(web3.toAscii(userAfter[2]).replace(/\0/g, ''), 'Organization3', 'user[2] failed after')
    assert.equal(web3.toAscii(userAfter[3]).replace(/\0/g, ''), 'Main St', 'user[3] failed after')
    assert.equal(web3.toAscii(userAfter[4]).replace(/\0/g, ''), '123', 'user[3] failed after')
    assert.equal(web3.toAscii(userAfter[5]).replace(/\0/g, ''), '01234', 'user[5] failed after')
    assert.equal(web3.toAscii(userAfter[6]).replace(/\0/g, ''), 'Anytown', 'user[6] failed after')
    assert.equal(web3.toAscii(userAfter[7]).replace(/\0/g, ''), 'USA', 'user[7] failed after')
    assert.equal(web3.toAscii(userAfter[8]).replace(/\0/g, ''), 'AnyState', 'user[8] failed after')
    assert.equal(userAfter[9].toNumber(), 0)
    assert.isTrue(userAfter[10])
  })

  it("should not change the username of a non existing user", async function () {
    let user = await UserLog.getFullUser(accounts[6])
    try {
      await UserLog.setUserName(accounts[6], web3.fromAscii('John2'), web3.fromAscii('Doe2'))
    }
    catch (ex) { }
    assert.deepEqual(user, await UserLog.getFullUser(accounts[6]))
  })

  it("should change an organization-name correctly", async function () {

    let orgBefore = await UserLog.getFullUser(accounts[3])
    await UserLog.setOrganization(accounts[3], web3.fromAscii('testorganization2'))
    let orgAfter = await UserLog.getFullUser(accounts[3])

    assert.equal(web3.toAscii(orgBefore[0]).replace(/\0/g, ''), 'John2', 'user[0] failed after')
    assert.equal(web3.toAscii(orgBefore[1]).replace(/\0/g, ''), 'Doe2', 'user[1] failed after')
    assert.equal(web3.toAscii(orgBefore[2]).replace(/\0/g, ''), 'Organization3', 'user[2] failed after')
    assert.equal(web3.toAscii(orgBefore[3]).replace(/\0/g, ''), 'Main St', 'user[3] failed after')
    assert.equal(web3.toAscii(orgBefore[4]).replace(/\0/g, ''), '123', 'user[3] failed after')
    assert.equal(web3.toAscii(orgBefore[5]).replace(/\0/g, ''), '01234', 'user[5] failed after')
    assert.equal(web3.toAscii(orgBefore[6]).replace(/\0/g, ''), 'Anytown', 'user[6] failed after')
    assert.equal(web3.toAscii(orgBefore[7]).replace(/\0/g, ''), 'USA', 'user[7] failed after')
    assert.equal(web3.toAscii(orgBefore[8]).replace(/\0/g, ''), 'AnyState', 'user[8] failed after')
    assert.equal(orgBefore[9].toNumber(), 0)
    assert.isTrue(orgBefore[10])

    assert.equal(web3.toAscii(orgAfter[0]).replace(/\0/g, ''), 'John2', 'user[0] failed after')
    assert.equal(web3.toAscii(orgAfter[1]).replace(/\0/g, ''), 'Doe2', 'user[1] failed after')
    assert.equal(web3.toAscii(orgAfter[2]).replace(/\0/g, ''), 'testorganization2', 'user[2] failed after')
    assert.equal(web3.toAscii(orgAfter[3]).replace(/\0/g, ''), 'Main St', 'user[3] failed after')
    assert.equal(web3.toAscii(orgAfter[4]).replace(/\0/g, ''), '123', 'user[3] failed after')
    assert.equal(web3.toAscii(orgAfter[5]).replace(/\0/g, ''), '01234', 'user[5] failed after')
    assert.equal(web3.toAscii(orgAfter[6]).replace(/\0/g, ''), 'Anytown', 'user[6] failed after')
    assert.equal(web3.toAscii(orgAfter[7]).replace(/\0/g, ''), 'USA', 'user[7] failed after')
    assert.equal(web3.toAscii(orgAfter[8]).replace(/\0/g, ''), 'AnyState', 'user[8] failed after')
    assert.equal(orgAfter[9].toNumber(), 0)
    assert.isTrue(orgAfter[10])
  })

  it("should not change a non exstiting organization-name", async function () {
    let orgNameBefore = await UserLog.getFullUser(accounts[6])
    try {
      await UserLog.setOrganization(accounts[6], web3.fromAscii('testorganization2'))
    } catch (ex) { }
    assert.deepEqual(orgNameBefore, await UserLog.getFullUser(accounts[6]))
  })

  it("should change an organization-address correctly", async function () {

    let orgBefore = await UserLog.getFullUser(accounts[3])


    await UserLog.setOrganizationAddress(accounts[3],
      web3.fromAscii('Main St2'),
      web3.fromAscii('1232'),
      web3.fromAscii('012342'),
      web3.fromAscii('Anytown2'),
      web3.fromAscii('USA2'),
      web3.fromAscii('AnyState2'))

    let orgAfter = await UserLog.getFullUser(accounts[3])

    assert.equal(web3.toAscii(orgBefore[0]).replace(/\0/g, ''), 'John2', 'user[0] failed after')
    assert.equal(web3.toAscii(orgBefore[1]).replace(/\0/g, ''), 'Doe2', 'user[1] failed after')
    assert.equal(web3.toAscii(orgBefore[2]).replace(/\0/g, ''), 'testorganization2', 'user[2] failed after')
    assert.equal(web3.toAscii(orgBefore[3]).replace(/\0/g, ''), 'Main St', 'user[3] failed after')
    assert.equal(web3.toAscii(orgBefore[4]).replace(/\0/g, ''), '123', 'user[3] failed after')
    assert.equal(web3.toAscii(orgBefore[5]).replace(/\0/g, ''), '01234', 'user[5] failed after')
    assert.equal(web3.toAscii(orgBefore[6]).replace(/\0/g, ''), 'Anytown', 'user[6] failed after')
    assert.equal(web3.toAscii(orgBefore[7]).replace(/\0/g, ''), 'USA', 'user[7] failed after')
    assert.equal(web3.toAscii(orgBefore[8]).replace(/\0/g, ''), 'AnyState', 'user[8] failed after')
    assert.equal(orgBefore[9].toNumber(), 0)
    assert.isTrue(orgBefore[10])

    assert.equal(web3.toAscii(orgAfter[0]).replace(/\0/g, ''), 'John2', 'user[0] failed after')
    assert.equal(web3.toAscii(orgAfter[1]).replace(/\0/g, ''), 'Doe2', 'user[1] failed after')
    assert.equal(web3.toAscii(orgAfter[2]).replace(/\0/g, ''), 'testorganization2', 'user[2] failed after')
    assert.equal(web3.toAscii(orgAfter[3]).replace(/\0/g, ''), 'Main St2', 'user[3] failed after')
    assert.equal(web3.toAscii(orgAfter[4]).replace(/\0/g, ''), '1232', 'user[3] failed after')
    assert.equal(web3.toAscii(orgAfter[5]).replace(/\0/g, ''), '012342', 'user[5] failed after')
    assert.equal(web3.toAscii(orgAfter[6]).replace(/\0/g, ''), 'Anytown2', 'user[6] failed after')
    assert.equal(web3.toAscii(orgAfter[7]).replace(/\0/g, ''), 'USA2', 'user[7] failed after')
    assert.equal(web3.toAscii(orgAfter[8]).replace(/\0/g, ''), 'AnyState2', 'user[8] failed after')
    assert.equal(orgAfter[9].toNumber(), 0)
    assert.isTrue(orgAfter[10])
  })

  it("should not change a non existing organization-address", async function () {
    let org = await UserLog.getFullUser(accounts[6])

    try {
      await UserLog.setOrganizationAddress(accounts[6],
        web3.fromAscii('Main St2'), 1232,
        web3.fromAscii('012342'),
        web3.fromAscii('Anytown2'),
        web3.fromAscii('USA2'),
        web3.fromAscii('AnyState2'))
    }
    catch (ex) {

    }
    assert.deepEqual(await UserLog.getFullUser(accounts[6]), org)
  })

  it("should be able to deactivate an user", async function () {
    assert.isTrue(await UserLog.doesUserExist(accounts[4]))
    await UserLog.deactivateUser(accounts[4])
    assert.isFalse(await UserLog.doesUserExist(accounts[4]))
  })


  /*
  it("should still have only 2 accounts", async function () {
    assert.equal(await UserDb.getAddressArrayLength(), 2)
  })
  */

  it("should not set a role for a non existing user", async function () {
    let roleBefore = await UserLog.getRolesRights(accounts[6])

    try {
      await UserLog.setRoles(accounts[6], 7)
    } catch (ex) { }
    let roleAfter = await UserLog.getRolesRights(accounts[6])

    assert.deepEqual(roleAfter, roleBefore)
  })

  it("should set a role for an existing user", async function () {
    let roleBefore = await UserLog.getRolesRights(accounts[3])
    await UserLog.setRoles(accounts[3], 7)
    let roleAfter = await UserLog.getRolesRights(accounts[3])

    assert.equal(roleBefore, 0)
    assert.equal(roleAfter, 7)
  })

  it("should not be possible to deactivate an userAdmin-account", async function () {
    let userExistsBefore = await UserLog.doesUserExist(accounts[1])
    try {
      await UserLog.deactivateUser(accounts[1])
    } catch (ex) {

    }
    let userExistsAfter = await UserLog.doesUserExist(accounts[1])

    assert.isTrue(userExistsBefore)
    assert.isTrue(userExistsAfter)
  })

  it("should not be possible to deactivate an assetAdmin-account", async function () {
    let userExistsBefore = await UserLog.doesUserExist(accounts[2])
    try {
      await UserLog.deactivateUser(accounts[2])
    } catch (ex) {

    }
    let userExistsAfter = await UserLog.doesUserExist(accounts[2])

    assert.isTrue(userExistsBefore)
    assert.isTrue(userExistsAfter)
  })


  it("should not be possible to deactivate an AgreementAdmin-account", async function () {
    let userExistsBefore = await UserLog.doesUserExist(accounts[9])
    try {
      await UserLog.deactivateUser(accounts[9])
    } catch (ex) {

    }
    let userExistsAfter = await UserLog.doesUserExist(accounts[9])

    assert.isTrue(userExistsBefore)
    assert.isTrue(userExistsAfter)
  })

  it("should be possible to add as TopAdmin", async function () {

    let rightsBefore = (await UserLog.getRolesRights(accounts[5])).toNumber()
    //  console.log(await UserLog.getFullUser(accounts[5]))
    await UserLog.addAdminRole(accounts[5], 0)

    let rightsAfter = (await UserLog.getRolesRights(accounts[5])).toNumber()

    assert.equal(rightsBefore, 0)
    assert.equal(rightsAfter, 1)
  })

  it("should not be possible to remove AdminRole", async function () {

    let rightsBefore = (await UserLog.getRolesRights(accounts[5])).toNumber()
    //  console.log(await UserLog.getFullUser(accounts[5]))
    try {
      await UserLog.removeAdminRole(accounts[5], 0, { from: accounts[9] })
    } catch (ex) {

    }
    let rightsAfter = (await UserLog.getRolesRights(accounts[5])).toNumber()

    assert.equal(rightsBefore, 1)
    assert.equal(rightsAfter, 1)
  })

  it("should be possible to remove AdminRole", async function () {

    let rightsBefore = (await UserLog.getRolesRights(accounts[5])).toNumber()
    //  console.log(await UserLog.getFullUser(accounts[5]))
    await UserLog.removeAdminRole(accounts[5], 0)

    let rightsAfter = (await UserLog.getRolesRights(accounts[5])).toNumber()

    assert.equal(rightsBefore, 1)
    assert.equal(rightsAfter, 0)
  })

  it("should be possible to remove AdminRole without the user beeing a an Admin", async function () {

    let rightsBefore = (await UserLog.getRolesRights(accounts[5])).toNumber()
    //  console.log(await UserLog.getFullUser(accounts[5]))
    await UserLog.removeAdminRole(accounts[5], 0)

    let rightsAfter = (await UserLog.getRolesRights(accounts[5])).toNumber()

    assert.equal(rightsBefore, 0)
    assert.equal(rightsAfter, 0)
  })


  it("should be possible to add as AssetManager", async function () {

    let rightsBefore = (await UserLog.getRolesRights(accounts[5])).toNumber()
    //  console.log(await UserLog.getFullUser(accounts[5]))
    await UserLog.addAssetManagerRole(accounts[5])

    let rightsAfter = (await UserLog.getRolesRights(accounts[5])).toNumber()

    assert.equal(rightsBefore, 0)
    assert.equal(rightsAfter, 16)
  })

  it("should  be possible to remove AssetManagerRole  ", async function () {

    let rightsBefore = (await UserLog.getRolesRights(accounts[5])).toNumber()
    //  console.log(await UserLog.getFullUser(accounts[5]))

    await UserLog.removeAssetManagerRole(accounts[5], { from: accounts[0] })

    let rightsAfter = (await UserLog.getRolesRights(accounts[5])).toNumber()

    assert.equal(rightsBefore, 16)
    assert.equal(rightsAfter, 0)
  })

  it("should  be possible to remove a non existing AssetManagerRole ", async function () {

    let rightsBefore = (await UserLog.getRolesRights(accounts[5])).toNumber()
    //  console.log(await UserLog.getFullUser(accounts[5]))

    await UserLog.removeAssetManagerRole(accounts[5], { from: accounts[0] })

    let rightsAfter = (await UserLog.getRolesRights(accounts[5])).toNumber()

    assert.equal(rightsBefore, 0)
    assert.equal(rightsAfter, 0)
  })

  it("should be possible to add as Trader", async function () {

    let rightsBefore = (await UserLog.getRolesRights(accounts[5])).toNumber()
    //  console.log(await UserLog.getFullUser(accounts[5]))
    await UserLog.addTraderRole(accounts[5])

    let rightsAfter = (await UserLog.getRolesRights(accounts[5])).toNumber()

    assert.equal(rightsBefore, 0)
    assert.equal(rightsAfter, 32)
  })

  it("should  be possible to remove AssetManagerRole  ", async function () {

    let rightsBefore = (await UserLog.getRolesRights(accounts[5])).toNumber()
    //  console.log(await UserLog.getFullUser(accounts[5]))

    await UserLog.removeTraderRole(accounts[5], { from: accounts[0] })

    let rightsAfter = (await UserLog.getRolesRights(accounts[5])).toNumber()

    assert.equal(rightsBefore, 32)
    assert.equal(rightsAfter, 0)
  })

  it("should  be possible to remove a non existing AssetManagerRole ", async function () {

    let rightsBefore = (await UserLog.getRolesRights(accounts[5])).toNumber()
    //  console.log(await UserLog.getFullUser(accounts[5]))

    await UserLog.removeTraderRole(accounts[5], { from: accounts[0] })

    let rightsAfter = (await UserLog.getRolesRights(accounts[5])).toNumber()

    assert.equal(rightsBefore, 0)
    assert.equal(rightsAfter, 0)
  })




})