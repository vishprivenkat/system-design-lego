import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from container_manager import ContainerManager
from container import Container
from machine import Machine


class TestContainerManager(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures before each test method"""
        self.machines = [
            "machine1,8,4096",
            "machine2,16,8192",
            "machine3,4,2048"
        ]
        self.manager = ContainerManager(self.machines)

    def test_container_manager_initialization(self):
        """Test that ContainerManager initializes with correct machines"""
        self.assertEqual(len(self.manager.machines), 3)
        self.assertIn("machine1", self.manager.machines)
        self.assertIn("machine2", self.manager.machines)
        self.assertIn("machine3", self.manager.machines)
        self.assertEqual(len(self.manager.containerToMachine), 0)

    def test_allocate_machines_parsing(self):
        """Test that machines are parsed correctly from input strings"""
        machine1 = self.manager.machines["machine1"]
        self.assertEqual(machine1.machineId, "machine1")
        self.assertEqual(machine1.totalCpu, 8)
        self.assertEqual(machine1.totalMem, 4096)

        machine2 = self.manager.machines["machine2"]
        self.assertEqual(machine2.totalCpu, 16)
        self.assertEqual(machine2.totalMem, 8192)

    def test_assign_machine_cpu_criteria(self):
        """Test assigning a container with CPU criteria (criteria=0)"""
        result = self.manager.assignMachine(0, "web-app", "nginx:latest", 4, 2048)

        self.assertEqual(result, "machine2")
        self.assertIn("web-app", self.manager.containerToMachine)
        self.assertEqual(self.manager.containerToMachine["web-app"], "machine2")
        self.assertEqual(self.manager.machines["machine2"].availableCpu, 12)
        self.assertEqual(self.manager.machines["machine2"].availableMem, 6144)

    def test_assign_machine_memory_criteria(self):
        """Test assigning a container with memory criteria (criteria=1)"""
        result = self.manager.assignMachine(1, "db-app", "postgres:latest", 4, 2048)

        self.assertEqual(result, "machine2")
        self.assertIn("db-app", self.manager.containerToMachine)

    def test_assign_machine_insufficient_resources(self):
        """Test assigning a container when no machine has sufficient resources"""
        result = self.manager.assignMachine(0, "huge-app", "image", 32, 16384)

        self.assertEqual(result, "")
        self.assertNotIn("huge-app", self.manager.containerToMachine)

    def test_assign_machine_exact_fit(self):
        """Test assigning a container that exactly fits a machine"""
        result = self.manager.assignMachine(0, "exact-fit", "image", 4, 2048)

        self.assertEqual(result, "machine3")
        self.assertEqual(self.manager.machines["machine3"].availableCpu, 0)
        self.assertEqual(self.manager.machines["machine3"].availableMem, 0)

    def test_assign_multiple_containers(self):
        """Test assigning multiple containers to different machines"""
        result1 = self.manager.assignMachine(0, "app1", "image1", 2, 1024)
        result2 = self.manager.assignMachine(0, "app2", "image2", 2, 1024)
        result3 = self.manager.assignMachine(0, "app3", "image3", 2, 1024)

        self.assertEqual(len(self.manager.containerToMachine), 3)
        self.assertIn("app1", self.manager.containerToMachine)
        self.assertIn("app2", self.manager.containerToMachine)
        self.assertIn("app3", self.manager.containerToMachine)

    def test_assign_machine_sorted_order(self):
        """Test that machines are evaluated in sorted order by machineId"""
        machines = [
            "machineZ,8,4096",
            "machineA,8,4096",
            "machineM,8,4096"
        ]
        manager = ContainerManager(machines)

        # With same resources, sorted order should pick machineA first
        result = manager.assignMachine(0, "test", "image", 2, 1024)
        self.assertEqual(result, "machineA")

    def test_assign_machine_best_fit_cpu(self):
        """Test that the machine with most available CPU is chosen (criteria=0)"""
        # Fill up machine2 partially
        self.manager.assignMachine(0, "filler", "image", 8, 4096)

        # Now machine1 should have more CPU available than machine2
        result = self.manager.assignMachine(0, "new-app", "image", 2, 1024)

        # machine1 has 8 CPU available, machine2 has 8 CPU available
        # machine3 has 4 CPU available
        # Should pick machine1 or machine2 (whichever comes first alphabetically)
        self.assertIn(result, ["machine1", "machine2"])

    def test_assign_machine_best_fit_memory(self):
        """Test that the machine with most available memory is chosen (criteria=1)"""
        result = self.manager.assignMachine(1, "mem-app", "image", 2, 1024)

        # machine2 has the most memory (8192)
        self.assertEqual(result, "machine2")

    def test_stop_container_success(self):
        """Test stopping an existing container returns True"""
        self.manager.assignMachine(0, "app1", "image", 4, 2048)

        result = self.manager.stop("app1")

        self.assertTrue(result)
        self.assertNotIn("app1", self.manager.containerToMachine)

    def test_stop_container_not_found(self):
        """Test stopping a non-existent container returns False"""
        result = self.manager.stop("nonexistent")

        self.assertFalse(result)

    def test_stop_container_resource_recovery(self):
        """Test that resources are recovered after stopping a container"""
        machine_id = self.manager.assignMachine(0, "app1", "image", 4, 2048)
        machine = self.manager.machines[machine_id]

        cpu_before_stop = machine.availableCpu
        mem_before_stop = machine.availableMem

        self.manager.stop("app1")

        self.assertEqual(machine.availableCpu, cpu_before_stop + 4)
        self.assertEqual(machine.availableMem, mem_before_stop + 2048)

    def test_stop_and_reassign(self):
        """Test stopping a container and reassigning resources"""
        # Assign a container
        self.manager.assignMachine(0, "app1", "image", 4, 2048)

        # Stop it
        self.manager.stop("app1")

        # Assign a new container with same name
        result = self.manager.assignMachine(0, "app1", "image", 4, 2048)

        self.assertNotEqual(result, "")
        self.assertIn("app1", self.manager.containerToMachine)

    def test_multiple_stops(self):
        """Test stopping multiple containers"""
        self.manager.assignMachine(0, "app1", "image1", 2, 1024)
        self.manager.assignMachine(0, "app2", "image2", 2, 1024)
        self.manager.assignMachine(0, "app3", "image3", 2, 1024)

        self.assertEqual(len(self.manager.containerToMachine), 3)

        self.manager.stop("app1")
        self.assertEqual(len(self.manager.containerToMachine), 2)

        self.manager.stop("app3")
        self.assertEqual(len(self.manager.containerToMachine), 1)

        self.manager.stop("app2")
        self.assertEqual(len(self.manager.containerToMachine), 0)

    def test_assign_after_partial_allocation(self):
        """Test assigning containers after some machines are partially full"""
        # Fill machine3 completely
        self.manager.assignMachine(0, "app1", "image", 4, 2048)

        # machine3 is now full, next container should go elsewhere
        result = self.manager.assignMachine(0, "app2", "image", 4, 2048)

        self.assertIn(result, ["machine1", "machine2"])
        self.assertNotEqual(result, "machine3")

    def test_empty_machines_list(self):
        """Test ContainerManager with no machines"""
        manager = ContainerManager([])

        self.assertEqual(len(manager.machines), 0)

        result = manager.assignMachine(0, "app", "image", 2, 1024)
        self.assertEqual(result, "")

    def test_container_isolation_across_machines(self):
        """Test that containers on different machines don't interfere"""
        result1 = self.manager.assignMachine(0, "app1", "image1", 2, 1024)
        result2 = self.manager.assignMachine(0, "app2", "image2", 8, 4096)

        # Containers should be on different machines
        self.assertNotEqual(result1, result2)

        # Stop one container
        self.manager.stop("app1")

        # Other container should still exist
        self.assertIn("app2", self.manager.containerToMachine)

    def test_criteria_selection_impact(self):
        """Test that different criteria result in different machine selection"""
        machines = [
            "machineA,16,2048",  # High CPU, low memory
            "machineB,4,8192"    # Low CPU, high memory
        ]
        manager = ContainerManager(machines)

        # With CPU criteria, should pick machineA
        result_cpu = manager.assignMachine(0, "cpu-app", "image", 2, 1024)
        self.assertEqual(result_cpu, "machineA")

        # Reset
        manager = ContainerManager(machines)

        # With memory criteria, should pick machineB
        result_mem = manager.assignMachine(1, "mem-app", "image", 2, 1024)
        self.assertEqual(result_mem, "machineB")

    def test_assign_with_zero_resources(self):
        """Test assigning a container with zero resources"""
        result = self.manager.assignMachine(0, "zero-app", "image", 0, 0)

        # Should succeed and pick first machine in sorted order
        self.assertNotEqual(result, "")
        self.assertIn("zero-app", self.manager.containerToMachine)


if __name__ == '__main__':
    unittest.main()
