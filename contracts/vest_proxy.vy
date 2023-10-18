# @version 0.3.7
"""
@title Vest Proxy
@author Llama Risk
@notice Extends functionality of Curve community fund vests
"""

from vyper.interfaces import ERC20

interface VestingEscrowSimple:
    def claim(addr: address = msg.sender): payable
    def start_time() -> uint256: view
    def end_time() -> uint256: view
    def disabled_at(arg0: address) -> uint256: view
    def total_claimed(arg0: address) -> uint256: view
    def initial_locked(arg0: address) -> uint256: view


event ApplyOwnership:
    admin: address

event CommitOwnership:
	admin: address

event Claim:
	contract: address
	operator: address
	claimable: uint256

admin: public(address)
future_admin: public(address)
operator: public(address)
token: public(address)


@external
def __init__(_admin: address, _operator: address, _token: address):
	"""
	@notice Contract constructor
	@param _admin Contract admin
	@param _operator Address to receive vest
	@param _token ERC20 vest token
	"""
	self.admin = _admin
	self.operator = _operator
	self.token = _token


@external
def set_operator(_op: address):
	"""
	@notice Set the contract operator
    @param _op Address set as the operator
	"""

	assert msg.sender == self.admin # dev: admin only
	self.operator = _op


@internal
@view
def _total_vested_of(_contract: address, _time: uint256 = block.timestamp) -> uint256:
    start: uint256 = VestingEscrowSimple(_contract).start_time()
    end: uint256 = VestingEscrowSimple(_contract).end_time()
    locked: uint256 = VestingEscrowSimple(_contract).initial_locked(self)
    if _time < start:
        return 0
    return min(locked * (_time - start) / (end - start), locked)


@external
@nonreentrant('lock')
def claim(_contract: address):
	"""
	@notice Claim vested funds from vest contract to the operator
	@param _contract address of the vest contract
	"""

	assert msg.sender == self.operator # dev: operator only

	t: uint256 = VestingEscrowSimple(_contract).disabled_at(self)
	if t == 0:
		t = block.timestamp
	claimed: uint256 = VestingEscrowSimple(_contract).total_claimed(self)
	claimable: uint256 = self._total_vested_of(_contract, t) - claimed
	claimed += claimable

	VestingEscrowSimple(_contract).claim()

	assert ERC20(self.token).transfer(self.operator, claimable)
	
	log Claim(_contract, self.operator, claimable)


@external
def commit_transfer_ownership(addr: address) -> bool:
    """
    @notice Transfer ownership of VestProxy to 'addr'
    @param addr Address to have ownership transferred to
    """
    assert msg.sender == self.admin  # dev: admin only
    self.future_admin = addr
    log CommitOwnership(addr)

    return True


@external
def apply_transfer_ownership() -> bool:
    """
    @notice Apply pending ownership transfer
    """
    assert msg.sender == self.admin  # dev: admin only
    _admin: address = self.future_admin
    assert _admin != ZERO_ADDRESS  # dev: admin not set
    self.admin = _admin
    log ApplyOwnership(_admin)

    return True







    