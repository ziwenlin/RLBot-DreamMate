import time

class TickMonitor:
    def __init__(self):
        time_now = time.perf_counter()
        self.last_time = time_now
        self.tps = 1

    def step(self):
        time_now = time.perf_counter()
        time_dif = time_now - self.last_time
        if time_dif > 0:
            self.tps = 1 / time_dif
        else:
            self.tps = 1
        self.last_time = time_now
        return self.tps


def main():
    tick = TickMonitor()
    tick.step()

    for _ in range(20):
        # 60 tps door time.sleep omdat Windows alles op 60 tps
        time.sleep(0.001)
        tick.step()
        print(f"Ticks per second: {tick.tps:.2f}")



if __name__ == '__main__':
    main()