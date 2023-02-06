from pyteal import *
import json

# Create an expression to store 0 in the `Count` global variable and return 1
handle_creation = Seq(
    App.globalPut(Bytes("Participants"), Int(0)),
    App.globalPut(Bytes("Ongoing"), Int(0)),
    App.globalPut(Bytes("LotteryRound"), Int(0)),
    App.globalPut(Bytes("Winner"), Int(0)),
    App.globalPut(Bytes("LotteryResolved"), Int(0)),
    Approve(),
)

# Main router class
router = Router(
    "my-first-router",
    BareCallActions(
        no_op=OnCompleteAction.create_only(handle_creation),
        update_application=OnCompleteAction.always(Reject()),
        delete_application=OnCompleteAction.always(Reject()),
        close_out=OnCompleteAction.never(),
        opt_in=OnCompleteAction.always(Approve()),
        clear_state=OnCompleteAction.never(),
    ),
)


@router.method(no_op=CallConfig.CALL)
def resetLottery(*, output: abi.String) -> Expr:
    """Use this method for when the winner does not claim his/her reward, and the lottery is blocked."""
    return Seq(
        Assert(App.globalGet(Bytes("Ongoing")) == Int(1)),
        Assert(Global.round() >= App.globalGet(Bytes("LotteryRound")) + Int(60)),
        App.globalPut(Bytes("Participants"), Int(0)),
        App.globalPut(Bytes("Ongoing"), Int(0)),
        App.globalPut(Bytes("LotteryResolved"), Int(0)),
        App.globalPut(Bytes("Winner"), Int(0)),
        output.set("lottery is reset!"),
    )


@router.method(no_op=CallConfig.CALL)
def claimWin(asset_to_receive: abi.Asset) -> Expr:
    return Seq(
        Assert(App.globalGet(Bytes("Ongoing")) == Int(1)),
        Assert(App.globalGet(Bytes("LotteryResolved")) == Int(1)),
        Assert(
            App.localGet(Txn.sender(), Bytes("ParticipantNumber"))
            == App.globalGet(Bytes("Winner"))
        ),
        Assert(
            App.localGet(Txn.sender(), Bytes("ParticipantLotteryRound"))
            == App.globalGet(Bytes("LotteryRound"))
        ),
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields(
            {
                TxnField.type_enum: TxnType.AssetTransfer,
                TxnField.asset_receiver: Txn.sender(),
                TxnField.asset_amount: Int(1),
                TxnField.xfer_asset: asset_to_receive.asset_id(),  # Must be in the assets array sent as part of the application call
            }
        ),
        InnerTxnBuilder.Submit(),
        App.globalPut(Bytes("LotteryResolved"), Int(0)),
        App.globalPut(Bytes("Participants"), Int(0)),
        App.globalPut(Bytes("Ongoing"), Int(0)),
        App.globalPut(Bytes("Winner"), Int(0)),
    )


@router.method(no_op=CallConfig.CALL)
def resolveLottery(
    random_contract_call: abi.Application, *, output: abi.Uint64
) -> Expr:
    return Seq(
        Assert(App.globalGet(Bytes("Ongoing")) == Int(1)),
        Assert(App.globalGet(Bytes("LotteryResolved")) == Int(0)),
        Assert(random_contract_call.application_id() == Int(110096026)),
        Assert(Global.round() >= App.globalGet(Bytes("LotteryRound")) + Int(5)),
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.MethodCall(
            app_id=random_contract_call.application_id(),
            method_signature="get(uint64,byte[])byte[]",
            args=[
                Itob(App.globalGet(Bytes("LotteryRound"))),
                Bytes(
                    "base32",
                    "7Z5PWO2C6LFNQFGHWKSK5H47IQP5OJW2M3HA2QPXTY3WTNP5NU2MHBW27M",
                ),
            ],
        ),
        InnerTxnBuilder.Submit(),
        App.globalPut(
            Bytes("Winner"),
            Btoi(Substring(InnerTxn.last_log(), Int(8), Int(16)))
            % App.globalGet(Bytes("Participants"))
            + Int(1),
        ),
        App.globalPut(Bytes("LotteryResolved"), Int(1)),
        output.set(App.globalGet(Bytes("Winner"))),
    )


@router.method(no_op=CallConfig.CALL)
def participate(*, output: abi.Uint64) -> Expr:
    return Seq(
        Assert(App.globalGet(Bytes("Ongoing")) == Int(1)),
        Assert(Global.round() <= App.globalGet(Bytes("LotteryRound"))),
        Assert(
            App.localGet(Txn.sender(), Bytes("ParticipantLotteryRound"))
            != App.globalGet(Bytes("LotteryRound"))
        ),
        App.globalPut(
            Bytes("Participants"), App.globalGet(Bytes("Participants")) + Int(1)
        ),
        App.localPut(
            Txn.sender(),
            Bytes("ParticipantNumber"),
            App.globalGet(Bytes("Participants")),
        ),
        App.localPut(
            Txn.sender(),
            Bytes("ParticipantLotteryRound"),
            App.globalGet(Bytes("LotteryRound")),
        ),
        output.set(App.localGet(Txn.sender(), Bytes("ParticipantNumber"))),
    )


@router.method(no_op=CallConfig.CALL)
def startLottery() -> Expr:
    return Seq(
        Assert(App.globalGet(Bytes("Ongoing")) == Int(0)),
        App.globalPut(Bytes("LotteryRound"), Global.round() + Int(15)),
        App.globalPut(Bytes("Ongoing"), Int(1)),
    )


@router.method(no_op=CallConfig.CALL)
def createLotteryAsset() -> Expr:
    return Seq(
        [
            Assert(Txn.sender() == Global.creator_address()),
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields(
                {
                    TxnField.type_enum: TxnType.AssetConfig,
                    TxnField.config_asset_total: Int(10000),
                    TxnField.config_asset_decimals: Int(0),
                    TxnField.config_asset_unit_name: Bytes("la"),
                    TxnField.config_asset_name: Bytes("LotteryAsset"),
                    TxnField.config_asset_url: Bytes("LotteryAsset.win"),
                    TxnField.config_asset_manager: Global.current_application_address(),
                    TxnField.config_asset_reserve: Global.current_application_address(),
                    TxnField.config_asset_freeze: Global.current_application_address(),
                    TxnField.config_asset_clawback: Global.current_application_address(),
                }
            ),
            InnerTxnBuilder.Submit(),
        ]
    )


approval_program, clear_state_program, contract = router.compile_program(
    version=7, optimize=OptimizeOptions(scratch_slots=True)
)

if __name__ == "__main__":
    import json

    calc = Calculator()
    print(calc.approval_program)
    print(calc.clear_program)
    print(json.dumps(calc.contract.dictify()))
