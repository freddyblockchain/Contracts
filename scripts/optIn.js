

import dotenv from "dotenv";
import algosdk from "algosdk";
dotenv.config();

const myaccount = algosdk.mnemonicToSecretKey(process.env.ACCOUNT_MNEMONIC);
const sender = myaccount.addr;

const baseServer = 'https://testnet-algorand.api.purestake.io/ps2'
const port = '';
const token = {
    'X-API-Key': process.env.API_KEY
}

const algodClient = new algosdk.Algodv2(token, baseServer, port);
// This variable is our client. It is the link between our code and the blockchain

let index = parseInt(process.env.APP_ID);
console.log("index is " + index);

(async () => {

    let params = await algodClient.getTransactionParams().do();

    const myAccount = algosdk.mnemonicToSecretKey(process.env.ACCOUNT_MNEMONIC.toString());

    console.log("opting in for app!");
    let optIn = algosdk.makeApplicationOptInTxn(myAccount.addr, params, 119288914);

    let optInTxn = optIn.signTxn(myAccount.sk);
          
    await algodClient.sendRawTransaction(optInTxn).do();

    console.log("optin done")
})()