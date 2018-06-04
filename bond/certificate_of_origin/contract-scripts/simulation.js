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
// @authors: slock.it GmbH, Heiko Burkhardt, heiko.burkhardt@slock.it


var AssetProducingRegistryLogic = artifacts.require("AssetProducingRegistryLogic");
var AssetConsumingRegistryLogic = artifacts.require("AssetConsumingRegistryLogic");

var DemandLogic = artifacts.require("DemandLogic");

const sleepTime = 5000

module.exports = async function (callback) {
    const sleep = (ms) => {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    const assetLogic = await AssetProducingRegistryLogic.deployed();
    const cosumingAssetLogic = await AssetConsumingRegistryLogic.deployed();
    const assetID = await createAsset(assetLogic, 'Saxony', "0x3b07f15efb10f29b3fc222fb7e717e9af0cc4243")
    const assetID2 = await createAsset(assetLogic, 'BW', "0x71c31ff1faa17b1cb5189fd845e0cca650d215d3")
    const assetID3 = await createAsset(assetLogic, 'Berlin', "0x3b07f15efb10f29b3fc222fb7e717e9af0cc4243")
    let assetID4 = null
    const assetID5 = await createConsumingAsset(cosumingAssetLogic, 'Berlin')
    const assetID6 = await createAsset(assetLogic, 'NRW', "0x71c31ff1faa17b1cb5189fd845e0cca650d215d3")

    await createDemand('BW', false, -1, 9000000, false, 0)
    await createDemand('Saxony', false, -1, 380000, false, 0)
    await createDemand('Saxony', true, 0, 9000000, false, 0)
    await createDemand('Saxony', false, -1, 9000000, false, 0)
    await createDemand('NRW', false, -1, 9000000, false, 0)
    await createDemand('NRW', false, assetID6, 9000000, true, assetID5)


    let i = 0;


    console.log('demand creation done')
    while (true) {

        console.log('\n# ' + i)

        const filehashgenerated = assetID + i

        const tx = await assetLogic.saveSmartMeterRead(assetID, 430 * i, false, 'assetID' + i, 300 * i, false, { from: "0x00f4af465162c05843ea38d203d37f7aad2e2c17", gasPrice: 0 })
        console.log('- Saved new meter read for asset ' + assetID + ': ' + 430 * i + ' ' + 300 * i)
        await sleep(sleepTime);

        const tx6 = await assetLogic.saveSmartMeterRead(assetID6, 10 * i, false, 'assetID6' + i, 300 * i, false, { from: "0x00f4af465162c05843ea38d203d37f7aad2e2c17", gasPrice: 0 })
        console.log('- Saved new meter read for asset ' + assetID6 + ': ' + 10 * i + ' ' + 2 * i)
        await sleep(sleepTime);

        const tx5 = await cosumingAssetLogic.saveSmartMeterRead(assetID5, 2 * i, 'assetID5' + i, false, { from: "0x00f4af465162c05843ea38d203d37f7aad2e2c17", gasPrice: 0 })
        console.log('- Saved new meter read for consuming asset ' + assetID5 + ': ' + 2 * i)
        await sleep(sleepTime);

        if (i < 3) {
            const tx2 = await assetLogic.saveSmartMeterRead(assetID2, 10 * i, false, 'assetID2' + i, 7 * i, false, { from: "0x00f4af465162c05843ea38d203d37f7aad2e2c17", gasPrice: 0 })
            console.log('- Saved new meter read for asset ' + assetID2 + ': ' + 10 * i + ' ' + 7 * i)
            await sleep(sleepTime);
        } else if (i == 3) {
            console.log('- Asset ' + assetID2 + ' inactive')
            await assetLogic.setActive(
                assetID2,
                false,
                { from: "0xcea1c413a570654fa85e78f7c17b755563fec5a5", gasPrice: 0 }
            )
            await sleep(sleepTime);
        }

        const tx3 = await assetLogic.saveSmartMeterRead(assetID3, 10 * i, false, 'assetID3' + i, 7 * i, false, { from: "0x00f4af465162c05843ea38d203d37f7aad2e2c17", gasPrice: 0 })
        console.log('- Saved new meter read for asset ' + assetID3 + ': ' + 10 * i + ' ' + 7 * i)
        await sleep(sleepTime);

        if (i == 2) {
            assetID4 = await createAsset(assetLogic, 'Saxony', "0x3b07f15efb10f29b3fc222fb7e717e9af0cc4243")
            await sleep(sleepTime);
        } else if (i > 2) {
            const tx4 = await assetLogic.saveSmartMeterRead(assetID4, 10 * i, false, 'assetID4' + i, 7 * i, false, { from: "0x00f4af465162c05843ea38d203d37f7aad2e2c17", gasPrice: 0 })
            console.log('- Saved new meter read for asset ' + assetID4 + ': ' + 10 * i + ' ' + 7 * i)
            await sleep(sleepTime);
        }

        if (i == 3) {
            await createDemand('Berlin', false, -1, 9000000, false, 0)
            await sleep(sleepTime);

        }

        await web3.currentProvider.send(
            {
                jsonrpc: '2.0',
                method: 'evm_increaseTime',
                params: [86400],
                id: 0
            })

        const time = new Date((await web3.eth.getBlock('latest').timestamp + 86400) * 1000)
        console.log('# New time: ' + time)
        i++;
    }

    callback();

};

async function createDemand(region, coupled, coupledAsset, endTimeOffset, timlyCoupled, consumingAsset) {
    const demandLogic = await DemandLogic.deployed();

    const createTx = await demandLogic.createDemand([false, true, true, true, true, false, coupledAsset !== -1, timlyCoupled, false, false], { from: "0x3b07f15efb10f29b3fc222fb7e717e9af0cc4243", gasPrice: 0 })

    //const agreementDate = Math.round(new Date().getTime() / 1000)
    const agreementDate = parseInt((await web3.eth.getBlock('latest')).timestamp, 10);

    const startTime = agreementDate - 12000000
    const endTime = agreementDate + endTimeOffset

    const id = createTx.logs.find((log) => log.event === 'createdEmptyDemand').args._demandId.toNumber();
    console.log('found demandID:' + id + " consumingasset: " + consumingAsset)

    const generalAndCouplingTx = await demandLogic.initGeneralAndCoupling(
        id,
        0, // originator 
        "0x84a2c086ffa013d06285cdd303556ec9be5a1ff7", // buyer
        startTime,
        endTime,
        3,
        10,
        0,
        coupledAsset === -1 ? 0 : coupledAsset,
        consumingAsset,
        { from: "0x3b07f15efb10f29b3fc222fb7e717e9af0cc4243", gasPrice: 0 }
    )
    console.log(id + 'generalAndCoupling')

    const txPd = await demandLogic.initPriceDriving(
        id,
        web3.fromAscii('Germany'),
        web3.fromAscii(region),
        0,
        1,
        0,
        web3.fromAscii('none'),
        web3.fromAscii('none'),
        { from: "0x3b07f15efb10f29b3fc222fb7e717e9af0cc4243", gasPrice: 0 }
    )
    console.log(id + 'priceDriving')

    const txMp = await demandLogic.initMatchProperties(
        id,
        100,
        0,
        "0x343854a430653571b4de6bf2b8c475f828036c30",
        { from: "0x3b07f15efb10f29b3fc222fb7e717e9af0cc4243", gasPrice: 0 }
    )


    console.log('- Demand created id: ' + id)
    return id;
}

async function createAsset(assetLogic, region, owner) {

    const createTx = await assetLogic.createAsset({ from: "0x3b07f15efb10f29b3fc222fb7e717e9af0cc4243", gasPrice: 0 })

    const id = createTx.logs.find((log) => log.event === 'LogAssetCreated').args._assetId.toNumber();

    await assetLogic.initGeneral(
        id,
        "0x00f4af465162c05843ea38d203d37f7aad2e2c17", //smart meter
        owner, //owner
        1234567890,
        true,
        { from: "0xcea1c413a570654fa85e78f7c17b755563fec5a5", gasPrice: 0 }
    )

    await assetLogic.initProducingProperties
        (id,
        0,
        1000,
        0,
        web3.fromAscii("N.A."),
        web3.fromAscii("N.A."),
        { from: "0xcea1c413a570654fa85e78f7c17b755563fec5a5", gasPrice: 0 }
        )


    const locationTx = await assetLogic.initLocation(
        id,
        web3.fromAscii('Germany'),
        web3.fromAscii(region),
        web3.fromAscii('12345'),
        web3.fromAscii('Mittweida'),
        web3.fromAscii('Markt'),
        web3.fromAscii('100000'),
        web3.fromAscii('0'),
        web3.fromAscii('0'),
        { from: "0xcea1c413a570654fa85e78f7c17b755563fec5a5", gasPrice: 0 }
    )
    console.log('- Asset created id: ' + id)
    return id;
}

async function createConsumingAsset(assetLogic, region) {

    const createTx = await assetLogic.createAsset({ from: "0x3b07f15efb10f29b3fc222fb7e717e9af0cc4243", gasPrice: 0 })

    const id = createTx.logs.find((log) => log.event === 'LogAssetCreated').args._assetId.toNumber();

    const generalTx = await assetLogic.initGeneral(
        id,
        "0x00f4af465162c05843ea38d203d37f7aad2e2c17", // smart meter
        "0x3b07f15efb10f29b3fc222fb7e717e9af0cc4243", // owner
        0,
        100000,
        false,
        true,
        { from: "0x3b07f15efb10f29b3fc222fb7e717e9af0cc4243", gasPrice: 0 }
    )

    const locationTx = await assetLogic.initLocation(
        id,
        web3.fromAscii('Germany'),
        web3.fromAscii(region),
        web3.fromAscii('12345'),
        web3.fromAscii('Mittweida'),
        web3.fromAscii('Markt'),
        web3.fromAscii('0'),
        web3.fromAscii('0'),
        web3.fromAscii('0'),
        { from: "0x3b07f15efb10f29b3fc222fb7e717e9af0cc4243", gasPrice: 0 }
    )
    console.log('- Consuming asset created id: ' + id)
    return id;
}

