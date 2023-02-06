
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
    const applicationRes = await algodClient.getApplicationByID(process.env.APP_ID).do()

    const globalState = applicationRes.params['global-state']

    console.log("global state is " + globalState)

    const firstKey = globalState[0].key
    const firstValue = globalState[0].value
    const secondKey = globalState[1].key
    const secondValue = globalState[1].value
    const thirdKey = globalState[2].key
    const thirdValue = globalState[2].value
    const fourthKey = globalState[3].key
    const fourthValue = globalState[3].value

    console.log("first key is : " + firstKey + "first value is: " + firstValue.bytes)
    console.log("second key is : " + secondKey + "second value is: " + secondValue.uint)
    console.log("third key is : " + thirdKey + "third value is: " + thirdValue.uint)
    console.log("fourth key is : " + fourthKey + "fourth value is: " + fourthValue.uint)
    console.log("algo address " + algosdk.getApplicationAddress(parseInt(process.env.APP_ID)))

    const buffC = fs.readFileSync("./build/lottery_contract.json");
    const c1 = new algosdk.ABIContract(JSON.parse(buffC.toString()));
    console.log("Contract Name: " + c1.name);
    console.log("APP ID: " + c1.appId);
    for (let mc of c1.methods) {
        console.log("Method Name " + mc.name);
    }
})()
