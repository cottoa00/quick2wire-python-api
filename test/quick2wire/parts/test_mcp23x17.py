

from quick2wire.parts.mcp23x17 import Registers, PinBanks, In, Out, IOCONA, IOCONB

class FakeRegisters(Registers):
    def __init__(self):
        self.registers = {}
        self.writes = []
        self.reset()
    
    def write_register(self, reg, value):
        self.writes.append((reg, value))
        self.registers[reg] = value
    
    def read_register(self, reg):
        return self.registers[reg]


class TestPinBanks:
    def setup_method(self, method):
        self.chip = PinBanks(FakeRegisters())
    
    def test_has_two_banks(self):
        assert len(self.chip.banks) == 2
        assert self.chip.banks[0] is not None
        assert self.chip.banks[1] is not None
    
    def test_both_banks_have_eight_pins(self):
        assert len(self.chip.banks[0]) == 8
        assert len(self.chip.banks[1]) == 8
    
    def test_can_use_a_context_manager_to_claim_ownership_of_a_pin_in_a_bank_and_release_it(self):
        with self.chip.banks[0][1] as pin:
            assert pin.bank == self.chip.banks[0]
            assert pin.index == 1
        
    def test_a_pin_can_only_be_claimed_once_at_any_time(self):
        with self.chip.banks[0][1] as pin:
            try :
                with self.chip.banks[0][1] as pin2:
                    raise AssertionError("claim_pin() should have failed")
            except ValueError as e:
                pass

    def test_a_pin_can_be_claimed_after_being_released(self):
        with self.chip.banks[0][1] as pin:
            pass
        
        with self.chip.banks[0][1] as pin_again:
            pass
    
    def test_after_reset_or_poweron_all_pins_are_input_pins(self):
        # Chip is reset in setup
        for p in all_pins(self.chip):
            assert p.direction == In
    
    def test_resets_iocon_before_other_registers(self):
        # Chip is reset in setup
        assert self.chip.registers.writes[0] == (IOCONA, 0)
        
    def test_only_resets_iocon_once_because_same_register_has_two_addresses(self):
        # Chip is reset in setup
        assert IOCONB not in [reg for (reg, value) in self.chip.registers.writes]

def all_pins(chip):
    for bank in 0,1:
        for pin in range(8):
            with chip.banks[bank][pin] as p:
                yield p
