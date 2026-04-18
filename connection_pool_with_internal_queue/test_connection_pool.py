import pytest
from connection_pool import ConnectionPool


class TestConnectionPool:

    def test_init(self):
        """Test ConnectionPool initialization"""
        pool = ConnectionPool(capacity=5)
        assert pool.capacity == 5
        assert pool.busy_connections == 0
        assert len(pool.connection_pool) == 5
        assert all(conn is None for conn in pool.connection_pool)

    def test_acquire_connection_when_available(self):
        """Test acquiring a connection when pool has capacity"""
        pool = ConnectionPool(capacity=3)

        conn_id = pool.acquireConnection("req1")
        assert conn_id == 0
        assert pool.busy_connections == 1
        assert pool.connection_pool[0] == "req1"

    def test_acquire_multiple_connections(self):
        """Test acquiring multiple connections"""
        pool = ConnectionPool(capacity=3)

        conn1 = pool.acquireConnection("req1")
        conn2 = pool.acquireConnection("req2")
        conn3 = pool.acquireConnection("req3")

        assert conn1 == 0
        assert conn2 == 1
        assert conn3 == 2
        assert pool.busy_connections == 3

    def test_acquire_connection_when_full(self):
        """Test acquiring connection when pool is at capacity"""
        pool = ConnectionPool(capacity=2)

        pool.acquireConnection("req1")
        pool.acquireConnection("req2")

        # Third request should be queued
        conn_id = pool.acquireConnection("req3")
        assert conn_id == -1
        assert "req3" in pool.request_to_connection
        assert pool.request_to_connection["req3"][0] == "waiting"

    def test_release_connection(self):
        """Test releasing a connection"""
        pool = ConnectionPool(capacity=2)

        pool.acquireConnection("req1")
        success = pool.releaseConnection("req1")

        assert success is True
        assert pool.busy_connections == 0
        assert pool.connection_pool[0] is None
        assert "req1" not in pool.request_to_connection

    def test_release_and_assign_queued_request(self):
        """Test that releasing a connection assigns it to queued request"""
        pool = ConnectionPool(capacity=2)

        pool.acquireConnection("req1")
        pool.acquireConnection("req2")
        pool.acquireConnection("req3")  # This gets queued

        # Release req1, req3 should get assigned
        pool.releaseConnection("req1")

        assert pool.busy_connections == 2
        assert pool.connection_pool[0] == "req3"
        assert pool.request_to_connection["req3"][0] == "assigned"

    def test_release_nonexistent_request(self):
        """Test releasing a request that doesn't exist"""
        pool = ConnectionPool(capacity=2)

        success = pool.releaseConnection("nonexistent")
        assert success is False

    def test_expire_request(self):
        """Test expiring a waiting request"""
        pool = ConnectionPool(capacity=1)

        pool.acquireConnection("req1")
        pool.acquireConnection("req2")  # Gets queued

        pool.expireRequest("req2")

        assert "req2" not in pool.request_to_connection

    def test_expire_nonexistent_request(self):
        """Test expiring a request that doesn't exist"""
        pool = ConnectionPool(capacity=2)

        # Should not raise an error
        pool.expireRequest("nonexistent")

    def test_get_requests_with_connection(self):
        """Test getting all requests with assigned connections"""
        pool = ConnectionPool(capacity=3)

        pool.acquireConnection("req1")
        pool.acquireConnection("req2")
        pool.acquireConnection("req3")

        requests = pool.getRequestsWithConnection()
        assert requests == ["req1-0", "req2-1", "req3-2"]

    def test_get_requests_with_connection_empty(self):
        """Test getting requests when no connections are assigned"""
        pool = ConnectionPool(capacity=2)

        requests = pool.getRequestsWithConnection()
        assert requests == []

    def test_get_requests_excludes_waiting(self):
        """Test that getRequestsWithConnection excludes waiting requests"""
        pool = ConnectionPool(capacity=1)

        pool.acquireConnection("req1")
        pool.acquireConnection("req2")  # Gets queued

        requests = pool.getRequestsWithConnection()
        assert requests == ["req1-0"]
        assert "req2" not in "".join(requests)

    def test_connection_reuse_after_release(self):
        """Test that released connections can be reused"""
        pool = ConnectionPool(capacity=2)

        pool.acquireConnection("req1")
        pool.releaseConnection("req1")

        conn_id = pool.acquireConnection("req2")
        assert conn_id == 0  # Should reuse the first connection
        assert pool.connection_pool[0] == "req2"

    def test_multiple_queued_requests(self):
        """Test multiple requests being queued and processed"""
        pool = ConnectionPool(capacity=1)

        pool.acquireConnection("req1")
        pool.acquireConnection("req2")  # Queued
        pool.acquireConnection("req3")  # Queued

        pool.releaseConnection("req1")  # req2 should get assigned
        assert pool.request_to_connection["req2"][0] == "assigned"

        pool.releaseConnection("req2")  # req3 should get assigned
        assert pool.request_to_connection["req3"][0] == "assigned"
