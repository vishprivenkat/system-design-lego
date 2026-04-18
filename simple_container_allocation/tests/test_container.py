import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from container import Container


class TestContainer(unittest.TestCase):

    def test_container_initialization(self):
        """Test that a container is initialized with correct attributes"""
        container = Container("web-server", 2, 512)

        self.assertEqual(container.containerName, "web-server")
        self.assertEqual(container.cpuUnits, 2)
        self.assertEqual(container.memUnits, 512)

    def test_container_with_zero_resources(self):
        """Test container creation with zero CPU and memory"""
        container = Container("minimal", 0, 0)

        self.assertEqual(container.cpuUnits, 0)
        self.assertEqual(container.memUnits, 0)

    def test_container_with_large_resources(self):
        """Test container with large resource requirements"""
        container = Container("heavy-app", 16, 32768)

        self.assertEqual(container.cpuUnits, 16)
        self.assertEqual(container.memUnits, 32768)

    def test_container_name_types(self):
        """Test container with various name formats"""
        container1 = Container("simple", 1, 100)
        container2 = Container("with-dashes", 1, 100)
        container3 = Container("with_underscores", 1, 100)
        container4 = Container("MixedCase123", 1, 100)

        self.assertEqual(container1.containerName, "simple")
        self.assertEqual(container2.containerName, "with-dashes")
        self.assertEqual(container3.containerName, "with_underscores")
        self.assertEqual(container4.containerName, "MixedCase123")

    def test_container_attribute_access(self):
        """Test that all container attributes are accessible"""
        container = Container("test", 4, 1024)

        self.assertTrue(hasattr(container, 'containerName'))
        self.assertTrue(hasattr(container, 'cpuUnits'))
        self.assertTrue(hasattr(container, 'memUnits'))


if __name__ == '__main__':
    unittest.main()
