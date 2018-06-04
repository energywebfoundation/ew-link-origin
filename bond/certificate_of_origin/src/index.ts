
export { Asset, AssetProperties, AssetType, Compliance } from './blockchain-facade/Asset'
export { Certificate } from './blockchain-facade/Certificate'
export { ProducingAsset, ProducingAssetProperties } from './blockchain-facade/ProducingAsset'
export { ConsumingAsset, ConsumingProperties } from './blockchain-facade/ConsumingAsset'
export { Demand, TimeFrame, Currency, DemandProperties } from './blockchain-facade/Demand'
export { BlockchainProperties } from './blockchain-facade/BlockchainProperties'
export { ContractEventHandler } from './blockchain-facade/ContractEventHandler'
export { EventHandlerManager } from './blockchain-facade/EventHandlerManager'
export { User } from './blockchain-facade/User'
export { General } from './blockchain-facade/General'

import * as DemandLogicTruffleBuild from '../contracts/DemandLogic.json';
import * as AssetProducingLogicTruffleBuild from '../contracts/AssetProducingRegistryLogic.json'
import * as AssetConsumingLogicTruffleBuild from '../contracts/AssetConsumingRegistryLogic.json'
import * as CertificateLogicTruffleBuild from '../contracts/CertificateLogic.json'
import * as CoOTruffleBuild from '../contracts/CoO.json'
import * as UserLogicTruffleBuild from '../contracts/UserLogic.json'

export { DemandLogicTruffleBuild, AssetProducingLogicTruffleBuild, AssetConsumingLogicTruffleBuild, CertificateLogicTruffleBuild, CoOTruffleBuild, UserLogicTruffleBuild }


