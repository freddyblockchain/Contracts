
import dotenv from "dotenv";
import algosdk from "algosdk";
import fs from "fs"
dotenv.config();

const baseServer = 'https://testnet-algorand.api.purestake.io/ps2'
const port = '';
const token = {
    'X-API-Key': process.env.API_KEY
}

const algodClient = new algosdk.Algodv2(token, baseServer, port);

let myaccount = algosdk.mnemonicToSecretKey(process.env.ACCOUNT_MNEMONIC);
let sender = myaccount.addr;


(async () => {
    const buff = fs.readFileSync("./build/lottery_contract.json")
    const contract = new algosdk.ABIContract(JSON.parse(buff.toString()))

    function getMethodByName(name) {
        const m = contract.methods.find((mt) => { return mt.name == name })
        if (m === undefined)
            throw Error("Method undefined")
        return m
    }

    const startLottery = getMethodByName("createLotteryAsset")

    const sp = await algodClient.getTransactionParams().do()
    const commonParams = {
        appID: parseInt(process.env.APP_ID),
        sender: sender,
        suggestedParams: sp,
        signer: algosdk.makeBasicAccountTransactionSigner(myaccount)
    }

    const comp = new algosdk.AtomicTransactionComposer()
    comp.addMethodCall({
        method: startLottery, methodArgs: [], ...commonParams
    })
    comp.buildGroup()
    const result = await comp.execute(algodClient, 2)
})()