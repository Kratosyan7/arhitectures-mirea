# -*- coding: utf-8 -*-
# Ghidra post-script (Jython): decompile named functions and print C.
# Run via: analyzeHeadless ... -postScript DecompileFn.py
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

TARGETS = ["my_replspace", "main"]

program = getCurrentProgram()
decomp = DecompInterface()
decomp.openProgram(program)
monitor = ConsoleTaskMonitor()
fm = program.getFunctionManager()

found = {}
for f in fm.getFunctions(True):
    if f.getName() in TARGETS:
        found[f.getName()] = f

for name in TARGETS:
    print("")
    print("==================== DECOMPILED: %s ====================" % name)
    f = found.get(name)
    if f is None:
        print("// function %s not found" % name)
        continue
    res = decomp.decompileFunction(f, 60, monitor)
    if res is not None and res.decompileCompleted():
        print(res.getDecompiledFunction().getC())
    else:
        print("// decompilation failed for %s" % name)
