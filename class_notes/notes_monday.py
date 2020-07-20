memory = [
    1,  # prints shiiiiiiit
    3,  # SAVE_REG R2, 99 -> register to save in, the value saved there
    2,  # R2
    99,  # 99
    4,  # print reg R2
    2,  # represents R2
    2,  # HALLLT
]
register = [0] * 8
pc = 0
running = True

while running:
    inst = memory[pc]
    if inst == 1:
        print("shiiiiiiit!")
        pc += 1
    elif inst == 2:
        running = False
    elif inst == 3:
        reg_num = memory[pc + 1]
        value = memory[pc + 2]
        register[reg_num] = value
        pc += 3
    elif inst == 4:
        reg_num = memory[pc + 1]
        print(register[reg_num])
        pc += 2
    else:
        print("this instruction is invalid")
