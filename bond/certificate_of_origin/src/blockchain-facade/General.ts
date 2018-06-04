import { BlockchainProperties } from './BlockchainProperties'

export namespace General {


    export async function createCertificateForAssetOwner(blockchainProperties: BlockchainProperties, wh: number, assetId: number) { 

        const gas = await blockchainProperties.certificateLogicInstance.methods
            .createCertificateForAssetOwner(assetId, wh)
            .estimateGas({from: blockchainProperties.matcherAccount})
        
        const tx = await blockchainProperties.certificateLogicInstance.methods
             .createCertificateForAssetOwner(assetId, wh)
             .send({from: blockchainProperties.matcherAccount, gas: Math.round(gas * 1.1)})
   
        return tx
    }

}