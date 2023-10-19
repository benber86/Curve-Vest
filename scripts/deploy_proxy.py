import json
import os
import warnings

import requests
from brownie import Contract, accounts, chain, vest_proxy

warnings.filterwarnings("ignore")

def main():
	# The Curve Community Fund that deploys VestingEscrowSimple
	vest_factory = Contract.from_explorer('0xe3997288987E6297Ad550A69B31439504F513267')
	# The CRV token contract
	CRV = Contract.from_explorer('0xD533a949740bb3306d119CC777fa900bA034cd52')
	# DAO address
	admin = accounts.at('0x40907540d8a6C65c637785e8f8B742ae6b0b9968', force=True)

	# Deploy our contract with admin = DAO and accounts[0] = operator
	proxy = vest_proxy.deploy(admin, accounts[0], CRV, {'from': admin})
	proxy = vest_proxy[0]

	# Deploy VestingEscrowSimple with arguments
	# token = CRV
	# recipient = proxy
	# amount = 100 CRV
	# can_disable = True
	# vest_duration = 1 year
	tx = vest_factory.deploy_vesting_contract(CRV, proxy, 100e18, True, 31536000, {'from': admin})
	
	# Assign vest_contract variable to newly created vest contract
	vest_contract = Contract.from_explorer(tx.new_contracts[0])

	return vest_contract, proxy 

# def claim(vest_contract, proxy):
# 	chain.sleep(15768000)
# 	chain.mine()
# 	proxy.claim(vest_contract, {'from': accounts[0]})
# 	balance = CRV.balanceOf(accounts[0]) / 1e18
# 	print(f"\nOperator ha {balance} CRV")