# Simple Container Allocation System

A Python-based container allocation system that manages the distribution of containers across multiple machines based on resource availability (CPU and memory).

## Architecture

The system consists of three main components:

- **Container** ([container.py](container.py)) - Represents a container with CPU and memory requirements
- **Machine** ([machine.py](machine.py)) - Represents a physical/virtual machine with resource tracking
- **ContainerManager** ([container_manager.py](container_manager.py)) - Orchestrates container allocation across machines

## Features

- **Resource-based allocation** - Allocates containers based on CPU and memory requirements
- **Multiple allocation strategies** - Choose between CPU-optimized (criteria=0) or memory-optimized (criteria=1) allocation
- **Best-fit algorithm** - Selects the machine with the most available resources of the target type
- **Resource tracking** - Monitors available CPU and memory on each machine
- **Container lifecycle management** - Start and stop containers with automatic resource reclamation

## Installation

No external dependencies required. The system uses Python's standard library.

```bash
# Clone or navigate to the directory
cd system-design-lego/simple_container_allocation
```

## Usage

### Basic Example

```python
from container_manager import ContainerManager

# Initialize with machine specifications
# Format: "machineId,cpuUnits,memoryMB"
machines = [
    "machine1,8,4096",
    "machine2,16,8192",
    "machine3,4,2048"
]

manager = ContainerManager(machines)

# Assign a container with CPU-optimized allocation (criteria=0)
machine_id = manager.assignMachine(
    criteria=0,                    # 0 for CPU, 1 for memory
    containerName="web-server",
    imageUrl="nginx:latest",
    cpuUnits=4,
    memMb=2048
)

print(f"Container assigned to: {machine_id}")

# Stop a container and reclaim resources
success = manager.stop("web-server")
print(f"Container stopped: {success}")
```

### Allocation Criteria

- **criteria=0** (CPU-optimized): Assigns container to the machine with the most available CPU
- **criteria=1** (Memory-optimized): Assigns container to the machine with the most available memory

When multiple machines have the same available resources, the system selects the first machine in alphabetical order by machine ID.

### Return Values

- `assignMachine()` returns:
  - Machine ID (string) if allocation succeeds
  - Empty string `""` if no machine has sufficient resources

- `stop()` returns:
  - `True` if container was found and stopped
  - `False` if container doesn't exist

## Running Tests

The project includes comprehensive test coverage for all three modules.

### Prerequisites

Install pytest if you haven't already:

```bash
pip install pytest
```

### Running All Tests

```bash
# From the simple_container_allocation directory
python -m pytest tests/ -v

# Or using unittest
python -m unittest discover tests/
```

### Running Individual Test Files

```bash
# Test Container class
python -m pytest tests/test_container.py -v

# Test Machine class
python -m pytest tests/test_machine.py -v

# Test ContainerManager class
python -m pytest tests/test_container_manager.py -v
```

### Running Specific Tests

```bash
# Run a specific test case
python -m pytest tests/test_machine.py::TestMachine::test_allocate_container -v

# Run tests matching a pattern
python -m pytest tests/ -k "allocate" -v
```

### Test Coverage

The test suite includes **46 test cases** covering:

#### Container Tests (5 tests)
- Initialization and attributes
- Zero and large resource values
- Various naming formats

#### Machine Tests (18 tests)
- Resource allocation/deallocation
- CPU and memory update operations
- Container lifecycle management
- Resource boundary conditions
- Multiple container scenarios

#### ContainerManager Tests (23 tests)
- Manager initialization
- Machine parsing
- CPU and memory-based allocation strategies
- Best-fit algorithm behavior
- Resource insufficiency handling
- Container stopping and recovery
- Edge cases (empty machines, zero resources)
- Alphabetical sorting validation

### Example Test Output

```bash
$ python -m pytest tests/ -v

tests/test_container.py::TestContainer::test_container_initialization PASSED
tests/test_machine.py::TestMachine::test_machine_initialization PASSED
tests/test_container_manager.py::TestContainerManager::test_assign_machine_cpu_criteria PASSED
...
==================== 46 passed in 0.05s ====================
```

## Code Structure

```
simple_container_allocation/
├── container.py           # Container class
├── machine.py            # Machine class with resource management
├── container_manager.py  # Main orchestration logic
├── tests/
│   ├── __init__.py
│   ├── test_container.py
│   ├── test_machine.py
│   └── test_container_manager.py
└── README.md
```

## Implementation Details

### Container Class
Simple data structure holding:
- `containerName` - Unique identifier
- `cpuUnits` - CPU resources required
- `memUnits` - Memory (MB) required

### Machine Class
Manages machine resources with:
- Total and available CPU/memory tracking
- Container registry
- Allocation/deallocation logic with boundary checks

### ContainerManager Class
Provides high-level orchestration:
- Parses machine specifications
- Implements best-fit allocation algorithm
- Maintains container-to-machine mapping
- Handles container lifecycle

### Best-Fit Algorithm

1. Filter machines that can accommodate the container's resource requirements
2. Among eligible machines, select based on allocation criteria:
   - CPU criteria: Pick machine with highest available CPU
   - Memory criteria: Pick machine with highest available memory
3. If tie, select first machine alphabetically by machine ID
4. If no suitable machine found, return empty string

## Limitations & Considerations

- No persistence - all state is in-memory
- Single-threaded - not designed for concurrent operations
- No container health monitoring
- No automatic rebalancing
- Machine resources cannot be modified after initialization
- Container names must be unique across all machines
- Does not implement lazy delete for containers that have been de-allocated.
- Uses sorting by `machineId` instead of by capacity. 

## Future Enhancements

- Add persistence layer
- Implement container migration
- Support for resource limits vs requests
- Multi-dimensional resource optimization
- Container health checks
- Auto-scaling capabilities
