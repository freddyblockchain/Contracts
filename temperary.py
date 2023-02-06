import base64
import json
from contracts.beakerContract import MyApp
from beaker import (
    client,
    sandbox,
    consts,
)
from algosdk import encoding
from pathlib import Path


def deployContract():

    calc = MyApp()
    accts = sandbox.get_accounts()

    acct1 = accts.pop()
    acct2 = accts.pop()

    app_client1 = client.ApplicationClient(
        client=sandbox.get_algod_client(), app=MyApp(), signer=acct1.signer
    )
    calc.dump((Path(__file__).parent / "artifacts"))
    print(calc.approval_program)
    print(calc.clear_program)
    print(json.dumps(calc.contract.dictify()))
    app_client1.create()
    app_client1.fund(10 * consts.algo)


def callMethod(app_id):
    accts = sandbox.get_accounts()

    acct1 = accts.pop()
    acct2 = accts.pop()

    app_client1 = client.ApplicationClient(
        client=sandbox.get_algod_client(),
        app=MyApp(),
        app_id=app_id,
        signer=acct1.signer,
    )

    c_encoded = "c".encode()
    key2 = encoding.decode_address(acct2.address) + c_encoded
    app_client1.call(
        MyApp.signup,
        affiliate=acct1.address,
        linkCreator=acct2.address,
        boxes=[
            [app_client1.app_id, encoding.decode_address(acct1.address)],
            [
                app_client1.app_id,
                key2,
            ],
        ],
    )
    print(f"Current app state: {app_client1.get_application_state()}")


def callHandleTransactions(app_id):
    accts = sandbox.get_accounts()

    acct1 = accts.pop()
    acct2 = accts.pop()

    app_client1 = client.ApplicationClient(
        client=sandbox.get_algod_client(),
        app=MyApp(),
        app_id=app_id,
        signer=acct1.signer,
    )

    a_encoded = "a".encode()
    key2 = encoding.decode_address(acct1.address) + a_encoded

    client.

    app_client1.add_transaction
    app_client1.call(
        MyApp.affiliate_transaction,
        affiliate=acct1.address,
        boxes=[
            [app_client1.app_id, encoding.decode_address(acct1.address)],
            [
                app_client1.app_id,
                key2,
            ],
        ],
    )
    print(f"Current app state: {app_client1.get_application_state()}")
