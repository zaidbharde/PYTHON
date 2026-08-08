class VendingState:
    def insert_coin(self, machine): pass
    def select_item(self, machine): pass
    def dispense(self, machine): pass

class IdleState(VendingState):
    def insert_coin(self, machine):
        print("Coin inserted")
        machine.state = HasCoinState()
    def select_item(self, machine):
        print("Insert coin first")

class HasCoinState(VendingState):
    def insert_coin(self, machine):
        print("Coin already inserted")
    def select_item(self, machine):
        print("Item selected")
        machine.state = DispensingState()
        machine.dispense()

class DispensingState(VendingState):
    def dispense(self, machine):
        print("Dispensing item...")
        machine.state = IdleState()

class VendingMachine:
    def __init__(self):
        self.state = IdleState()

    def insert_coin(self):
        self.state.insert_coin(self)

    def select_item(self):
        self.state.select_item(self)

    def dispense(self):
        self.state.dispense(self)


if __name__ == "__main__":
    vm = VendingMachine()
    vm.select_item()   # blocked, no coin
    vm.insert_coin()
    vm.select_item()   # dispenses
