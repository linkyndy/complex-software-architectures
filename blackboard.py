from random import choice, shuffle
from time import sleep


class Blackboard(object):
    def __init__(self, chairs=None):
        self.chairs = chairs or []


class Chair(object):
    def __init__(self):
        self.seat = self.feet = self.backrest = self.stabilizer_bar = \
        self.packaged = False

    def is_complete(self):
        return (self.seat and self.feet and self.backrest and
                self.stabilizer_bar and self.packaged)


class Worker(object):
    def __init__(self, name, time):
        self.name = name
        self.time = time

    def can_work(self, chair):
        raise NotImplemented()

    def work(self, chair):
        raise NotImplemented()


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


class Controller(object):
    def __init__(self, blackboard, workers=None):
        self.blackboard = blackboard
        self.workers = workers or []

    def run(self):
        if not self.blackboard.chairs:
            raise Exception('No chairs added')
        if not self.workers:
            raise Exception('No workers added')

        while self.blackboard.chairs:
            print '%s Chairs left, workers taking ' \
                  'turns...' % len(self.blackboard.chairs)
            worker = choice(self.workers)
            print '  %s looks for a chair...' % worker.name
            for chair in self.blackboard.chairs:
                if worker.can_work(chair):
                    print '    Found available chair, started working on ' \
                          'it (%ss)' % worker.time
                    worker.work(chair)
                    print '    Finished working'
                    if chair.is_complete():
                        print '    Chair is complete'
                        self.blackboard.chairs.remove(chair)
                    break
            shuffle(self.blackboard.chairs)


if __name__ == '__main__':
    blackboard = Blackboard([Chair() for _ in range(5)])

    john = SeatCutter('john', 2)
    travis = FeetAssembler('travis', 1)
    james = BackrestAssembler('james', 3)
    oliver = StabilizerBarAssembler('oliver', 1)
    donald = ChairPackager('donald', 4)

    controller = Controller(blackboard, workers=[john, travis, james, oliver, donald])
    controller.run()
