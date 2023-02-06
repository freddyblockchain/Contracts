
import dotenv from "dotenv";
import algosdk, { ABIType } from "algosdk";
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

const utf8Encode = new TextEncoder();


(async () => {
    const buff = fs.readFileSync("./build/random.json")
    const contract = new algosdk.ABIContract(JSON.parse(buff.toString()))

    function getMethodByName(name) {
        const m = contract.methods.find((mt) => { return mt.name == name })
        if (m === undefined)
            throw Error("Method undefined")
        return m
    }

    const getRandomNumber = getMethodByName("get")

    const sp = await algodClient.getTransactionParams().do()
    const commonParams = {
        appID: parseInt(110096026),
        sender: sender,
        suggestedParams: sp,
        signer: algosdk.makeBasicAccountTransactionSigner(myaccount)
    }


    function byteArrayToLong(/*byte[]*/byteArray) {
        let bitString = ""
        for (let index in byteArray) {

            bitString += byteArray[index] > 122 ? 1 : 0
        }

        console.log("bit string is : " + bitString)

        const num = parseInt(bitString, 2)

        console.log("int is :" + num)
    };



    const comp = new algosdk.AtomicTransactionComposer()
    comp.addMethodCall({
        method: getRandomNumber, methodArgs: [24586021, utf8Encode.encode(sender)], ...commonParams
    })
    comp.buildGroup()
    const result = await comp.execute(algodClient, 2)

    const randomValue = result.methodResults[0].returnValue

    console.log("type is " + typeof randomValue)

    const keys = Object.keys(randomValue)


    const uintarray = new Uint8Array(Object.values(randomValue))

    console.log("first key " + keys[0] + "first value " + uintarray[0])

    console.log("length of values: " + uintarray.length)

    console.log("return value is : " + randomValue)


    const long = byteArrayToLong(uintarray);

    console.log("\n decoded value is : " + long)
})()