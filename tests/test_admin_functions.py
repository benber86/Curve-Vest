import brownie
import pytest


def test_set_operator(fn_isolation, voting_escrow_proxy, admin, operator, alice):
    assert voting_escrow_proxy.admin() == admin
    assert voting_escrow_proxy.operator() == operator
    voting_escrow_proxy.set_operator(alice, {"from": admin})
    assert voting_escrow_proxy.operator() == alice
    with brownie.reverts():
        voting_escrow_proxy.set_operator(alice, {"from": alice})


def test_transfer_ownership(fn_isolation, voting_escrow_proxy, admin, alice):
    with brownie.reverts():
        voting_escrow_proxy.commit_transfer_ownership(alice, {"from": alice})

    assert voting_escrow_proxy.admin() == admin
    voting_escrow_proxy.commit_transfer_ownership(alice, {"from": admin})
    assert voting_escrow_proxy.future_admin() == alice
    assert voting_escrow_proxy.admin() == admin

    with brownie.reverts():
        voting_escrow_proxy.accept_transfer_ownership(
            {"from": admin}
        )  # not future admin

    voting_escrow_proxy.accept_transfer_ownership({"from": alice})
    assert voting_escrow_proxy.admin() == alice


def test_no_transfer_ownership_to_zero_address(
    fn_isolation, voting_escrow_proxy, admin, operator, alice
):
    assert voting_escrow_proxy.admin() == admin
    with brownie.reverts():
        voting_escrow_proxy.commit_transfer_ownership(
            brownie.ZERO_ADDRESS, {"from": admin}
        )


def test_rescue_token_only_operator(
    fn_isolation, voting_escrow_factory, curve_token, voting_escrow_proxy, alice
):
    curve_token.transfer(voting_escrow_proxy, 1e20, {"from": voting_escrow_factory})
    with brownie.reverts():
        voting_escrow_proxy.rescue_token(alice, 1e20, curve_token, {"from": alice})


def test_rescue_token_not_to_zero_address(
    fn_isolation, voting_escrow_factory, curve_token, voting_escrow_proxy, operator
):
    curve_token.transfer(voting_escrow_proxy, 1e20, {"from": voting_escrow_factory})
    with brownie.reverts():
        voting_escrow_proxy.rescue_token(
            brownie.ZERO_ADDRESS, 1e20, curve_token, {"from": operator}
        )


def test_rescue_token(
    fn_isolation,
    voting_escrow_factory,
    voting_escrow_proxy,
    curve_token,
    operator,
    alice,
):
    curve_token.transfer(voting_escrow_proxy, 1e20, {"from": voting_escrow_factory})
    operator_previous_balance = curve_token.balanceOf(operator)
    voting_escrow_proxy.rescue_token(operator, 1e20, curve_token, {"from": operator})
    assert curve_token.balanceOf(operator) == operator_previous_balance + 1e20
