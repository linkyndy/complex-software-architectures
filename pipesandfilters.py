from time import sleep


class Pipe(object):
    def __init__(self, workers):
        self.workers = workers

    def run(self, chairs):
        print '%s chairs...' % len(chairs)
        for chair in chairs:
            print '  Working on chair...'
            for worker in self.workers:
                print '    %s works on it (%ss)' % (worker.name, worker.time)
                worker.work(chair)
                print '    Finished working'
            print '  Chair is ready'
        print 'All chairs have been assembled'


class Chair(object):
    def __init__(self):
        self.seat = self.feet = self.backrest = self.stabilizer_bar = \
        self.packaged = False


class Worker(object):
    def __init__(self, name, time):
        self.name = name
        self.time = time

    def work(self, chair):
        raise NotImplemented()


class SeatCutter(Worker):
    def work(self, chair):
        sleep(self.time)
        chair.seat = True


class FeetAssembler(Worker):
    def work(self, chair):
        sleep(self.time)
        chair.feet = True


class BackrestAssembler(Worker):
    def work(self, chair):
        sleep(self.time)
        chair.backrest = True


class StabilizerBarAssembler(Worker):
    def work(self, chair):
        sleep(self.time)
        chair.stabilizer_bar = True


class ChairPackager(Worker):
    def work(self, chair):
        sleep(self.time)
        chair.packaged = True


if __name__ == '__main__':
    john = SeatCutter('john', 2)
    travis = FeetAssembler('travis', 1)
    james = BackrestAssembler('james', 3)
    oliver = StabilizerBarAssembler('oliver', 1)
    donald = ChairPackager('donald', 4)

    pipe = Pipe(workers=(john, travis, james, oliver, donald))
    pipe.run([Chair() for _ in range(5)])
