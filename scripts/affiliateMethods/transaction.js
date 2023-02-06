import dotenv from "dotenv";
import algosdk from "algosdk";
import { TextEncoder } from "util";
import fs from "fs"
dotenv.config();

const baseServer = 'https://testnet-algorand.api.purestake.io/ps2'
const port = '';
const token = {
    'X-API-Key': process.env.API_KEY
}

const algodClient = new algosdk.Algodv2(token, baseServer, port);

let myaccount = algosdk.mnemonicToSecretKey(process.env.ACCOUNT_MNEMONIC);
let user = myaccount.addr;

let myAccount2 = algosdk.mnemonicToSecretKey(process.env.ACCOUNT_MNEMONIC2);
let affiliate = myAccount2.addr;

const applicationAddress = "YB6KBSSB5DGM4ND74YX6IO5ERXSLST7TP3EAO6RXPU5M6JWFYX3IA7AFJA";



(async () => {
    const encoder = new TextEncoder()
    let encodedA = encoder.encode("a")

    let userDecodedAddress = algosdk.decodeAddress(user);
    let affiliateDecodedAddress = algosdk.decodeAddress(affiliate)

    let userBytes =  concat([userDecodedAddress.publicKey])
    let affiliateBytes = concat([affiliateDecodedAddress.publicKey, encodedA]);

    const buff = fs.readFileSync("./contracts/artifacts/contract.json")
    const contract = new algosdk.ABIContract(JSON.parse(buff.toString()))

    function getMethodByName(name) {
        const m = contract.methods.find((mt) => { return mt.name == name })
        if (m === undefined)
            throw Error("Method undefined")
        return m
    }

    const methodName = getMethodByName("affiliate_transaction")

    const sp = await algodClient.getTransactionParams().do()
    const commonParams = {
        appID: parseInt(process.env.APP_ID),
        sender: user,
        suggestedParams: sp,
        signer: algosdk.makeBasicAccountTransactionSigner(myaccount),

    }

    const comp = new algosdk.AtomicTransactionComposer()
    const txn = {
        txn: new algosdk.Transaction({ from: user, to: applicationAddress, amount: 5000000, ...sp }),
        signer: algosdk.makeBasicAccountTransactionSigner(myaccount)
    }
    comp.addMethodCall({
        method: methodName, methodArgs: [txn, affiliate], boxes: [{appIndex: parseInt(process.env.APP_ID), name: userBytes},{appIndex: parseInt(process.env.APP_ID), name: affiliateBytes}], ...commonParams
    })
    comp.buildGroup()
    const result = await comp.execute(algodClient, 2)

    console.log("done")
})()

function concat(arrays) {
    // sum of individual array lengths
    let totalLength = arrays.reduce((acc, value) => acc + value.length, 0);
  
    let result = new Uint8Array(totalLength);
  
    if (!arrays.length) return result;
  
    // for each array - copy it over result
    // next array is copied right after the previous one
    let length = 0;
    for(let array of arrays) {
      result.set(array, length);
      length += array.length;
    }
  
    return result;
  }