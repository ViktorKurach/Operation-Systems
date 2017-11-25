import threading
from time import sleep

semaphore = threading.BoundedSemaphore()

# Common resource
bank = {"1": 50, "2": 25, "5": 20, "10": 15, "25": 10, "50": 5, "100": 0}

price_to_Kiev = 28
price_to_Moscow = 37
price_to_London = 50
price_to_Berlin = 77
price_to_Paris = 91

purchases = ["", "Kiev", "Paris", "", "", "London", "", "Berlin", "Moscow", "", "Berlin"]

# Common resources
rest = 0
rest_signal = False
stop_signal = False


def count_bank():
    res = 0
    for x in bank.keys():
        res += int(x) * bank[x]
    return str(res)


def get_ticket_price(city):
    if city == "Kiev":
        return price_to_Kiev
    if city == "Moscow":
        return price_to_Moscow
    if city == "Berlin":
        return price_to_Berlin
    if city == "Paris":
        return price_to_Paris
    if city == "London":
        return price_to_London


def count_rest(c1, c2, c5, c10, c25, c50):
    return c1 + c2 * 2 + c5 * 5 + c10 * 10 + c25 * 25 + c50 * 50


def gather_rest():
    c1, c2, c5, c10, c25, c50 = 0, 0, 0, 0, 0, 0
    while bank["50"] > 0 and count_rest(0, 0, 0, 0, 0, c50 + 1) <= rest:
        c50 += 1
        bank["50"] -= 1
    while bank["25"] > 0 and count_rest(0, 0, 0, 0, c25 + 1, c50) <= rest:
        c25 += 1
        bank["25"] -= 1
    while bank["10"] > 0 and count_rest(0, 0, 0, c10 + 1, c25, c50) <= rest:
        c10 += 1
        bank["10"] -= 1
    while bank["5"] > 0 and count_rest(0, 0, c5 + 1, c10, c25, c50) <= rest:
        c5 += 1
        bank["5"] -= 1
    while bank["2"] > 0 and count_rest(0, c2 + 1, c5, c10, c25, c50) <= rest:
        c2 += 1
        bank["2"] -= 1
    while bank["1"] > 0 and count_rest(c1 + 1, c2, c5, c10, c25, c50) <= rest:
        c1 += 1
        bank["1"] -= 1
    return c1, c2, c5, c10, c25, c50


def give_money_back(c1, c2, c5, c10, c25, c50):
    bank["100"] -= 1
    bank["50"] += c50
    bank["25"] += c25
    bank["10"] += c10
    bank["5"] += c5
    bank["2"] += c2
    bank["1"] += c1


def get_rest_string(c1, c2, c5, c10, c25, c50):
    rest_string = str(count_rest(c1, c2, c5, c10, c25, c50)) + " ( "
    if c50 > 0:
        rest_string += str(c50) + "*50 "
    if c25 > 0:
        rest_string += str(c25) + "*25 "
    if c10 > 0:
        rest_string += str(c10) + "*10 "
    if c5 > 0:
        rest_string += str(c5) + "*5 "
    if c2 > 0:
        rest_string += str(c2) + "*2 "
    if c1 > 0:
        rest_string += str(c1) + "*1 "
    return rest_string + ")"


def sell_ticket():
    time = 0
    global rest
    global rest_signal
    global stop_signal
    while True:
        if purchases[time] != "":
            semaphore.acquire()
            bank["100"] += 1
            rest = 100 - get_ticket_price(purchases[time])
            print("Moment: %s\nCity: %s\nPrice: %s"
                  % (time, purchases[time], get_ticket_price(purchases[time])))
            rest_signal = True
            semaphore.release()
        sleep(0.001)
        time += 1
        if time == len(purchases):
            stop_signal = True
            break


def give_rest():
    global rest
    global rest_signal
    while True:
        if rest_signal:
            semaphore.acquire()
            rest_signal = False
            c1, c2, c5, c10, c25, c50 = gather_rest()
            if count_rest(c1, c2, c5, c10, c25, c50) < rest:
                print("Unable to give rest")
                give_money_back(c1, c2, c5, c10, c25, c50)
            else:
                print("Rest: " + get_rest_string(c1, c2, c5, c10, c25, c50))
            print("Bank: %s\n" % count_bank())
            semaphore.release()
        if stop_signal:
            break


thread1 = threading.Thread(target=sell_ticket)
thread2 = threading.Thread(target=give_rest)
thread1.start()
thread2.start()
thread1.join()
thread2.join()
