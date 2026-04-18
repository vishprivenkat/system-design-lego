from typing import List
from collections import deque 

class Node:
    def __init__(self, value:str) -> None:
        self.prev_node = None 
        self.next_node = None 
        self.value = value 

class Queue: 
    def __init__(self) -> None: 
        self.head = Node('start') 
        self.tail = Node('end') 

        self.head.next_node = self.tail 
        self.head.prev_node = self.tail 

        self.tail.next_node = self.head 
        self.tail.prev_node = self.head 

    def _enque(self, value:str) -> Node:
        # Enque value at a node before the tail node 
        last_node = self.tail
        second_last_node = self.tail.prev_node 
        
        new_node = Node(value)

        new_node.next_node = self.tail 
        new_node.prev_node = second_last_node 

        second_last_node.next_node = new_node 
        self.tail.prev_node = new_node 

        return new_node 
    
    def _deque(self) -> None: 
        if self.head.next_node == self.tail: 
            # implies queue is empty, so no nodes available to deque 
            return 

        deque_node = self.head.next_node 
        second_node = deque_node.next_node 

        self.head.next_node = second_node 
        second_node.prev_node = self.head 

        del deque_node 

    def _delete_node(self, node:Node) -> None: 
        if not node: 
            return 
        
        node_after = node.next_node 
        node_before = node.prev_node 

        node_after.prev_node = node_before
        node_before.next_node = node_after

        del node  
    
    def _top(self) -> str: 
        if self.head.next_node == self.tail: 
            return None
        return self.head.next_node.value 


            
class ConnectionPool:
    def __init__(self, capacity: int):
        self.capacity = capacity 
        self.busy_connections = 0 
        self.connection_pool = [None]*capacity
        self.request_to_connection = dict()  
        self.queue = Queue() 

    def _findSmallestAvailableConnection(self) -> int: 
        for i in range(0, self.capacity):
            if not self.connection_pool[i]: 
                return i 
        return -1 

    def acquireConnection(self, requestId: str) -> int:
        if self.busy_connections < self.capacity:
            smallestAvailableConnection = self._findSmallestAvailableConnection() 
            self.request_to_connection[requestId] = ('assigned', smallestAvailableConnection) 
            self.connection_pool[smallestAvailableConnection] = requestId 
            self.busy_connections +=1 
            return smallestAvailableConnection
        
        # Enque request 
        request_node = self.queue._enque(requestId)
        self.request_to_connection[requestId] = ('waiting', request_node) 
        return -1

    def releaseConnection(self, requestId: str) -> bool:
        if requestId in self.request_to_connection and self.request_to_connection[requestId][0] == 'assigned': 
            # Release connection 
            status, connection = self.request_to_connection[requestId] 
            self.busy_connections -=1 
            self.connection_pool[connection] = None 
            del self.request_to_connection[requestId] 

            # 
            earliest_waiting_requestId = self.queue._top() 
            if earliest_waiting_requestId: 
                self.queue._deque() 
                self.acquireConnection(earliest_waiting_requestId) 
            return True 

        return False

    def expireRequest(self, requestId: str):
        if requestId in self.request_to_connection and self.request_to_connection[requestId][0] == 'waiting': 
            status, queue_node = self.request_to_connection[requestId] 

            self.queue._delete_node(queue_node)
            del self.request_to_connection[requestId] 

        return

    def getRequestsWithConnection(self) -> List[str]:
        requestsWithConnection = []
        for requestId, status in self.request_to_connection.items():
            if status[0] == 'assigned':
                requestsWithConnection.append(requestId+'-'+str(status[1])) 
        
        if requestsWithConnection:
            return sorted(requestsWithConnection)

        return []