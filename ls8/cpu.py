"""CPU functionality."""

import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
ADD = 0b10100000
CMP = 0b10100111
JMP = 0b01010100
JNE = 0b01010110
JEQ = 0b01010101


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # memory bytes
        self.ram = [0] * 256
        # 8 general purpose geisters
        self.reg = [0] * 8
        # internal register counter
        self.pc = 0

        # later will set the initial value of the stack pointer
        self.sp = 7
        # branch table attampt
        # flag does it need to be binary? Check later.
        self.flag = 0b00000100

        self.branchtable = {}
        self.branchtable[HLT] = self.hlt
        self.branchtable[LDI] = self.ldi
        self.branchtable[PRN] = self.prn
        self.branchtable[MUL] = self.mul
        self.branchtable[PUSH] = self.push
        self.branchtable[POP] = self.pop
        self.branchtable[CALL] = self.call
        self.branchtable[RET] = self.ret
        self.branchtable[ADD] = self.add
        self.branchtable[CMP] = self.cmp_fun
        self.branchtable[JMP] = self.jmp
        self.branchtable[JNE] = self.jne
        self.branchtable[JEQ] = self.jeq

    def load(self):
        """Load a program into memory."""

        address = 0
        if len(sys.argv) != 2:
            print("usage: comp.py filename")
            sys.exit(1)

        try:
            with open(sys.argv[1]) as f:
                for line in f:
                    try:
                        line = line.strip()
                        line = line.split("#", 1)[0]
                        line = int(line, 2)  # base 2 because its binary
                        self.ram[address] = line
                        address += 1
                    except ValueError:
                        pass
        except FileNotFoundError:
            print(f"Couldn't find file {sys.argv[1]}")
            sys.exit(1)

        # # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010,  # LDI R0,8 128->dec
        #     0b00000000,
        #     0b00001000,
        #     0b01000111,  # PRN R0
        #     0b00000000,
        #     0b00000001,  # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        # elif op == "SUB": etc
        elif op == "CMP":
            if self.reg[reg_a] < self.reg[reg_b]:
                self.flag = 0b00000100  # L1
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.flag = 0b00000010  # G1
            #                 `FL` bits: `00000LGE`
            else:
                self.flag = 0b00000001  # E1

        # * `L` Less-than: during a `CMP`, set to 1 if registerA is less than registerB,
        #   zero otherwise.
        # * `G` Greater-than: during a `CMP`, set to 1 if registerA is greater than
        #   registerB, zero otherwise.
        # * `E` Equal: during a `CMP`, set to 1 if registerA is equal to registerB, zero
        #   otherwise.
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

    def ram_read(self, MAR):
        # accept the address to read and return the value stored
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        # accept a value to write, an address to write to
        # MAR is the memory address register, MDR is the memory data register
        # write the value -> MDR to the address MAR
        self.ram[MAR] = MDR

    def hlt(self):
        # stop the program by calling it in the run function
        self.running = False

    def ldi(self):
        #### LDI
        # `LDI register immediate`
        # Set the value of a register to an integer.
        # Machine code:
        # ```
        # 10000010 00000rrr iiiiiiii
        # 82 0r ii
        # ```
        # 0b10000010,  # LDI R0,8 128->dec

        # sets a specific register to a specified value
        # print("LDI")
        # self.trace()
        operand_a = self.ram[self.pc + 1]
        operand_b = self.ram[self.pc + 2]
        self.reg[operand_a] = operand_b
        self.pc += 3
        # self.trace()

    def prn(self):
        opperand_a = self.ram[self.pc + 1]
        print(self.reg[opperand_a])
        self.pc += 2

    def add(self):
        opperand_a = self.ram[self.pc + 1]
        opperand_b = self.ram[self.pc + 2]
        self.alu("ADD", opperand_a, opperand_a)
        self.pc += 3

    def mul(self):
        operand_a = self.ram[self.pc + 1]
        operand_b = self.ram[self.pc + 2]
        self.alu("MUL", operand_a, operand_b)
        self.pc += 3

    def push(self):
        # print("pushing")
        # self.trace()
        # decrement the stack pointer\
        self.reg[self.sp] -= 1

        reg_num = self.ram[self.pc + 1]
        value = self.reg[reg_num]
        # print(value)
        address_to_push_to = self.reg[self.sp]
        self.ram[address_to_push_to] = value

        self.pc += 2
        # copy the value in the given register to the address pointed to by the sp
        # self.trace()

    def pop(self):
        # print("popping")
        # pop into registers, pop whatever is at top of stack to R0
        # copy the value from the address point to by the sp
        # increment the sp
        # self.trace()
        address_to_pop_from = self.reg[self.sp]
        value = self.ram[address_to_pop_from]

        reg_num = self.ram[self.pc + 1]
        self.reg[reg_num] = value

        self.reg[self.sp] += 1
        self.pc += 2
        # self.trace()

    def call(self):
        # get the address of the next instruction
        # print("CALL:")
        # self.trace()
        return_address = self.pc + 2
        # push that onto the stack
        self.reg[self.sp] -= 1
        address_to_push_to = self.reg[self.sp]
        self.ram[address_to_push_to] = return_address

        # set the PC to the subroutine address
        register_number = self.ram[self.pc + 1]
        subroutine_address = self.reg[register_number]

        self.pc = subroutine_address
        # print("endCALL")
        # self.trace()

    def ret(self):
        # get return address from the top of the stack
        # print("RET:")
        # self.trace()
        address_to_pop_from = self.reg[self.sp]
        return_address = self.ram[address_to_pop_from]
        self.reg[self.sp] += 1

        # set the PC to the return addresss
        self.pc = return_address

    def cmp_fun(self):
        # cmp:
        # This is an instruction handled by the ALU.*
        # print("CMP:")
        # self.trace()
        operand_a = self.ram[self.pc + 1]
        operand_b = self.ram[self.pc + 2]
        self.alu("CMP", operand_a, operand_b)
        self.pc += 3
        # self.trace()

    def jmp(self):
        self.trace()
        self.pc += 1
        given_reg = self.ram[self.pc]
        jump = self.reg[given_reg]
        self.pc = jump

    # jump to the address stored in the given reg.
    # set the pc to the address stored in the given reg

    def jne(self):
        self.pc += 1
        given_reg = self.ram[self.pc]
        jump_add = self.reg[given_reg]
        if self.flag != 0b00000001:
            self.pc = jump_add
        else:
            self.pc += 1

    # if equal flag is clear (false, 0), jump to the address stored in the given reg

    def jeq(self):
        self.pc += 1
        given_reg = self.ram[self.pc]
        jump_add = self.reg[given_reg]
        if self.flag == 0b00000001:
            self.pc = jump_add
        else:
            self.pc += 1

    # if equal flag is set true, jump to the address stored in the given reg

    def run(self):
        """Run the CPU."""
        self.running = True
        while self.running:
            # needs to read the emmeory address thats stored in the regester PC
            # store the result in the IR

            ir = self.pc
            inst = self.ram[ir]
            self.branchtable[inst]()
            # if else chain to deal with the program
            # if inst == LDI:
            #     self.ldi()
            # elif inst == HLT:
            #     self.hlt()
            # elif inst == PRN:
            #     self.prn()
            # elif inst == MUL:
            #     self.mul()

