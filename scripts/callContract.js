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
    try {

        let params = await algodClient.getTransactionParams().do();
        console.log("TRANSFER")



        let txn = algosdk.makeApplicationNoOpTxn(sender, params, index, undefined, ['RQX6JUHQRR4X7442D7DQPWPFL2JGSX6KX3EXTIXLCPMJ7EZQLBAN5KQFIY'], undefined, [106059946])
        console.log("algo address " + algosdk.getApplicationAddress(index))
        let txId = txn.txID().toString();

        // sign, send, await
        let signedTxn = txn.signTxn(myaccount.sk);
        console.log("Signed transaction with txID: %s", txId);
        await algodClient.sendRawTransaction(signedTxn).do();
        await algosdk.waitForConfirmation(algodClient, txId, 2);
        algodClient.getApplicationByID

        // display results
        let transactionResponse = await algodClient.pendingTransactionInformation(txId).do();
        console.log("Called app-id:", transactionResponse['txn']['txn']['apid'])
        console.log("transactionId is " + txId)

    } catch (err) {
        console.error("Tests failed!", err);
        process.exit(1);
    }
})()