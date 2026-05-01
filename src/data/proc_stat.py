import dataclasses


@dataclasses.dataclass
class ProcStat:
    cpu_id: str
    user_time: int
    nice_time: int
    system_time: int
    idle_time: int
    iowait_time: int
    irq_time: int
    softirq_time: int
    steal_time: int
    guest_time: int
    guest_nice_time: int

    def total_time(self) -> int:
        return sum([
            self.user_time, self.nice_time, self.system_time, self.idle_time,
            self.iowait_time, self.irq_time, self.softirq_time, self.steal_time,
            self.guest_time, self.guest_nice_time
        ])

    def non_idle_time(self) -> int:
        return self.total_time() - self.idle_time

    def calculate_cpu_usage(self, prev: ProcStat) -> float:
        prev_total: int = prev.total_time()
        curr_total: int = self.total_time()

        prev_non_idle: int = prev.non_idle_time()
        curr_non_idle: int = self.non_idle_time()

        total_delta: int = curr_total - prev_total
        non_idle_delta: int = curr_non_idle - prev_non_idle

        cpu_usage = (non_idle_delta * 100.) / total_delta if total_delta > 0 else 0
        return cpu_usage
