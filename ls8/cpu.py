"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.branchtable = {}
        self.branchtable[0b00000001] = self.handle_HLT
        self.branchtable[0b10000010] = self.handle_LDI
        self.branchtable[0b01000111] = self.handle_PRN
        self.branchtable[0b10100010] = self.handle_MUL
        self.branchtable[0b10100011] = self.handle_DIV
        self.branchtable[0b10100000] = self.handle_ADD
        self.branchtable[0b10100001] = self.handle_SUB
        self.branchtable[0b01100101] = self.handle_INC
        self.branchtable[0b01100110] = self.handle_DEC
        self.branchtable[0b01000101] = self.handle_PUSH
        self.branchtable[0b01000110] = self.handle_POP
        self.branchtable[0b01010000] = self.handle_CALL
        self.branchtable[0b00010001] = self.handle_RET

    def load(self):
        """Load a program into memory."""

        address = 0

        filename = 'examples/' + sys.argv[1] + '.ls8'

        file = open(filename, 'r')
        program = []

        for line in file:
            if not line[0] == '#' and not len(line.strip()) == 0:
                program.append(int(line.strip()[:8], 2))

        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == 'MUL':
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "DIV":
            self.reg[reg_a] /= self.reg[reg_b]
        elif op == "INC":
            self.reg[reg_a] += 1
        elif op == "DEC":
            self.reg[reg_a] -= 1
        else:
            raise Exception("Unsupported ALU operation")

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, address, value):
        self.ram[address] = value

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def handle_HLT(self):
        sys.exit()

    def handle_LDI(self):
        reg_address = self.ram[self.pc + 1]
        value = self.ram[self.pc + 2]
        self.reg[reg_address] = value
    
    def handle_PRN(self):
        reg_address = self.ram[self.pc + 1]
        print(self.reg[reg_address])
    
    def handle_ADD(self):
        reg_address_a = self.ram[self.pc + 1]
        reg_address_b = self.ram[self.pc + 2]
        self.alu('ADD', reg_address_a, reg_address_b )

    def handle_SUB(self):
        reg_address_a = self.ram[self.pc + 1]
        reg_address_b = self.ram[self.pc + 2]
        self.alu('SUB', reg_address_a, reg_address_b )

    def handle_MUL(self):
        reg_address_a = self.ram[self.pc + 1]
        reg_address_b = self.ram[self.pc + 2]
        self.alu('MUL', reg_address_a, reg_address_b )
    
    def handle_DIV(self):
        reg_address_a = self.ram[self.pc + 1]
        reg_address_b = self.ram[self.pc + 2]
        self.alu('DIV', reg_address_a, reg_address_b )
    
    def handle_INC(self):
        reg_address_a = self.ram[self.pc + 1]
        self.alu('INC', reg_address_a)

    def handle_DEC(self):
        reg_address_a = self.ram[self.pc + 1]
        self.alu('DEC', reg_address_a)

    def handle_PUSH(self):
        self.reg[7] -= 1
        reg_address = self.ram[self.pc + 1]
        value = self.reg[reg_address]
        self.ram[self.reg[7]] = value

    def handle_POP(self):
        value = self.ram[self.reg[7]]
        reg_address = self.ram[self.pc +1]
        self.ram[reg_address] = value
        self.reg[7] += 1
        
    def handle_CALL(self):
        #address of instruction after call is pushed onto stack
        self.reg[7] -= 1
        return_address = self.ram[self.pc + 2]
        self.ram[self.reg[7]] = return_address

        #set pc to call operand
        reg_number = self.ram[self.pc + 1]
        destination = self.reg[reg_number]

        pc = destination - 1

    def handle_RET(self):
        return_address = self.ram[self.reg[7]]
        self.reg[7] += 1

        self.pc = return_address - 1
        
    def run(self):
        """Run the CPU."""
        self.reg[7] = 0xF4

        while True:
            # grab from memory - an instruction register
            mem = self.ram[self.pc]
            increment = ((mem & 0b11000000) >> 6 ) + 1

            if mem in self.branchtable:
                self.branchtable[mem]()
            else:
                print(f'Intruction {mem} unknown')

            self.pc += increment
