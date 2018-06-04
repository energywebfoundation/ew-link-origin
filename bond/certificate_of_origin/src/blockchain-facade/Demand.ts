import Web3Type from '../types/web3'
import { BlockchainProperties } from './BlockchainProperties'
import { AssetType } from './Asset'
import { Compliance } from './Asset'
import { BlockchainDataModelEntity } from './BlockchainDataModelEntity'

export interface FullDemandProperties {
    enabledProperties: boolean[]
    originator: string
    buyer: string
    startTime: number
    endTime: number
    timeframe: TimeFrame
    pricePerCertifiedWh: number
    currency: Currency
    productingAsset: number
    consumingAsset: number
    locationCountry: string
    locationRegion: string
    assettype: AssetType
    minCO2Offset: number
    otherGreenAttributes: string
    typeOfPublicSupport: string
    targetWhPerPeriod: number
    matcher: string,
    registryCompliance: Compliance

}

export enum TimeFrame {
    yearly,
    monthly,
    daily,
    hourly
}

export enum Currency {
    Euro,
    USD,
    SingaporeDollar,
    Ether
}

export enum DemandProperties {
    Originator,
    AssetType,
    Compliance,
    Country,
    Region,
    MinCO2,
    Producing,
    Consuming
}



export class Demand extends BlockchainDataModelEntity implements FullDemandProperties {
    id: number
    enabledProperties: boolean[]

    //MatcherProperties
    targetWhPerPeriod: number
    currentWhPerPeriod: number
    certInCurrentPeriod: number
    productionLastSetInPeriod: number
    matcher: string
    matcherPropertiesExists: boolean
    //PriceDriving
    locationCountry: string
    locationRegion: string
    assettype: AssetType
    minCO2Offset: number
    priceDrivingExists: boolean
    registryCompliance: Compliance
    otherGreenAttributes: string
    typeOfPublicSupport: string
    //GeneralInfo
    originator: string
    buyer: string
    agreementDate: number
    startTime: number
    endTime: number
    currency: Currency
    generalInfoExists: boolean
    //Demand and Coupling
    enabled: boolean
    timeframe: TimeFrame
    productingAsset: number
    consumingAsset: number
    demandMask: number
    pricePerCertifiedWh: number

    initialized: boolean

    blockchainProperties: BlockchainProperties

    constructor(id: number, blockchainProperties: BlockchainProperties) {
        super(id, blockchainProperties)
        this.initialized = false
    }


