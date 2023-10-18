import json
import os
import warnings

import requests
from brownie import Contract, accounts, chain, vest_proxy

warnings.filterwarnings("ignore")

def main():
	treasury = Contract.from_explorer('0xe3997288987E6297Ad550A69B31439504F513267')
	CRV = Contract.from_explorer('0xD533a949740bb3306d119CC777fa900bA034cd52')
	admin = accounts.at('0x40907540d8a6C65c637785e8f8B742ae6b0b9968', force=True)

	proxy = vest_proxy.deploy(admin, accounts[0], CRV, {'from': admin})
	
	tx = treasury.deploy_vesting_contract(CRV, proxy, 100e18, True, 31536000, {'from': admin})
	vest = Contract.from_explorer(tx.new_contracts[0])

	return vest, proxy 

def claim(vest, proxy):
	chain.sleep(15000000)
	chain.mine()
	proxy.claim(vest, {'from': accounts[0]})
	balance = CRV.balanceOf(accounts[0]) / 1e18
	print(f"\nOperator ha {balance} CRV")