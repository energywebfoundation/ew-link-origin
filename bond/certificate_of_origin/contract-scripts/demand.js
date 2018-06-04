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

var DemandLogic = artifacts.require("DemandLogic");

module.exports = async function (callback) {

  const sleep = (ms) => {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  if (process.argv[4] === '--create') {
    const demandLogic = await DemandLogic.deployed();
    const createTx = await demandLogic.createDemand()

    const agreementDate = Math.round(new Date().getTime() / 1000)
    const startTime = agreementDate - 1200
    const endTime = agreementDate + 1200


    const id = createTx.logs.find((log) => log.event === 'createdEmptyDemand').args.id.toNumber();
    const generalAndCouplingTx = await demandLogic.initGeneralAndCoupling(
      id,
      web3.eth.accounts[8],
      web3.eth.accounts[9],
      agreementDate,
      startTime,
      endTime,
      0,
      10,
      0,
      false,
      -1,
      -1
    )

    const txPd = await demandLogic.initPriceDriving(
      id,
      'Germany',
      'Saxony',
      0,
      10
    )

    const txMp = await demandLogic.initMatchProperties(
      id,
      100,
      200,
      web3.eth.accounts[8]
    )

    console.log(await demandLogic.getDemandGeneral(id))

    callback();

  } else {
    console.log("Demand")
    console.log("e.g.: truffle exec create-demand.js --create Test 4 3 0 0 1 0 0 false 0\n")

    callback();
  }

};
