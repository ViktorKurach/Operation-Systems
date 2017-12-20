n_max = 65536

hard_disc = ["ID", "$"]
files = [{"name": "", "init_cluster": "", "size": ""}]


def show_memory_map():
    print("\n")
    for i in range(0, len(hard_disc)):
        if i % 10 == 9:
            print("%s\n" % hard_disc[i], end="")
        else:
            print("%s\t" % hard_disc[i], end="")
    print("\n")


def show_existing_files():
    for file in files:
        print("%s: %s clusters starting from %s" % (file["name"], file["size"], file["init_cluster"]))
    print()


def find_free_cluster(disc, after):
    for i in range(0, len(disc)):
        if disc[i] == "0" and i > after:
            return i
    return len(disc)


def file_exists(name):
    for file in files:
        if file["name"] == name:
            return True
    return False


def get_file_size(name):
    for file in files:
        if file["name"] == name:
            return int(file["size"])
    return -1


def remember_new_file_size(file_name, new_size):
    for file in files:
        if file["name"] == file_name:
            file["size"] = new_size


def get_init_cluster(file_name):
    for file in files:
        if file["name"] == file_name:
            return int(file["init_cluster"])
    return -1


def get_last_cluster(file_name):
    cluster_index = get_init_cluster(file_name)
    while hard_disc[cluster_index] != "$":
        cluster_index = int(hard_disc[cluster_index])
    return cluster_index


def get_new_last_cluster(file_name, new_size):
    cluster_index = get_init_cluster(file_name)
    for i in range(0, new_size - 1):
        cluster_index = int(hard_disc[cluster_index])
    return cluster_index


def create_large_file(size, init_cluster):
    global hard_disc
    new_hard_disc = hard_disc.copy()
    cluster_index = init_cluster
    for i in range(0, int(size)):
        next_cluster_index = find_free_cluster(new_hard_disc, cluster_index)
        if i == int(size) - 1:
            new_hard_disc[cluster_index] = "$"
        elif next_cluster_index == len(new_hard_disc):
            return 2
        else:
            new_hard_disc[cluster_index] = str(next_cluster_index)
        cluster_index = next_cluster_index
    hard_disc = new_hard_disc.copy()
    return 0


def create_file(name, size):
    try:
        if name == "" or size == 0:
            return 1
        if file_exists(name):
            return 3
        cluster_index = find_free_cluster(hard_disc, 0)
        file = {"name": name, "size": size, "init_cluster": str(cluster_index)}
        if int(size) == 1 and cluster_index != len(hard_disc):
            hard_disc[cluster_index] = "$"
        else:
            res = create_large_file(size, cluster_index)
            if res != 0:
                return res
        files.append(file)
        return 0
    except ValueError:
        return 1


def create_file_interface():
    print("File name: ", end="")
    name = input()
    print("File size: ", end="")
    size = input()
    res = create_file(name, size)
    if res == 0:
        print("File created\n")
    elif res == 1:
        print("No file name or file size in not integer\n")
    elif res == 2:
        print("Creation failed: not enough memory\n")
    elif res == 3:
        print("File already exists\n")
    else:
        print("Unknown error\n")


def extend_file(last_cluster, size, new_size):
    global hard_disc
    new_hard_disc = hard_disc.copy()
    for i in range(0, new_size - size + 1):
        if i == 0:
            next_cluster = find_free_cluster(new_hard_disc, 0)
        else:
            next_cluster = find_free_cluster(new_hard_disc, last_cluster)
        if i == new_size - size:
            new_hard_disc[last_cluster] = "$"
        elif next_cluster == len(new_hard_disc):
            return 3
        else:
            new_hard_disc[last_cluster] = str(next_cluster)
        last_cluster = next_cluster
    hard_disc = new_hard_disc.copy()
    return 0


def reduce_file(last_cluster, size, new_size):
    global hard_disc
    new_hard_disc = hard_disc.copy()
    for i in range(0, size - new_size + 1):
        if i != size - new_size:
            next_cluster = int(new_hard_disc[last_cluster])
        if i == 0:
            new_hard_disc[last_cluster] = "$"
        else:
            new_hard_disc[last_cluster] = "0"
        last_cluster = next_cluster
    hard_disc = new_hard_disc.copy()
    return 0


def change_file_size(name, new_size):
    try:
        size = get_file_size(name)
        if size == -1:
            return 2
        last_cluster = get_last_cluster(name)
        if last_cluster == -1:
            return 2
        res = 0
        if int(new_size) - size > 0:
            res = extend_file(last_cluster, size, int(new_size))
        if int(new_size) - size < 0:
            new_last_cluster = get_new_last_cluster(name, int(new_size))
            res = reduce_file(new_last_cluster, size, int(new_size))
        if res != 0:
            return res
        remember_new_file_size(name, new_size)
        return 0
    except ValueError:
        return 1


def change_file_size_interface():
    print("File name: ", end="")
    name = input()
    print("New size: ", end="")
    new_size = input()
    res = change_file_size(name, new_size)
    if res == 0:
        print("Size of %s changed to %s\n" % (name, new_size))
    elif res == 1:
        print("No file name or file size in not integer\n")
    elif res == 2:
        print("No file found\n")
    elif res == 3:
        print("Operation failed: not enough memory\n")


def show_menu():
    print("1. Show memory map\n\
2. Show existing files\n\
3. Create new file\n\
4. Change file size\n\
0. Exit")


def init_memory():
    global hard_disc
    global files
    files = []
    for i in range(0, 100 - 2):
        hard_disc.append("0")


init_memory()
while True:
    show_menu()
    ch = input()
    while ch not in ["0", "1", "2", "3", "4"]:
        ch = input()
    if ch == "1":
        show_memory_map()
    elif ch == "2":
        show_existing_files()
    elif ch == "3":
        create_file_interface()
    elif ch == "4":
        change_file_size_interface()
    elif ch == "0":
        break
