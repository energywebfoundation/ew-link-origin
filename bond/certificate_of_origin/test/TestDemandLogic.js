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

var DemandLogic = artifacts.require("DemandLogic");
var CoO = artifacts.require("CoO");

var DemandDB = artifacts.require("DemandDB")

var AssetProducingRegistryLogic = artifacts.require("AssetProducingRegistryLogic");
var CertificateLogic = artifacts.require("CertificateLogic");

var ConsumingLogic = artifacts.require("AssetConsumingRegistryLogic");

var UserLogic = artifacts.require("UserLogic");


contract('DemandLogic', function (accounts) {

    var demandLogic, demandDb, assetLogic, certificateLogic, startTime, endTime, agreementDate, userLogic, consumingLogic

    it("should get the instances", async function () {
        demandLogic = await DemandLogic.deployed();
        coo = await CoO.deployed()
        demandDb = await DemandDB.deployed()
        assetLogic = await AssetProducingRegistryLogic.deployed()
        certificateLogic = await CertificateLogic.deployed()
        userLogic = await UserLogic.deployed()
        consumingLogic = await ConsumingLogic.deployed();


        assert.isNotNull(demandLogic)
        assert.isNotNull(coo)
    })

    it("should create a new Asset for testing", async function () {
        await assetLogic.createAsset()
        await assetLogic.initGeneral(
            0,
            accounts[9],
            accounts[0],
            1234567890,
            true,
            { from: accounts[2] })
        await assetLogic.initProducingProperties(0,
            0,
            50000,
            0,
            web3.fromAscii("N.A."),
            web3.fromAscii("N.A."))

        await assetLogic.initLocation(
            0,
            web3.fromAscii("Germany"),
            web3.fromAscii("Saxony"),
            web3.fromAscii("123412"),
            web3.fromAscii("Mittweida"),
            web3.fromAscii("Markt"),
            web3.fromAscii("16"),
            web3.fromAscii("0.1232423423"),
            web3.fromAscii("0.2342342445")
        )
    })

    it("should have 0 elements in the actvieDemands-List", async function () {
        assert.equal((await demandLogic.getActiveDemandListLength()).toNumber(), 0)
    })

    it("should have 0 elements in the allDemands-List", async function () {
        assert.equal((await demandLogic.getAllDemandListLength()).toNumber(), 0)
    })

    it("should create an empty demand", async function () {
        await demandLogic.createDemand([false, false, false, false, false, false, false, false, false, false])
    })

    it("should have 1 elements in the allDemands-List", async function () {
        assert.equal((await demandLogic.getAllDemandListLength()).toNumber(), 1)
    })

    it("should throw an error when trying to create a demand with a non existing producing asset", async function () {

        agreementDate = (await web3.eth.getBlock('latest')).timestamp
        startTime = agreementDate - 120
        endTime = agreementDate + 1200
        let failed = false
        try {
            await demandLogic.initGeneralAndCoupling(
                0,
                0,// accounts[4],
                accounts[3],
                startTime,
                endTime,
                0,
                0,
                0,
                false,
                2,
                -1
            )
        }
        catch (ex) {
            failed = true
        }

        assert.isTrue(failed)
    })


    it("should create a new GeneralDemand", async function () {

        await demandLogic.initGeneralAndCoupling(
            0,
            0,// accounts[4],
            accounts[3],
            startTime,
            endTime,
            0,
            0,
            0,
            0,
            0
        )
    })

    it("should return the generalDemand correctly", async function () {
        let demand = await demandLogic.getDemandGeneral(0)

        assert.equal(demand[0], '0x0000000000000000000000000000000000000000')
        assert.equal(demand[1], accounts[3])
        assert.equal(demand[2].toNumber(), startTime)
        assert.equal(demand[3].toNumber(), endTime)
        assert.equal(demand[4], 0)
        assert.equal(demand[5], 0)
        assert.equal(demand[6], 0)
        assert.equal(demand[7], 0)

    })

    it("should show the correct existing status", async function () {
        let demand = await demandLogic.getExistStatus(0)

        assert.isTrue(demand[0])
        assert.isFalse(demand[1])
        assert.isFalse(demand[2])
    })

    it("should return the couplinh correctly", async function () {
        let demand = await demandLogic.getDemandCoupling(0)

        assert.equal(demand[0].toNumber(), 0)
        assert.equal(demand[1].toNumber(), 0)
    })

    it("should have 0 elements in the actvieDemands-List", async function () {
        assert.equal((await demandLogic.getActiveDemandListLength()).toNumber(), 0)
    })

    it("should have 0 elements in the allDemands-List", async function () {
        assert.equal((await demandLogic.getAllDemandListLength()).toNumber(), 1)
    })

    it("should create a new priceDriving ", async function () {
        await demandLogic.initPriceDriving(0,
            web3.fromAscii("Germany"),
            web3.fromAscii("Saxony"),
            0,
            10,
            0,
            web3.fromAscii("N.A"),
            web3.fromAscii("N.A")
        )
    })

    it("should return the priceDriving correctly", async function () {
        let demand = await demandLogic.getDemandPriceDriving(0)

        assert.equal(web3.toAscii(demand[0]).replace(/\0/g, ''), 'Germany')
        assert.equal(web3.toAscii(demand[1]).replace(/\0/g, ''), 'Saxony')
        assert.equal(demand[2].toNumber(), 0)
        assert.equal(demand[3].toNumber(), 10)
        assert.equal(demand[4].toNumber(), 0)
        assert.equal(web3.toAscii(demand[5]).replace(/\0/g, ''), 'N.A')
        assert.equal(web3.toAscii(demand[6]).replace(/\0/g, ''), 'N.A')
    })


    it("should show the correct existing status", async function () {
        let demand = await demandLogic.getExistStatus(0)

        assert.isTrue(demand[0])
        assert.isTrue(demand[1])
        assert.isFalse(demand[2])
    })

    it("should have 0 elements in the actvieDemands-List", async function () {
        assert.equal((await demandLogic.getActiveDemandListLength()).toNumber(), 0)
    })

    it("should have 0 elements in the allDemands-List", async function () {
        assert.equal((await demandLogic.getAllDemandListLength()).toNumber(), 1)
    })

    it("should create a new matcherProperty ", async function () {
        await demandLogic.initMatchProperties(
            0,
            10000,
            0,
            accounts[8]
        )
    })

    it("should return the matcherProperty correctly", async function () {
        let demand = await demandLogic.getDemandMatcherProperties(0)

        assert.equal(demand[0].toNumber(), 10000)
        assert.equal(demand[1].toNumber(), 0)
        assert.equal(demand[2].toNumber(), 0)
        assert.equal(demand[3].toNumber(), 0)
        assert.equal(demand[4], accounts[8])
    })

    it("should show the correct existing status", async function () {
        let demand = await demandLogic.getExistStatus(0)

        assert.isTrue(demand[0])
        assert.isTrue(demand[1])
        assert.isTrue(demand[2])
    })

    it("should have 1 elements in the actvieDemands-List", async function () {
        assert.equal((await demandLogic.getActiveDemandListLength()).toNumber(), 1)
    })

    it("should have 1 elements in the allDemands-List", async function () {
        assert.equal((await demandLogic.getAllDemandListLength()).toNumber(), 1)
    })


    it("should add the buyer as trader ", async function () {
        userLogic.addTraderRole(accounts[3])
    })

    it("should add the buyer as trader ", async function () {
        userLogic.addTraderRole(accounts[9])
        userLogic.addAssetManagerRole(accounts[9])
        userLogic.addTraderRole(accounts[0])

    })

    it("should produce 100000 watt ", async function () {
        await assetLogic.saveSmartMeterRead(0, 100000, false, web3.fromAscii('newFileHash'), 10000, false, { from: accounts[9] })
    })

    it("should return false when using wrong the matcher ", async function () {
        let checkResult = await demandLogic.checkMatcher(0, 100)
        assert.equal(checkResult[0], 0)
        assert.equal(checkResult[1], 0)
        assert.equal(checkResult[2], 0)
        assert.isFalse(checkResult[3])
    })

    it("should return false when sending claiming too much energy", async function () {
        let checkResult = await demandLogic.checkMatcher(0, 10000000)
        assert.equal(checkResult[0], 0)
        assert.equal(checkResult[1], 0)
        assert.equal(checkResult[2], 0)
        assert.isFalse(checkResult[3])
    })

    it("should return true with matching inputs", async function () {
        let checkResult = await demandLogic.checkMatcher(0, 10000, { from: accounts[8] })
        assert.equal(checkResult[0], 10000)
        assert.equal(checkResult[1], 1)
        assert.equal(checkResult[2], 0)
        assert.isTrue(checkResult[3])

    })

    it("should have 0 certificates in the list", async function () {
        let cert = await certificateLogic.getCertificateListLength()

        assert.equal(cert.toNumber(), 0)
    })

    it("should be possible to fullfill a demand", async function () {

        let lengthBefore = await certificateLogic.getCertificateListLength()

        let matchPropBefore = await demandLogic.getDemandMatcherProperties(0)
        let tx = await demandLogic.matchDemand(0, 10000, 0, { from: accounts[8] })
        let matchPropAfter = await demandLogic.getDemandMatcherProperties(0)

        let lengthAfter = await certificateLogic.getCertificateListLength()

        assert.equal(lengthBefore.toNumber(), 0)
        assert.equal(lengthAfter.toNumber(), 1)

        assert.equal(matchPropBefore[0].toNumber(), 10000)
        assert.equal(matchPropAfter[0].toNumber(), 10000)

        assert.equal(matchPropBefore[1].toNumber(), 0)
        assert.equal(matchPropAfter[1].toNumber(), 10000)

        assert.equal(matchPropBefore[2].toNumber(), 0)
        assert.equal(matchPropAfter[2].toNumber(), 1)

        assert.equal(matchPropBefore[3].toNumber(), 0)
        assert.equal(matchPropAfter[3].toNumber(), 0)

    })

    it("should get the right amount of  Co2 Used for certificate", async function () {
        assert.equal((await assetLogic.getCo2UsedForCertificate(0)).toNumber(), 1000)
    })

    it("should have 1 certificates in the list", async function () {
        let cert = await certificateLogic.getCertificateListLength()

        assert.equal(cert.toNumber(), 1)
    })

    it("should have created certificate correctly", async function () {
        let cert = await certificateLogic.getCertificate(0)

        assert.equal(cert[0].toNumber(), 0)
        assert.equal(cert[1], accounts[3])
        assert.equal(cert[2].toNumber(), 10000)
        assert.isFalse(cert[3])
        assert.equal(web3.toAscii(cert[4]).replace(/\0/g, ''), 'newFileHash')
        assert.equal(cert[5].toNumber(), 1000)


    })

    it("should not be possible to fullfill a demand again", async function () {

        let failed = false
        try {
            let tx = await demandLogic.matchDemand(0, 10000, 0, 0, { from: accounts[8] })
            if (tx.receipt.status == '0x00') failed = true

        } catch (ex) {
            failed = true
        }

        assert.isTrue(failed)
    })

    it("should create a 2nd demand", async function () {
        await demandLogic.createDemand([false, true, false, true, true, false, false, false, false, false])
        await demandLogic.initGeneralAndCoupling(
            1,
            0,// accounts[4],
            accounts[3],
            startTime,
            endTime,
            0,
            00,
            0,
            0,
            0
        )
        await demandLogic.initPriceDriving(1,
            web3.fromAscii("Germany"),
            web3.fromAscii("Saxony"),
            0,
            0,
            0,
            web3.fromAscii("N.A."),
            web3.fromAscii("N.A.")
        )
        await demandLogic.initMatchProperties(1,
            10000,
            0,
            accounts[8]
        )
    })


    it("should have 2 elements in the actvieDemands-List", async function () {
        assert.equal((await demandLogic.getActiveDemandListLength()).toNumber(), 2)
    })

    it("should have 2 elements in the allDemands-List", async function () {
        assert.equal((await demandLogic.getActiveDemandListLength()).toNumber(), 2)
    })

    it("should return the right active-Demands", async function () {
        assert.equal((await demandLogic.getActiveDemandIdAt(0)).toNumber(), 0)
        assert.equal((await demandLogic.getActiveDemandIdAt(1)).toNumber(), 1)

    })



    it("should be possible to nearly fullfill 2nd demand", async function () {


        let lengthBefore = await certificateLogic.getCertificateListLength()

        let matchPropBefore = await demandLogic.getDemandMatcherProperties(1)
        let tx = await demandLogic.matchDemand(1, 8000, 0, { from: accounts[8] })
        let matchPropAfter = await demandLogic.getDemandMatcherProperties(1)

        let lengthAfter = await certificateLogic.getCertificateListLength()

        assert.equal(lengthBefore.toNumber(), 1)
        assert.equal(lengthAfter.toNumber(), 2)

        assert.equal(matchPropBefore[0].toNumber(), 10000)
        assert.equal(matchPropAfter[0].toNumber(), 10000)

        assert.equal(matchPropBefore[1].toNumber(), 0)
        assert.equal(matchPropAfter[1].toNumber(), 8000)

        assert.equal(matchPropBefore[2].toNumber(), 0)
        assert.equal(matchPropAfter[2].toNumber(), 1)

        assert.equal(matchPropBefore[3].toNumber(), 0)
        assert.equal(matchPropAfter[3].toNumber(), 0)



    })

    it("should have 1 certificates in the list", async function () {
        let cert = await certificateLogic.getCertificateListLength()

        assert.equal(cert.toNumber(), 2)
    })

    it("should have created certificate correctly", async function () {
        let cert = await certificateLogic.getCertificate(1)

        assert.equal(cert[0].toNumber(), 0)
        assert.equal(cert[1], accounts[3])
        assert.equal(cert[2].toNumber(), 8000)
        assert.isFalse(cert[3])
        assert.equal(web3.toAscii(cert[4]).replace(/\0/g, ''), 'newFileHash')
        assert.closeTo(cert[5].toNumber(), 800, 1)


    })

    it("should be possible to completly fullfill 2nd demand", async function () {

        let lengthBefore = await certificateLogic.getCertificateListLength()

        let matchPropBefore = await demandLogic.getDemandMatcherProperties(1)
        let tx = await demandLogic.matchDemand(1, 2000, 0, { from: accounts[8] })
        let matchPropAfter = await demandLogic.getDemandMatcherProperties(1)

        let lengthAfter = await certificateLogic.getCertificateListLength()

        assert.equal(lengthBefore.toNumber(), 2)
        assert.equal(lengthAfter.toNumber(), 3)

        assert.equal(matchPropBefore[0].toNumber(), 10000)
        assert.equal(matchPropAfter[0].toNumber(), 10000)

        assert.equal(matchPropBefore[1].toNumber(), 8000)
        assert.equal(matchPropAfter[1].toNumber(), 10000)

        assert.equal(matchPropBefore[2].toNumber(), 1)
        assert.equal(matchPropAfter[2].toNumber(), 2)

        assert.equal(matchPropBefore[3].toNumber(), 0)
        assert.equal(matchPropAfter[3].toNumber(), 0)

    })

    it("should have 3 certificates in the list", async function () {
        let cert = await certificateLogic.getCertificateListLength()

        assert.equal(cert.toNumber(), 3)
    })

    it("should have created certificate correctly", async function () {
        let cert = await certificateLogic.getCertificate(2)

        assert.equal(cert[0].toNumber(), 0)
        assert.equal(cert[1], accounts[3])
        assert.equal(cert[2].toNumber(), 2000)
        assert.isFalse(cert[3])
        assert.equal(web3.toAscii(cert[4]).replace(/\0/g, ''), 'newFileHash')
        assert.equal(cert[5].toNumber(), 200)


    })

    it("should not be possible to remove active demands when their endtime is not yet finished", async function () {

        let activeDemandsBefore = (await demandLogic.getActiveDemandListLength()).toNumber()
        try {
            await demandLogic.removeActiveDemand(0)
        }
        catch (ex) {

        }
        let actvieDemandsAfter = (await demandLogic.getActiveDemandListLength()).toNumber()

        assert.equal(activeDemandsBefore, actvieDemandsAfter)
    })

    it("should  be possible to remove active demands when their endtime is passed", async function () {

        await web3.currentProvider.send(
            {
                jsonrpc: '2.0',
                method: 'evm_increaseTime',
                params: [1500],
                id: 0
            })


        let activeDemandsBefore = (await demandLogic.getActiveDemandListLength()).toNumber()

        await demandLogic.removeActiveDemand(0)

        let actvieDemandsAfter = (await demandLogic.getActiveDemandListLength()).toNumber()

        assert.equal(activeDemandsBefore, 2)
        assert.equal(actvieDemandsAfter, 1)

    })

    it("should return the right active-Demand after removing the 1st one", async function () {
        assert.equal((await demandLogic.getActiveDemandIdAt(0)).toNumber(), 1)

    })

    it("should create a 3rd demand", async function () {
        await demandLogic.createDemand([false, true, true, true, true, true, true, false, false, false])
        await demandLogic.initGeneralAndCoupling(
            2,
            0,
            accounts[3],
            startTime,
            endTime,
            0,
            1,
            0,
            0,
            0
        )
        await demandLogic.initPriceDriving(2,
            web3.fromAscii("Germany"),
            web3.fromAscii("Berlin"),
            0,
            10,
            0,
            web3.fromAscii("N.A."),
            web3.fromAscii("N.A."))
        await demandLogic.initMatchProperties(2,
            10000,
            0,
            accounts[8]
        )
    })

    it("should create a 4th demand", async function () {
        await demandLogic.createDemand([false, false, true, true, true, false, true, false, false, false])
        await demandLogic.initGeneralAndCoupling(
            3,
            accounts[3],
            accounts[3],
            startTime,
            endTime,
            0,
            1,
            0,
            0,
            0
        )
        await demandLogic.initPriceDriving(
            3,
            web3.fromAscii("Germany"),
            web3.fromAscii("Berlin"),
            0,
            10,
            1,
            web3.fromAscii("N.A."),
            web3.fromAscii("N.A."))
        let tx = await demandLogic.initMatchProperties(3,
            10000,
            0,
            accounts[8]
        )
    })

    it("should create a new Assets for testing", async function () {
        await assetLogic.createAsset()
        /* await assetLogic.initGeneral(1,
             accounts[9],
             accounts[0],
             1,
             0,
             1234567890,
             100000,
             true,
             { from: accounts[2] }
         )*/

        await assetLogic.initGeneral(
            1,
            accounts[9],
            accounts[0],
            1234567890,
            true,
            { from: accounts[2] })
        await assetLogic.initProducingProperties(1,
            1,
            50000,
            0,
            web3.fromAscii("N.A."),
            web3.fromAscii("N.A."))

        await assetLogic.initLocation(
            1,
            web3.fromAscii("Germany"),
            web3.fromAscii("Saxony"),
            web3.fromAscii("123412"),
            web3.fromAscii("Mittweida"),
            web3.fromAscii("Markt"),
            web3.fromAscii("16"),
            web3.fromAscii("0.1232423423"),
            web3.fromAscii("0.2342342445")
        )

        await assetLogic.createAsset()
        await assetLogic.initGeneral(
            2,
            accounts[9],
            accounts[0],
            1234567890,
            true,
            { from: accounts[2] })
        await assetLogic.initProducingProperties(2,
            0,
            50000,
            0,
            web3.fromAscii("N.A."),
            web3.fromAscii("N.A."))

        await assetLogic.initLocation(
            2,
            web3.fromAscii("Germany"),
            web3.fromAscii("Berlin"),
            web3.fromAscii("123412"),
            web3.fromAscii("Mittweida"),
            web3.fromAscii("Markt"),
            web3.fromAscii("16"),
            web3.fromAscii("0.1232423423"),
            web3.fromAscii("0.2342342445")
        )

        await assetLogic.createAsset()
        await assetLogic.initGeneral(
            3,
            accounts[9],
            accounts[0],
            1234567890,
            true,
            { from: accounts[2] })
        await assetLogic.initProducingProperties(3,
            0,
            50000,
            1,
            web3.fromAscii("N.A."),
            web3.fromAscii("N.A."))

        await assetLogic.initLocation(
            3,
            web3.fromAscii("USA"),
            web3.fromAscii("California"),
            web3.fromAscii("123412"),
            web3.fromAscii("Mittweida"),
            web3.fromAscii("Markt"),
            web3.fromAscii("16"),
            web3.fromAscii("0.1232423423"),
            web3.fromAscii("0.2342342445")
        )

        await assetLogic.createAsset()
        await assetLogic.initGeneral(
            4,
            accounts[9],
            accounts[0],
            1234567890,
            true,
            { from: accounts[2] })
        await assetLogic.initProducingProperties(4,
            2,
            50000,
            2,
            web3.fromAscii("N.A."),
            web3.fromAscii("N.A."))
        await assetLogic.initLocation(
            4,
            web3.fromAscii("Germany"),
            web3.fromAscii("Berlin"),
            web3.fromAscii("123412"),
            web3.fromAscii("Mittweida"),
            web3.fromAscii("Markt"),
            web3.fromAscii("16"),
            web3.fromAscii("0.1232423423"),
            web3.fromAscii("0.2342342445")
        )


    })


    it("should return false when using the wrong assetId", async function () {
        let demand = await demandLogic.checkDemandGeneral(2, 0)

        assert.equal(demand[0], '0x0000000000000000000000000000000000000000')
        assert.isFalse(demand[1])

    })


    it("should return false when the assetType is not matching", async function () {
        let demand = await demandLogic.checkPriceDriving(2, 1, 100, 0)
        //   console.log(demand)
        assert.isFalse(demand[0])

    })

    it("should return false when the country is not matching", async function () {
        let demand = await demandLogic.checkPriceDriving(2, 3, 100, 0)
        //   console.log(demand)
        assert.isFalse(demand[0])

    })

    it("should return false when the region is not matching", async function () {
        let demand = await demandLogic.checkPriceDriving(1, 2, 100, 0)
        assert.isFalse(demand[0])

    })

    it("should return false when the compliance is not matching", async function () {
        let demand = await demandLogic.checkPriceDriving(3, 4, 10, 0)
        assert.isFalse(demand[0])

    })

    it("should return false when the no energy is given", async function () {
        let demand = await demandLogic.checkPriceDriving(3, 4, 0, 0)
        assert.isFalse(demand[0])

    })

    it("should initiaie a 5th demand with coupling", async function () {
        await demandLogic.createDemand([false, false, false, true, true, false, true, true, false, false])

        await demandLogic.initPriceDriving(4,
            web3.fromAscii("Germany"),
            web3.fromAscii("Berlin"),
            0,
            10,
            0,
            web3.fromAscii("N.A."),
            web3.fromAscii("N.A."))

        await demandLogic.initMatchProperties(4,
            10000,
            0,
            accounts[8]
        )
    })

    it("should throw an error when trying to create a demand with a non existing consuming asset", async function () {

        agreementDate = (await web3.eth.getBlock('latest')).timestamp
        startTime = agreementDate - 120
        endTime = agreementDate + 1200
        let failed = false
        try {
            await demandLogic.initGeneralAndCoupling(
                4,
                0,// accounts[4],
                accounts[3],
                startTime,
                endTime,
                0,
                0,
                0,
                0,
                0
            )
        }
        catch (ex) {
            failed = true
        }

        assert.isTrue(failed)
    })

    it("should create an consuming asset", async function () {
        let tx = await consumingLogic.createAsset()

        await consumingLogic.initGeneral(0,
            accounts[9], accounts[0],
            1234567890,
            1000,
            false, true)
        await consumingLogic.initLocation(
            0,
            web3.fromAscii("Germany"),
            web3.fromAscii("Saxony"),
            web3.fromAscii("123412"),
            web3.fromAscii("Mittweida"),
            web3.fromAscii("Markt"),
            web3.fromAscii("16a"),
            web3.fromAscii("0.1232423423"),
            web3.fromAscii("0.2342342445")
        )

    })

    it("should be possible to create coupled demand now", async function () {
        await demandLogic.initGeneralAndCoupling(
            4,
            0,// accounts[4],
            accounts[3],
            startTime,
            endTime,
            0,
            0,
            0,
            0,
            0
        )

    })
    /*
        it("should return false when trying to couple right wrong consumingAsset", async function () {
            let demand = await demandLogic.checkDemandGeneral(4, 0)
            assert.isFalse(demand[1])
     
        })
    */
    it("should return false when trying to couple wrong producingAsset", async function () {
        // let demandMask = (await demandDb.getDemandMask(4)).toNumber()
        let demand = await demandLogic.checkDemandCoupling(4, 1, 0)
        assert.isFalse(demand[0])

    })

    it("should return true when trying to couple right consumingAsset", async function () {
        let demand = await demandLogic.checkDemandCoupling(4, 0, 0)
        assert.isTrue(demand[0])

    })

    it("should return false the originator is wrong", async function () {

        let demand = await demandLogic.checkDemandGeneral(3, 0)
        assert.isFalse(demand[1])

    })

    it("should return false when matching too much energy ", async function () {
        let checkResult = await demandLogic.checkMatcher(4, 100000, { from: accounts[8] })
        assert.isFalse(checkResult[3])
    })

    it("should create a monthly demand", async function () {
        await demandLogic.createDemand([false, false, false, false, false, false, false, false, false, false])
        await demandLogic.initGeneralAndCoupling(
            5,
            0,
            accounts[3],
            startTime,
            endTime,
            1,
            1,
            0,
            0,
            0
        )
        await demandLogic.initPriceDriving(
            5,
            web3.fromAscii("Germany"),
            web3.fromAscii("Berlin"),
            0,
            10,
            1,
            web3.fromAscii("N.A."),
            web3.fromAscii("N.A."))

        let tx = await demandLogic.initMatchProperties(5,
            10000,
            0,
            accounts[8]
        )
    })


    it("should create a daily demand", async function () {
        await demandLogic.createDemand([false, false, false, false, false, false, false, false, false, false])
        await demandLogic.initGeneralAndCoupling(
            6,
            0,
            accounts[3],
            startTime,
            endTime,
            2,
            1,
            0,
            0,
            0
        )
        await demandLogic.initPriceDriving(
            6,
            web3.fromAscii("Germany"),
            web3.fromAscii("Berlin"),
            0,
            10,
            1,
            web3.fromAscii("N.A."),
            web3.fromAscii("N.A."))


        let tx = await demandLogic.initMatchProperties(6,
            10000,
            0,
            accounts[8]
        )
    })

    it("should create an hourly demand", async function () {
        await demandLogic.createDemand([false, false, false, false, false, false, false, false, false, false])
        await demandLogic.initGeneralAndCoupling(
            7,
            0,
            accounts[3],
            startTime,
            endTime,
            3,
            1,
            0,
            0,
            0
        )
        await demandLogic.initPriceDriving(
            7,
            web3.fromAscii("Germany"),
            web3.fromAscii("Berlin"),
            0,
            10,
            1,
            web3.fromAscii("N.A."),
            web3.fromAscii("N.A."))
        let tx = await demandLogic.initMatchProperties(7,
            10000,
            0,
            accounts[8]
        )
    })

    it("should increase blocktime by 1 year", async function () {

        await web3.currentProvider.send(
            {
                jsonrpc: '2.0',
                method: 'evm_increaseTime',
                params: [86400 * 365],
                id: 0
            })
        await web3.currentProvider.send(
            {
                jsonrpc: '2.0',
                method: 'evm_mine',
                params: [],
                id: 0
            })
    })

    it("should return the right yearly period", async function () {


        assert.equal((await demandLogic.getCurrentPeriod(4)).toNumber(), 1)

    })


    it("should return the right monthly period", async function () {

        assert.equal((await demandLogic.getCurrentPeriod(5)).toNumber(), 12)

    })


    it("should return the right daily period", async function () {

        assert.equal((await demandLogic.getCurrentPeriod(6)).toNumber(), 365)

    })


    it("should return the right hourly period", async function () {

        assert.equal((await demandLogic.getCurrentPeriod(7)).toNumber(), 365 * 24)

    })


    it("should return false when matching too much energy ", async function () {
        let checkResult = await demandLogic.checkMatcher(4, 100000, { from: accounts[8] })
        assert.isFalse(checkResult[3])
    })

    it("should return true when matchingis right in later period ", async function () {
        let checkResult = await demandLogic.checkMatcher(4, 100, { from: accounts[8] })
        assert.equal(checkResult[0].toNumber(), 100)
        assert.equal(checkResult[1].toNumber(), 1)
        assert.equal(checkResult[2].toNumber(), 1)
        assert.isTrue(checkResult[3])
    })

    it("Testcase matchcertificate", async function () {

        agreementDate = (await web3.eth.getBlock('latest')).timestamp
        startTime = agreementDate - 120
        endTime = agreementDate + 1200

        await assetLogic.createAsset()
        await assetLogic.initGeneral(
            5,
            accounts[9],
            accounts[0],
            1234567890,
            true,
            { from: accounts[2] })
        await assetLogic.initProducingProperties(5,
            0,
            50000,
            0,
            web3.fromAscii("N.A."),
            web3.fromAscii("N.A."))
        await assetLogic.initLocation(
            5,
            web3.fromAscii("Germany"),
            web3.fromAscii("Berlin"),
            web3.fromAscii("123412"),
            web3.fromAscii("Mittweida"),
            web3.fromAscii("Markt"),
            web3.fromAscii("16"),
            web3.fromAscii("0.1232423423"),
            web3.fromAscii("0.2342342445")
        )

        await assetLogic.saveSmartMeterRead(5, 100000, false, web3.fromAscii('newFileHash'), 7, false, { from: accounts[9] })

        await demandLogic.createDemand([false, true, true, true, true, false, false, false, false, false])
        await demandLogic.initGeneralAndCoupling(
            8,
            0,
            accounts[0],
            startTime,
            endTime,
            3,
            1,
            0,
            5,
            0
        )
        await demandLogic.initPriceDriving(
            8,
            web3.fromAscii("Germany"),
            web3.fromAscii("Berlin"),
            0,
            0,
            0,
            web3.fromAscii("N.A."),
            web3.fromAscii("N.A."))
        let tx = await demandLogic.initMatchProperties(8,
            100001,
            0,
            accounts[8]
        )

        tx = await certificateLogic.createCertificateForAssetOwner(5, 100000, {
            from: accounts[8]
        })

        var cert = await certificateLogic.getCertificate(3)
        tx = await demandLogic.matchCertificate(8, 3, { from: accounts[8] })



    })

})