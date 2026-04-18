from container import Container

class Machine: 
    def __init__(self, machineId, totalCpu, totalMem):
        self.machineId = machineId 
        self.totalCpu = totalCpu  
        self.totalMem = totalMem
        self.containersRunning = dict()
        self.availableMem = totalMem 
        self.availableCpu = totalCpu 
    
    def canAllocate(self, cpuUnits, memUnits):
        return self.availableMem >= memUnits and self.availableCpu >= cpuUnits 
    
    def updateCpu(self, cpuUnits, op = 'allocate'):
        if op == 'allocate':
            if self.availableCpu >= cpuUnits:
                self.availableCpu -= cpuUnits
        elif op == 'deallocate':
            self.availableCpu += cpuUnits
        return self.availableCpu 
    
    def updateMem(self, memUnits, op = 'allocate'):
        if op == 'allocate':
            if self.availableMem >= memUnits:
                self.availableMem -= memUnits
        elif op == 'deallocate':
            self.availableMem += memUnits
        return self.availableMem 

    def allocateContainer(self, container: Container): 
        self.containersRunning[container.containerName] = container 
        self.updateCpu(container.cpuUnits, op='allocate')
        self.updateMem(container.memUnits, op='allocate') 
    
    def deallocateContainer(self, containerId):
        if containerId in self.containersRunning:
            container = self.containersRunning[containerId]
            self.updateCpu(container.cpuUnits, op='deallocate')
            self.updateMem(container.memUnits, op='deallocate') 
            del self.containersRunning[containerId] 
            return True 
        return False 
