import { BlockchainProperties } from './BlockchainProperties'

export abstract class BlockchainDataModelEntity {

    id: number
    blockchainProperties: BlockchainProperties

    constructor(id: number, blockchainProperties: BlockchainProperties) {

        this.id = id
        this.blockchainProperties = blockchainProperties

    }

    abstract async syncWithBlockchain(): Promise<BlockchainDataModelEntity>


}