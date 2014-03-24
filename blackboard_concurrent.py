from random import choice, shuffle
from threading import Thread, Lock
from time import sleep


class Blackboard(object):
    def __init__(self, chairs=None):
        self.chairs = chairs or []


class Chair(object):
    def __init__(self):
        self.seat = self.feet = self.backrest = self.stabilizer_bar = \
        self.packaged = False
        self.lock = Lock()

    def is_complete(self):
        return (self.seat and self.feet and self.backrest and
                self.stabilizer_bar and self.packaged)

    def __str__(self):
        return '%s%s%s%s%s' % ('X' if self.seat else 'O',
                               'X' if self.feet else 'O',
                               'X' if self.backrest else 'O',
                               'X' if self.stabilizer_bar else 'O',
                               'X' if self.packaged else 'O')


class Worker(Thread):
    def __init__(self, name, time, blackboard):
        super(Worker, self).__init__()

        self.name = name
        self.time = time
        self.blackboard = blackboard

        self.start()

    def can_work(self, chair):
        raise NotImplemented()

    def work(self, chair):
        raise NotImplemented()

    def run(self):
        while self.blackboard.chairs:
            chair = choice(self.blackboard.chairs)
            # Search for another chair is this one is currently locked
            if chair.lock.acquire(False):
                try:
                    if self.can_work(chair):
                        print '%s: Working on chair %s...' % (self.name,
                                                              chair)
                        self.work(chair)
                        if chair.is_complete():
                            print '%s: Chair is finished!' % self.name
                            self.blackboard.chairs.remove(chair)
                finally:
                    chair.lock.release()


class SeatCutter(Worker):
    def can_work(self, chair):
        # For a SeatCutter to do his job, given chair mustn't have a seat yet
        return not chair.seat

    def work(self, chair):
        sleep(self.time)
        chair.seat = True


class FeetAssembler(Worker):
    def can_work(self, chair):
        # For a FeetAssembler to do his job, given chair must have a seat, but
        # not its feet yet
        return chair.seat and not chair.feet

    def work(self, chair):
        sleep(self.time)
        chair.feet = True


class BackrestAssembler(Worker):
    def can_work(self, chair):
        # For a BackrestAssembler to do his job, given chair must have a seat,
        # but not its backrest yet
        return chair.seat and not chair.backrest

    def work(self, chair):
        sleep(self.time)
        chair.backrest = True


class StabilizerBarAssembler(Worker):
    def can_work(self, chair):
        # For a StabilizerBarAssembler to do his job, given chair must have
        # its feet, but not its stabilizer bar yet
        return chair.feet and not chair.stabilizer_bar

    def work(self, chair):
        sleep(self.time)
        chair.stabilizer_bar = True


class ChairPackager(Worker):
    def can_work(self, chair):
        # For a ChairPackager to do his job, given chair must have everything
        # assembled, but mustn't be packaged yet
        return chair.stabilizer_bar and chair.backrest and not chair.packaged

    def work(self, chair):
        sleep(self.time)
        chair.packaged = True


if __name__ == '__main__':
    blackboard = Blackboard([Chair() for _ in range(5)])

    john = SeatCutter('john', 2, blackboard)
    travis = FeetAssembler('travis', 1, blackboard)
    james = BackrestAssembler('james', 3, blackboard)
    oliver = StabilizerBarAssembler('oliver', 1, blackboard)
    donald = ChairPackager('donald', 4, blackboard)

