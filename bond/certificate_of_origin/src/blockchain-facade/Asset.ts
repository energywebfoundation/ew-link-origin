import Web3Type from '../types/web3'
import { BlockchainProperties } from './BlockchainProperties'
import { ProducingAsset } from './ProducingAsset'
import { ConsumingAsset } from './ConsumingAsset'
import { BlockchainDataModelEntity } from './BlockchainDataModelEntity'

export interface AssetProperties {
      // GeneralInformation
      smartMeter: string
      owner: string
      operationalSince: number
      capacityWh: number
      lastSmartMeterReadWh?: number
      active: boolean
      lastSmartMeterReadFileHash?: string
      country: string
      region: string
      zip: string
      city: string
      street: string
      houseNumber: string
      gpsLatitude: string
      gpsLongitude: string
}

export enum AssetType {
    Wind,
    Solar,
    RunRiverHydro,
    BiomassGas
}

export enum Compliance {
    none,
    IREC,
    EEC,
    TIGR
}


export abstract class Asset extends BlockchainDataModelEntity implements AssetProperties{


    id: number
    // GeneralInformation
    smartMeter: string
    owner: string

    operationalSince: number
    capacityWh: number
    lastSmartMeterReadWh: number
    active: boolean

    lastSmartMeterReadFileHash: string


    // Location
    country: string
    region: string
    zip: string
    city: string
    street: string
    houseNumber: string
    gpsLatitude: string
    gpsLongitude: string

    initialized: boolean;

    blockchainProperties: BlockchainProperties

    constructor(id: number, blockchainProperties: BlockchainProperties) {
        super(id, blockchainProperties)

        this.initialized = false
    }



    



}