"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256    # Holds 256 bytes of memory 
        self.reg = [0] * 8  # Holds 8 general-purpose registers
        self.pc = 0 # Program Counter, address of the currently executing instruction
        self.ldi = 0b10000010
        self.prn = 0b01000111
        self.hlt = 0b00000001
        self.mul = 0b10100010
        self.add = 0b10100000
        self.push = 0b01000101
        self.pop = 0b01000110
        self.call = 0b01010000
        self.ret = 0b00010001
        self.running = True
        self.branchtable = {
            self.ldi: self.handle_load_immediate,
            self.prn: self.handle_print,
            self.hlt: self.handle_halt,
            self.mul: self.handle_multiply,
            self.push: self.handle_push,
            self.pop: self.handle_pop,
            self.call: self.handle_call,
            self.ret: self.handle_return,
            self.add: self.handle_add
        }
        self.sp = 7 # Stack Pointer
        self.reg[self.sp] = 0xFF # Used to keep register values between 0-255
        

        
    def load(self, file):
        """Load a program into memory."""

        address = 0
        
        program = open(file, "r")
        
        for line in program:
            line = line.split("#")
            line = line[0].strip()
            if line == "":
                continue
            self.ram[address] = int(line, 2)
            address += 1
            
    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "DIV":
            self.reg[reg_a] /= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()
        
    def ram_read(self, mar):
        # Memory Address Register (MAR): holds the memory address we're reading or writing
        return self.ram[mar]
    
    def ram_write(self, mar, mdr):
        # Memory Data Register (mdr), holds the value to write or the value just read
        self.ram[mar] = mdr

    def handle_load_immediate(self):
        # Handles intructions
        operand_a = self.ram_read(self.pc+1)
        operand_b = self.ram_read(self.pc+2)
        self.reg[operand_a] = operand_b
        self.pc += 3
        
    def handle_print(self):
        # Handles print
        operand_a = self.ram_read(self.pc+1)
        print(self.reg[operand_a])
        self.pc += 2
    
    def handle_halt(self):
        # Stops program
        self.running = False
        
    def handle_multiply(self):
        # Multiplies
        operand_a = self.ram_read(self.pc+1)
        operand_b = self.ram_read(self.pc+2)
        self.alu("MUL", operand_a, operand_b)
        
        self.pc += 3
        
    def handle_add(self):
        operand_a = self.ram_read(self.pc+1)
        operand_b = self.ram_read(self.pc+2)
        self.alu("ADD", operand_a, operand_b)
        
        self.pc += 3
        
    def handle_push(self):
        # Decrement stack pointer
        self.reg[self.sp] -= 1
        
        # Copies value from register into memory
        reg_num = self.ram[self.pc+1]
        value = self.reg[reg_num] # Being pushed
        
        address = self.reg[self.sp]
        
        # Stores the value on the stack
        self.ram[address] = value
        
        self.pc += 2
        
    def handle_pop(self):
        address = self.reg[self.sp]
        value = self.ram[address]
        
        # Copies value from memory into register
        reg_num = self.ram[self.pc+1]
        self.reg[reg_num] = value # Being popped off of stack
        
        # Increment stack pointer
        self.reg[self.sp] += 1
        
        self.pc += 2
        
    def handle_call(self):
        # Computes return address
        return_address = self.pc+2
        
        # Pushes to stack
        self.reg[self.sp] -= 1
        self.ram[self.reg[self.sp]] = return_address
        
        # Sets program counter to the value in the given register
        register_number = self.ram[self.pc+1]
        destination_address = self.reg[register_number]
        
        self.pc = destination_address
        
        print("REG", self.reg)
        print("RAM", self.ram)
        print("SP", self.sp)
        print("Return address", return_address)
        print("register_number", register_number)
        print("destination_address", destination_address)
    
    def handle_return(self):
        # Pop returns address from top of stack
        return_address = self.ram[self.reg[self.pc]]
        print("return",return_address)
        self.reg[self.sp] += 1
        
        # Sets program counter
        self.pc = return_address
        
        print("REG", self.reg)
        print("RAM", self.ram)
        print("SP", self.sp)
        print("Return address", return_address)
        # print("register_number", register_number)
        # print("destination_address", destination_address)
        
    def run(self):
        """Run the CPU."""

        while self.running:
            # Instruction Register
            ir = self.ram_read(self.pc)
            
            if self.branchtable.get(ir):
                self.branchtable[ir]()
            else:
                print("Unknown instructions")
                sys.exit(1)
        
            #self.trace()