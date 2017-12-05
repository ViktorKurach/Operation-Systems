processes = [
    {"id": "P1", "data": "aaaaaaaaaaaaaaaaaaaaa"},
    {"id": "P2", "data": "bbbbbbbbbb"},
    {"id": "P3", "data": "ccccccccccccccccccccccccccccccccccccccc"}
]
memory = ""
max_mem_size = 160
memory_table = [{"start": 0, "length": 0, "process": ""}]


def init_memory():
    global memory_table
    global memory
    memory_table = []
    p_address = 0
    for p in processes:
        memory += p["data"]
        memory_table.append({"start": p_address, "length": len(p["data"]), "process": p["id"]})
        p_address += len(p["data"])


def show_memory_map():
    for i in range(0, len(memory)):
        if i % 16 == 0:
            print("\n%04X\t|" % i, end="")
        if i % 4 == 0:
            print(" ", end="")
        if not memory[i]:
            print("0", end="")
        else:
            print("%s" % memory[i], end="")
    print("\n")


def show_memory_table():
    print("Start\tLength\tProcess")
    for d in memory_table:
        print("%X\t%d\t%s" % (d["start"], d["length"], d["process"]))
    print()


def launch_process(process_id, process_data):
    global memory
    global memory_table
    if process_data == "" or process_id == "" or len(memory) + len(process_data) > max_mem_size:
        return 1
    p_address = len(memory)
    memory += process_data
    memory_table.append({"start": p_address, "length": len(process_data), "process": process_id})
    return 0


def launch_new_process_interface():
    print("Process id: ", end="")
    process_id = input()
    print("Process data: ", end="")
    process_data = input()
    res = launch_process(process_id, process_data)
    if res != 0:
        print("Failed to launch process")
    else:
        print("Process %s launched" % process_id)
    print()


def edit_process(process_id, new_data):
    global memory
    global memory_table
    for p in memory_table:
        if p["process"] == process_id:
            p_length = p["length"]
            p_start = p["start"]
            if len(new_data) > p_length:
                return 1, len(new_data) - p_length
            memory = memory[0:p_start] + new_data + "~"*(p_length-len(new_data)) + memory[p_start + p_length:]
            return 0, p_length - len(new_data)
    return 2, None


def edit_process_interface():
    print("Process id: ", end="")
    process_id = input()
    print("New process data: ", end="")
    new_data = input()
    res, space = edit_process(process_id, new_data)
    if res == 0:
        print("Process %s edited, %d free space in the section" % (process_id, space))
    elif res == 1:
        print("Not enough space in the section: %d more required" % space)
    else:
        print("Failed to edit process %s" % process_id)
    print()


def read_from_process(process_id, address):
    try:
        for p in memory_table:
            if p["process"] == process_id and 0 <= int(address) <= p["length"] - 1:
                return memory[p["start"] + int(address)]
        return ""
    except ValueError:
        return ""


def read_from_process_interface():
    print("Process id: ", end="")
    process_id = input()
    print("Address in process: ", end="")
    address = input()
    res = read_from_process(process_id, address)
    if res == "":
        print("Failed to read from process %s" % process_id)
    else:
        print(res)
    print()


def write_to_process(process_id, address, value):
    global memory
    try:
        for p in memory_table:
            if p["process"] == process_id and 0 <= (int(address)) <= p["length"] - 1:
                abs_address = p["start"] + int(address)
                memory = memory[0:abs_address] + value[0] + memory[abs_address+1:]
                return 0
        return 1
    except ValueError:
        return 1


def write_to_process_interface():
    print("Process id: ", end="")
    process_id = input()
    print("Address in process: ", end="")
    address = input()
    print("Value: ", end="")
    value = input()
    res = write_to_process(process_id, address, value)
    if res != 0:
        print("Failed to write to process %s" % process_id)
    else:
        print("Wrote successfully")
    print()


def show_menu():
    print("1. Show memory map")
    print("2. Show memory table")
    print("3. Launch new process")
    print("4. Edit process")
    print("5. Read from process")
    print("6. Write to process")
    print("0. Exit")


init_memory()
while True:
    show_menu()
    ch = input()
    while ch not in ["0", "1", "2", "3", "4", "5", "6"]:
        ch = input()
    if ch == "0":
        break
    elif ch == "1":
        show_memory_map()
    elif ch == "2":
        show_memory_table()
    elif ch == "3":
        launch_new_process_interface()
    elif ch == "4":
        edit_process_interface()
    elif ch == "5":
        read_from_process_interface()
    elif ch == "6":
        write_to_process_interface()
