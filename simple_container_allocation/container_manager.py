from typing import List
from machine import Machine
from container import Container

class ContainerManager:
    def __init__(self, machines):
        self.machines = dict()
        self.containerToMachine = dict() 
        self.allocate_machines(machines)

    def allocate_machines(self, machines: List[str]):
        # Function to parse machines and store 
        for machine in machines:
            parts = machine.split(',')
            machineId, cpuUnits, memUnits = parts[0], int(parts[1]), int(parts[2]) 
            self.machines[machineId] = Machine(machineId, cpuUnits, memUnits)
    
    def assignMachine(self, criteria, containerName, imageUrl, cpuUnits, memMb) -> str: 
        best_value = -1 
        best_machine = None 
        for machineId in sorted(self.machines.keys()):
            machine = self.machines[machineId]

            if not machine.canAllocate(cpuUnits, memMb):
                continue 
            value = -1 
            if criteria == 0:
                value = machine.availableCpu 
            else:
                value = machine.availableMem 
            
            if value > best_value:
                best_value = value 
                best_machine = machineId 
        
        if best_machine:
            container = Container(containerName, cpuUnits, memMb)
            self.machines[best_machine].allocateContainer(container) 
            self.containerToMachine[containerName] = best_machine
            return best_machine 
        return "" 
    



    def stop(self, name) -> bool:
        if name not in self.containerToMachine:
            return False 

        machineId = self.containerToMachine[name] 
        if self.machines[machineId].deallocateContainer(name):
            del self.containerToMachine[name] 
            return True 
        return False 
