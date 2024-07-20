import threading, time

done = False

def worker(text, number):
    counter = 0
    while True:
        time.sleep(1)
        counter += 1
        print(f"{text} {number} {counter}")

t1 = threading.Thread(target=worker, daemon=True, args=("ola", 22))
t2 = threading.Thread(target=worker, daemon=True, args=("ola", 22))
input("press enter to quit")
done = True