    static async CREATE_DEMAND(demandProperties: FullDemandProperties, blockchainProperties: BlockchainProperties, account: string): Promise<Demand> {
        const gasCreate = await blockchainProperties.demandLogicInstance.methods
            .createDemand(demandProperties.enabledProperties)
            .estimateGas({ from: account })

        const txCreate = await blockchainProperties.demandLogicInstance.methods
            .createDemand(demandProperties.enabledProperties)
            .send({ from: account, gas: Math.round(gasCreate * 1.1) })

        const demandId = parseInt(txCreate.events.createdEmptyDemand.returnValues._demandId, 10)

        const initGeneralParams = [
            demandId,
            demandProperties.originator,
            demandProperties.buyer,
            demandProperties.startTime,
            demandProperties.endTime,
            demandProperties.timeframe,
            demandProperties.pricePerCertifiedWh,
            demandProperties.currency,
            demandProperties.productingAsset,
            demandProperties.consumingAsset
        ]

        const gasInitGeneral = await blockchainProperties.demandLogicInstance.methods
            .initGeneralAndCoupling(...initGeneralParams)
            .estimateGas({ from: account })

        const txInitGeneral = await blockchainProperties.demandLogicInstance.methods
            .initGeneralAndCoupling(...initGeneralParams)
            .send({ from: account, gas: Math.round(gasInitGeneral * 1.1) })

        const initMatchPropertiesParams = [
            demandId,
            demandProperties.targetWhPerPeriod,
            0,
            demandProperties.matcher
        ]

        const gasInitMatcher = await blockchainProperties.demandLogicInstance.methods
            .initMatchProperties(...initMatchPropertiesParams)
            .estimateGas({ from: account })

        const txInitMatcher = await blockchainProperties.demandLogicInstance.methods
            .initMatchProperties(...initMatchPropertiesParams)
            .send({ from: account, gas: Math.round(gasInitMatcher * 1.1) })

        const initPriceDrivingPropertiesParams = [
            demandId,
            blockchainProperties.web3.utils.fromUtf8(demandProperties.locationCountry),
            blockchainProperties.web3.utils.fromUtf8(demandProperties.locationRegion),
            demandProperties.assettype,
            demandProperties.minCO2Offset,
            demandProperties.registryCompliance,
            blockchainProperties.web3.utils.fromUtf8(demandProperties.otherGreenAttributes),
            blockchainProperties.web3.utils.fromUtf8(demandProperties.typeOfPublicSupport)
        ]

        const gasInitPriceDriving = await blockchainProperties.demandLogicInstance.methods
            .initPriceDriving(...initPriceDrivingPropertiesParams)
            .estimateGas({ from: account })

        const txInitPriceDriving = await blockchainProperties.demandLogicInstance.methods
            .initPriceDriving(...initPriceDrivingPropertiesParams)
            .send({ from: account, gas: Math.round(gasInitPriceDriving * 1.1) })

        return (new Demand(demandId, blockchainProperties)).syncWithBlockchain()
    }

    static async GET_ALL_DEMAND_LIST_LENGTH(blockchainProperties: BlockchainProperties) {
        return parseInt(await blockchainProperties.demandLogicInstance.methods.getAllDemandListLength().call(), 10)
    }

    static async GET_ACTIVE_DEMAND_LIST_LENGTH(blockchainProperties: BlockchainProperties) {
        return parseInt(await blockchainProperties.demandLogicInstance.methods.getActiveDemandListLength().call(), 10)
    }

    static async GET_ACTIVE_DEMAND_ID_AT(index: number, blockchainProperties: BlockchainProperties) {

        return blockchainProperties.demandLogicInstance.methods.getActiveDemandIdAt(index).call()
    }

    static async GET_ALL_ACTIVE_DEMANDS(blockchainProperties: BlockchainProperties) {

        const demandIdPromises = Array(await Demand.GET_ACTIVE_DEMAND_LIST_LENGTH(blockchainProperties))
            .fill(null)
            .map((item, index) => Demand.GET_ACTIVE_DEMAND_ID_AT(index, blockchainProperties))

        const demandIds = await Promise.all(demandIdPromises)

        const demandPromises = demandIds.map((id) => ((new Demand(id, blockchainProperties)).syncWithBlockchain()))

        return Promise.all(demandPromises)

    }

    getBitFromDemandMask(bitPosition: number): boolean {

        return ((2 ** bitPosition) & this.demandMask) !== 0
    }

    async getCurrentPeriod() {
        return await this.blockchainProperties.demandLogicInstance.methods.getCurrentPeriod(this.id).call()
    }

    async matchDemand(wh: number, assetId: number) {

        //console.log('! ' + this.id + ' ' + wh + ' ' + assetId + ' from: ' + this.blockchainProperties.matcherAccount)


        const gas = await this.blockchainProperties.demandLogicInstance.methods
            .matchDemand(this.id, wh, assetId)
            .estimateGas({ from: this.blockchainProperties.matcherAccount })

        const tx = await this.blockchainProperties.demandLogicInstance.methods
            .matchDemand(this.id, wh, assetId)
            .send({ from: this.blockchainProperties.matcherAccount, gas: Math.round(gas * 1.1) })


        return tx
    }

