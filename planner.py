BP1 = {"name": "BP1", "income": 0, "length": 8, "start": -1, "remain": 0, "estimate": -1}
BP2 = {"name": "BP2", "income": 2, "length": 5, "start": -1, "remain": 0, "estimate": -1}
BP3 = {"name": "BP3", "income": 4, "length": 10, "start": -1, "remain": 0, "estimate": -1}
BP4 = {"name": "BP4", "income": 5, "length": 7, "start": -1, "remain": 0, "estimate": -1}
IP1 = {"name": "IP1", "income": 0, "length": 12, "start": -1, "remain": 0, "estimate": -1}
IP2 = {"name": "IP2", "income": 1, "length": 15, "start": -1, "remain": 0, "estimate": -1}
IP3 = {"name": "IP3", "income": 3, "length": 8, "start": -1, "remain": 0, "estimate": -1}
IP4 = {"name": "IP4", "income": 6, "length": 14, "start": -1, "remain": 0, "estimate": -1}
IP5 = {"name": "IP5", "income": 7, "length": 10, "start": -1, "remain": 0, "estimate": -1}
background_processes = [BP1, BP2, BP3, BP4]
interactive_processes = [IP1, IP2, IP3, IP4, IP5]


def print_map_header(output=None):
    print("Time\t", end="", file=output)
    for x in interactive_processes:
        print("%s\t" % x["name"], end="", file=output)
    for x in background_processes:
        print("%s\t" % x["name"], end="", file=output)
    print(file=output)


def print_results(output=None):
    print("Process\tIncome\tLength\tStart\tEstimate\tDelay\tFull time\n", file=output)
    average_delay_background = 0
    average_full_time_background = 0
    for x in background_processes:
        print("%s\t%d\t%d\t%d\t%d\t\t%d\t%d" %
              (x["name"], x["income"], x["length"], x["start"], x["estimate"],
               x["estimate"] - x["start"] - x["length"], x["estimate"] - x["start"]),
              file=output)
        average_delay_background += x["estimate"] - x["start"] - x["length"]
        average_full_time_background += x["estimate"] - x["start"]
    average_delay_background /= len(background_processes)
    average_full_time_background /= len(background_processes)
    average_delay_interactive = 0
    average_full_time_interactive = 0
    for x in interactive_processes:
        print("%s\t%d\t%d\t%d\t%d\t\t%d\t%d" %
              (x["name"], x["income"], x["length"], x["start"], x["estimate"],
               x["estimate"] - x["start"] - x["length"], x["estimate"] - x["start"]),
              file=output)
        average_delay_interactive += x["estimate"] - x["start"] - x["length"]
        average_full_time_interactive += x["estimate"] - x["start"]
    average_delay_interactive /= len(interactive_processes)
    average_full_time_interactive /= len(interactive_processes)
    print("\nBackground processes average delay: %d" % average_delay_background, file=output)
    print("Background processes average full time: %d\n" % average_full_time_background, file=output)
    print("Interactive processes average delay: %d" % average_delay_interactive, file=output)
    print("Interactive processes average full time: %d\n" % average_full_time_interactive, file=output)


def logging(process_name, time, output=None):
    if process_name[0] == "I":
        print("%s\t%s*" % (str(time), "\t" * (int(process_name[2]) - 1)), file=output)
    elif process_name[0] == "B":
        print("%s\t%s*" % (str(time), "\t" * (int(process_name[2]) + 4)), file=output)


def check_for_new_process(processes, queue, time):
    for x in processes:
        if x["income"] <= time and x["start"] == -1:
            queue.append(x)
            x["start"] = time
    return queue


def remove_estimated(queue, active_process):
    if active_process["remain"] <= 0:
        queue.remove(active_process)
        return None
    return active_process


def choose_active_for_srtf(queue, active_process):
    for x in queue:
        if not active_process or x["remain"] <= active_process["remain"]:
            active_process = x
    return active_process


def choose_active_for_rr(queue, active_process):
    if not active_process or active_process == queue[len(queue) - 1]:
        return queue[0]
    return queue[queue.index(active_process) + 1]


def change_current_time(active_process, time, n):
    time += n
    active_process["remain"] -= n
    if active_process["remain"] == 0:
        active_process["estimate"] = time
    return time, active_process["remain"]


def change_time_bounds(current_time, time_bound):
    start = current_time
    while time_bound % 10 != 8:
        time_bound += 1
    if start == time_bound:
        time_bound += 10
    return start, time_bound


def srtf_planner(processes, queue, start, time_bound, output=None):
    if not (start > 8 and not queue):
        time = start
        active_process, old_active_process = None, None
        while time < time_bound or old_active_process == active_process:
            queue = check_for_new_process(processes, queue, time)
            active = choose_active_for_srtf(queue, active_process)
            if time == time_bound and old_active_process != active or not queue:
                break
            logging(active["name"], time, output=output)
            time, active["remain"] = change_current_time(active, time, 1)
            old_active_process = active
            active_process = remove_estimated(queue, active)
        start, time_bound = change_time_bounds(time, time_bound)
    return queue, start, time_bound


def rr_planner(processes, queue, start, time_bound, active_rr_process, time_quantum=1, output=None):
    if not (start > 0 and not queue):
        time = start
        while time < time_bound:
            queue = check_for_new_process(processes, queue, time)
            active_process = choose_active_for_rr(queue, active_rr_process)
            logging(active_process["name"], time, output=output)
            time, active_process["remain"] = change_current_time(active_process, time, time_quantum)
            active_rr_process = remove_estimated(queue, active_process)
            if not queue:
                break
    start, bound = time_bound, time_bound + 2
    return queue, start, bound, active_rr_process


def general_planner(output=None):
    time, start, bound = 0, 0, 8
    back_queue, inter_queue, active_rr = [], [], None
    for x in background_processes + interactive_processes:
        x["remain"] = x["length"]
    while True:
        inter_queue, start, bound, active_rr = \
            rr_planner(interactive_processes, inter_queue, start, bound, active_rr, output=output)
        back_queue, start, bound = \
            srtf_planner(background_processes, back_queue, start, bound, output=output)
        if not back_queue and not inter_queue:
            break


if __name__ == "__main__":
    f = open("map.txt", "w")
    print_map_header(output=f)
    general_planner(output=f)
    f.close()
    g = open("result.txt", "w")
    print_results(g)
    g.close()

