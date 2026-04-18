import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from machine import Machine
from container import Container


class TestMachine(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures before each test method"""
        self.machine = Machine("machine1", 8, 4096)

    def test_machine_initialization(self):
        """Test that a machine is initialized with correct attributes"""
        machine = Machine("test-machine", 16, 8192)

        self.assertEqual(machine.machineId, "test-machine")
        self.assertEqual(machine.totalCpu, 16)
        self.assertEqual(machine.totalMem, 8192)
        self.assertEqual(machine.availableCpu, 16)
        self.assertEqual(machine.availableMem, 8192)
        self.assertEqual(len(machine.containersRunning), 0)

    def test_can_allocate_with_sufficient_resources(self):
        """Test canAllocate returns True when resources are available"""
        self.assertTrue(self.machine.canAllocate(4, 2048))
        self.assertTrue(self.machine.canAllocate(8, 4096))
        self.assertTrue(self.machine.canAllocate(0, 0))

    def test_can_allocate_with_insufficient_cpu(self):
        """Test canAllocate returns False when CPU is insufficient"""
        self.assertFalse(self.machine.canAllocate(16, 2048))

    def test_can_allocate_with_insufficient_memory(self):
        """Test canAllocate returns False when memory is insufficient"""
        self.assertFalse(self.machine.canAllocate(4, 8192))

    def test_can_allocate_with_insufficient_both(self):
        """Test canAllocate returns False when both resources are insufficient"""
        self.assertFalse(self.machine.canAllocate(16, 8192))

    def test_update_cpu_allocate(self):
        """Test CPU allocation decreases available CPU"""
        result = self.machine.updateCpu(4, 'allocate')

        self.assertEqual(result, 4)
        self.assertEqual(self.machine.availableCpu, 4)

    def test_update_cpu_allocate_excessive(self):
        """Test CPU allocation does not decrease when insufficient"""
        result = self.machine.updateCpu(16, 'allocate')

        self.assertEqual(result, 8)
        self.assertEqual(self.machine.availableCpu, 8)

    def test_update_cpu_deallocate(self):
        """Test CPU deallocation increases available CPU"""
        self.machine.updateCpu(4, 'allocate')
        result = self.machine.updateCpu(2, 'deallocate')

        self.assertEqual(result, 6)
        self.assertEqual(self.machine.availableCpu, 6)

    def test_update_mem_allocate(self):
        """Test memory allocation decreases available memory"""
        result = self.machine.updateMem(2048, 'allocate')

        self.assertEqual(result, 2048)
        self.assertEqual(self.machine.availableMem, 2048)

    def test_update_mem_allocate_excessive(self):
        """Test memory allocation does not decrease when insufficient"""
        result = self.machine.updateMem(8192, 'allocate')

        self.assertEqual(result, 4096)
        self.assertEqual(self.machine.availableMem, 4096)

    def test_update_mem_deallocate(self):
        """Test memory deallocation increases available memory"""
        self.machine.updateMem(2048, 'allocate')
        result = self.machine.updateMem(1024, 'deallocate')

        self.assertEqual(result, 3072)
        self.assertEqual(self.machine.availableMem, 3072)

    def test_allocate_container(self):
        """Test allocating a container reduces available resources"""
        container = Container("web-app", 4, 2048)
        self.machine.allocateContainer(container)

        self.assertEqual(self.machine.availableCpu, 4)
        self.assertEqual(self.machine.availableMem, 2048)
        self.assertIn("web-app", self.machine.containersRunning)
        self.assertEqual(self.machine.containersRunning["web-app"], container)

    def test_allocate_multiple_containers(self):
        """Test allocating multiple containers"""
        container1 = Container("app1", 2, 1024)
        container2 = Container("app2", 3, 1536)

        self.machine.allocateContainer(container1)
        self.machine.allocateContainer(container2)

        self.assertEqual(self.machine.availableCpu, 3)
        self.assertEqual(self.machine.availableMem, 1536)
        self.assertEqual(len(self.machine.containersRunning), 2)

    def test_deallocate_container_success(self):
        """Test deallocating an existing container returns True and frees resources"""
        container = Container("app1", 4, 2048)
        self.machine.allocateContainer(container)

        result = self.machine.deallocateContainer("app1")

        self.assertTrue(result)
        self.assertEqual(self.machine.availableCpu, 8)
        self.assertEqual(self.machine.availableMem, 4096)
        self.assertNotIn("app1", self.machine.containersRunning)

    def test_deallocate_container_not_found(self):
        """Test deallocating a non-existent container returns False"""
        result = self.machine.deallocateContainer("nonexistent")

        self.assertFalse(result)
        self.assertEqual(self.machine.availableCpu, 8)
        self.assertEqual(self.machine.availableMem, 4096)

    def test_allocate_and_deallocate_sequence(self):
        """Test a sequence of allocations and deallocations"""
        container1 = Container("app1", 2, 1024)
        container2 = Container("app2", 3, 1536)
        container3 = Container("app3", 1, 512)

        # Allocate containers
        self.machine.allocateContainer(container1)
        self.machine.allocateContainer(container2)
        self.machine.allocateContainer(container3)

        self.assertEqual(self.machine.availableCpu, 2)
        self.assertEqual(self.machine.availableMem, 1024)

        # Deallocate middle container
        self.machine.deallocateContainer("app2")

        self.assertEqual(self.machine.availableCpu, 5)
        self.assertEqual(self.machine.availableMem, 2560)
        self.assertEqual(len(self.machine.containersRunning), 2)

    def test_container_isolation(self):
        """Test that containers maintain their own state"""
        container1 = Container("app1", 2, 1024)
        container2 = Container("app2", 4, 2048)

        self.machine.allocateContainer(container1)
        self.machine.allocateContainer(container2)

        retrieved1 = self.machine.containersRunning["app1"]
        retrieved2 = self.machine.containersRunning["app2"]

        self.assertEqual(retrieved1.cpuUnits, 2)
        self.assertEqual(retrieved1.memUnits, 1024)
        self.assertEqual(retrieved2.cpuUnits, 4)
        self.assertEqual(retrieved2.memUnits, 2048)


if __name__ == '__main__':
    unittest.main()
