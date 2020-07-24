"""CPU functionality."""
import sys

SP = 7


class CPUCOPY:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.pc = 0
        self.reg = [0] * 8
        self.ram = [0] * 256
        self.branch_table = {
            0b00000001: self.HLT,
            0b10000010: self.LDI,
            0b01000111: self.PRN,
            0b10100010: self.MUL,
            0b10100000: self.ADD,
            0b01000101: self.PUSH,
            0b01000110: self.POP,
            0b00010001: self.RET,
            0b01010000: self.CALL,
        }

    def ram_read(self, mar):
        # mar is the address being read
        return self.ram[mar]

    def ram_write(self, mdr, mar):
        # mdr is the data being written
        self.ram[mar] = mdr

    def push_value(self, value):
        self.reg[SP] -= 1
        self.ram_write(value, self.reg[SP])

    def pop_value(self):
        value = self.ram_read(self.reg[SP])
        self.reg[SP] += 1
        return value

    def load(self, filename):
        """Load a program into memory."""
        address = 0
        with open(filename) as f:
            for line in f:
                line = line.split("#")
                try:
                    v = int(line[0], 2)
                except ValueError:
                    continue
                self.ram[address] = v
                address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """
        print(
            f"TRACE: %02X | %02X %02X %02X |"
            % (
                self.pc,
                # self.fl,
                # self.ie,
                self.ram_read(self.pc),
                self.ram_read(self.pc + 1),
                self.ram_read(self.pc + 2),
            ),
            end="",
        )
        for i in range(8):
            print(" %02X" % self.reg[i], end="")
        print()

    def HLT(self, operand_a, operand_b):
        sys.exit()

    def LDI(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b
        self.pc += 3

    def PRN(self, operand_a, operand_b):
        print(self.reg[operand_a])
        self.pc += 2

    def ADD(self, operand_a, operand_b):
        self.reg[operand_a] += self.reg[operand_b]
        self.pc += 3

    def MUL(self, operand_a, operand_b):
        self.reg[operand_a] *= self.reg[operand_b]
        self.pc += 3

    def PUSH(self, operand_a, operand_b):
        self.push_value(self.reg[operand_a])
        self.pc += 2

    def POP(self, operand_a, operand_b):
        self.reg[operand_a] = self.pop_value()
        self.pc += 2

    def CALL(self, operand_a, operand_b):
        self.push_value(self.pc + 2)
        self.pc = self.reg[operand_a]

    def RET(self, operand_a, operand_b):
        self.pc = self.pop_value()

    def run(self):
        """Run the CPU."""
        while True:
            # ir == Instruction Register
            ir = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            if ir in self.branch_table:
                self.branch_table[ir](operand_a, operand_b)
            else:
                print(f"Unknown instruction {ir} at address {self.pc}")
                sys.exit()
