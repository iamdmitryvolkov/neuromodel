# Network tester (C) Dmitry Volkov 2015

# version 1.0 (8.07.2015)

from testerengine import *
from task import *


engine = TesterEngine()

#engine.add_task(Task("Noize nerons count", 1))
#engine.add_task(Task("Noize current", 2))
#engine.add_task(Task("Electrodes sensitivity", 3))
#engine.add_task(Task("Extra connections", 4))
#engine.add_task(Task("Extra electrode connections", 5))
#engine.add_task(Task("U threshold", 6))
#engine.add_task(Task("V threshold", 7))
#engine.add_task(Task("Stability limit", 8))
#engine.add_task(Task("Resource max", 9))
#engine.add_task(Task("Resource min", 10))
#engine.add_task(Task("U relax time", 11))
#engine.add_task(Task("S relax time", 12))
engine.add_task(Task("Potentials info", 13))

print("")

engine.start()

print("")
print("Bye bye")