    async matchCertificate(certificateId: number) {

        const gas = await this.blockchainProperties.demandLogicInstance.methods
            .matchCertificate(this.id, certificateId)
            .estimateGas({ from: this.blockchainProperties.matcherAccount })

        const tx = await this.blockchainProperties.demandLogicInstance.methods
            .matchCertificate(this.id, certificateId)
            .send({ from: this.blockchainProperties.matcherAccount, gas: Math.round(gas * 1.1) })

        return tx

    }


    async syncWithBlockchain(): Promise<Demand> {
        if (this.id != null) {
            const structDataPromises = []
            structDataPromises.push(this.blockchainProperties.demandLogicInstance.methods.getDemandGeneral(this.id).call())
            structDataPromises.push(this.blockchainProperties.demandLogicInstance.methods.getDemandPriceDriving(this.id).call())
            structDataPromises.push(this.blockchainProperties.demandLogicInstance.methods.getDemandMatcherProperties(this.id).call())
            structDataPromises.push(this.blockchainProperties.demandLogicInstance.methods.getDemandCoupling(this.id).call())

            const demandData = await Promise.all(structDataPromises)

            this.targetWhPerPeriod = parseInt(demandData[2].targetWhPerPeriod, 10)
            this.currentWhPerPeriod = parseInt(demandData[2].currentWhPerPeriod, 10)
            this.certInCurrentPeriod = parseInt(demandData[2].certInCurrentPeriod, 10)
            this.productionLastSetInPeriod = parseInt(demandData[2].productionLastSetInPeriod, 10)
            this.matcher = demandData[2].matcher

            //PriceDriving
            this.locationCountry = this.blockchainProperties.web3.utils.hexToUtf8(demandData[1].locationCountry)
            this.locationRegion = this.blockchainProperties.web3.utils.hexToUtf8(demandData[1].locationRegion)
            this.assettype = parseInt(demandData[1].assettype, 10)
            this.minCO2Offset = parseInt(demandData[1].minCO2Offset, 10)

            this.registryCompliance = parseInt(demandData[1].registryCompliance, 10)
            //GeneralInfo
            this.originator = demandData[0].originator
            this.buyer = demandData[0].buyer
            this.agreementDate = parseInt(demandData[0].agreementDate, 10)
            this.startTime = parseInt(demandData[0].startTime, 10)
            this.endTime = parseInt(demandData[0].endTime, 10)
            this.currency = parseInt(demandData[0].currency, 10)
            this.demandMask = parseInt(demandData[0].demandMask, 10)
            this.timeframe = parseInt(demandData[0].timeframe, 10)
            //Demand and Coupling

            this.productingAsset = parseInt(demandData[3].producingAssets, 10)
            this.consumingAsset = parseInt(demandData[3].consumingAssets, 10)

            this.initialized = true

        }
        return this
    }

    async checkDemandCoupling(demandId: number, prodAssetId: number, wCreated: number) {
        console.log(await this.blockchainProperties.demandLogicInstance.methods.checkDemandCoupling(demandId, prodAssetId, wCreated).call())
    }

    async checkDemandGeneral(demandId: number, prodAssetId: number) {
        console.log(await this.blockchainProperties.demandLogicInstance.methods.asynccheckDemandGeneral(demandId, prodAssetId).call())
    }

    async checkMatcher(demandId: number, wCreated: number, matcher: string) {
        console.log(await this.blockchainProperties.demandLogicInstance.methods.checkMatcher(demandId, wCreated).call({ from: matcher }))
    }

    async checkPriceDriving(demandId: number, prodAssetId: number, wCreated: number, co2Saved: number) {
        console.log(await this.blockchainProperties.demandLogicInstance.methods.checkPriceDriving(demandId, prodAssetId, wCreated, co2Saved).call())

    }

    async getDemandEvents() {

        return (await this.blockchainProperties.demandLogicInstance.getPastEvents('allEvents', {
            fromBlock: 0,
            toBlock: 'latest',
            topics: [null, this.blockchainProperties.web3.utils.padLeft(this.blockchainProperties.web3.utils.fromDecimal(this.id), 64, '0')]
        }))
    }
}