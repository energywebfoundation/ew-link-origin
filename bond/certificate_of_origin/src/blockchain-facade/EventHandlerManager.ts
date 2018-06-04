import Web3Type from '../types/web3'
import { ContractEventHandler } from './ContractEventHandler'
import { BlockchainProperties } from './BlockchainProperties'

export class EventHandlerManager {
    private contractEventHandlers: ContractEventHandler[]
    private tickTime: number
    private running: boolean
    private blockchainProperties: BlockchainProperties

    constructor(tickTime: number, blockchainProperties: BlockchainProperties) {
        this.tickTime = tickTime
        this.blockchainProperties = blockchainProperties
        this.contractEventHandlers = []
    }

    registerEventHandler(eventHandler: ContractEventHandler) {
        this.contractEventHandlers.push(eventHandler)
    }

    start() {
        this.running = true
        this.loop()
    
    }

    stop() {
        this.running = false
    }

    async loop() {
        while (this.running) {
            this.contractEventHandlers.forEach((eventHandler: ContractEventHandler) => eventHandler.tick(this.blockchainProperties))
            await this.sleep(this.tickTime)
        }
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms))
    }

}