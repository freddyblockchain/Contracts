from beaker.application import Application
from beaker.decorators import external, internal
from pathlib import Path
from pyteal import (
    App,
    Assert,
    Btoi,
    Bytes,
    Concat,
    Extract,
    Global,
    If,
    InnerTxnBuilder,
    Int,
    Itob,
    Pop,
    Seq,
    Txn,
    TxnField,
    TxnType,
)
from pyteal.ast import abi


class MyApp(Application):
    contractFee = Int(1000000)

    @external
    def signup(self, user: abi.Address, affiliate: abi.Address):
        affiliateKey = Concat(
            affiliate.get(),
            Bytes("c"),
        )
        return Seq(
            userBox := App.box_get(user.get()),
            Assert(userBox.hasValue() == Int(0)),
            App.box_put(
                user.get(),
                affiliate.get(),
            ),
            affiliateBox := App.box_get(affiliateKey),
            App.box_put(
                affiliateKey,
                If(affiliateBox.hasValue() == Int(0))
                .Then(Itob(Int(1)))
                .Else(Itob(Btoi(affiliateBox.value()) + Int(1))),
            ),
        )

    @external
    def affiliate_transaction(
        self, payment: abi.PaymentTransaction, affiliate: abi.Account
    ):
        userKey = Txn.sender()
        affiliateAmountKey = Concat(affiliate.address(), Bytes("a"))
        return Seq(
            userBox := App.box_get(userKey),
            Assert(payment.get().sender() == Txn.sender()),
            Assert(payment.get().receiver() == Global.current_application_address()),
            Assert(userBox.hasValue() == Int(1)),
            Assert(userBox.value() == affiliate.address()),
            self.handle_transactions(payment, affiliate),
            affiliateAmountBox := App.box_get(affiliateAmountKey),
            App.box_put(
                affiliateAmountKey,
                If(affiliateAmountBox.hasValue() == Int(0))
                .Then(Itob(Int(1)))
                .Else(
                    Itob(
                        Btoi(affiliateAmountBox.value())
                        + (payment.get().amount() - self.contractFee)
                    )
                ),
            ),
        )

    @internal
    def handle_transactions(
        self, payment: abi.PaymentTransaction, affiliate: abi.Account
    ):
        return Seq(
            [
                InnerTxnBuilder.Begin(),
                InnerTxnBuilder.SetFields(
                    {
                        TxnField.type_enum: TxnType.Payment,
                        TxnField.sender: Global.current_application_address(),
                        TxnField.amount: Int(1000000),
                        TxnField.receiver: Global.creator_address(),
                    }
                ),
                InnerTxnBuilder.Next(),
                InnerTxnBuilder.SetFields(
                    {
                        TxnField.type_enum: TxnType.Payment,
                        TxnField.sender: Global.current_application_address(),
                        TxnField.amount: payment.get().amount() - self.contractFee,
                        TxnField.receiver: affiliate.address(),
                    }
                ),
                InnerTxnBuilder.Submit(),
            ]
        )


if __name__ == "__main__":
    import json

    app = MyApp()
    app.dump((Path(__file__).parent / "artifacts"))
