import Web3Type from '../types/web3'
import { BlockchainProperties } from './BlockchainProperties'
import { AssetType } from './Asset'
import { Compliance } from './Asset'


export enum Roles {
    TopAdmin,
    UserAdmin,
    AssetAdmin,
    AgreementAdmin,
    AssetManager,
    Trader,
    Matcher
} 

export class User {
    accountAddress: string

    firstName: string
    surname: string
    organization: string
    street: string
    number: string
    zip: string
    city: string
    country: string
    state: string

    roles: number
    active: boolean

    blockchainProperties: BlockchainProperties

    constructor(accountAddress: string, blockchainProperties: BlockchainProperties) {
        this.accountAddress = accountAddress
        this.blockchainProperties = blockchainProperties
    }


    async syncWithBlockchain(): Promise<User> {
        if (this.accountAddress) {

            const userData = await this.blockchainProperties.userLogicInstance.methods.getFullUser(this.accountAddress).call()

            this.firstName = this.blockchainProperties.web3.utils.hexToUtf8(userData.firstName)
            this.surname = this.blockchainProperties.web3.utils.hexToUtf8(userData.surname)
            this.organization = this.blockchainProperties.web3.utils.hexToUtf8(userData.organization)
            this.street = this.blockchainProperties.web3.utils.hexToUtf8(userData.street)
            this.number = this.blockchainProperties.web3.utils.hexToUtf8(userData.number)
            this.zip = this.blockchainProperties.web3.utils.hexToUtf8(userData.zip)
            this.city = this.blockchainProperties.web3.utils.hexToUtf8(userData.city)
            this.country = this.blockchainProperties.web3.utils.hexToUtf8(userData.country)
            this.state = this.blockchainProperties.web3.utils.hexToUtf8(userData.state)

            this.roles = parseInt(userData.roles, 10)
            this.active = userData.active

        }
        return this
    }

}