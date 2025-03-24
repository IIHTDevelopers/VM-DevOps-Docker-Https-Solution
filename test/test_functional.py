import sys
import unittest
import docker
import time
import requests
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from test.TestUtils import TestUtils

class TestDockerHttpdApache(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Setup Docker client and check if the required container exists."""
        cls.client = docker.from_env()
        cls.test_obj = TestUtils()

        # Check if the container already exists, but don't create a new one if it doesn't
        try:
            cls.container = cls.client.containers.get("httpd-container")
            print(f"Found existing container: {cls.container.name}")

            # Wait for the container to be in running state
            cls.wait_for_container_to_be_running()
        except docker.errors.NotFound:
            print("Container 'httpd-container' not found. Tests will fail.")
            cls.test_obj.yakshaAssert("container_exists", False, "functional")
            # Set container to None to indicate it doesn't exist
            cls.container = None

    @classmethod
    def tearDownClass(cls):
        """Cleanup after tests."""
        if cls.container is None:
            print("Tests complete. No container was found to clean up.")
        else:
            print("Tests complete. No need to remove container as it's already existing.")

    @classmethod
    def wait_for_container_to_be_running(cls, timeout=30):
        """Wait for the container to be in 'running' state."""
        if cls.container is None:
            print("Cannot wait for container to be running - container does not exist")
            return

        start_time = time.time()
        while time.time() - start_time < timeout:
            cls.container.reload()  # Reload the container to get its latest state
            if cls.container.status == 'running':
                print(f"Container {cls.container.name} is now running.")
                return
            print(f"Container {cls.container.name} is not running yet.")
            time.sleep(2)
        raise Exception(f"Container {cls.container.name} did not start within {timeout} seconds.")

    def test_container_running(self):
        """Test if the container 'httpd-container' is running."""
        try:
            if self.container is None:
                self.test_obj.yakshaAssert("test_container_running", False, "functional")
                print("test_container_running = Failed - Container does not exist")
                return

            self.container.reload()  # Reload the container's status
            expected_status = "running"
            actual_status = self.container.status
            if actual_status == expected_status:
                self.test_obj.yakshaAssert("test_container_running", True, "functional")
                print("test_container_running = Passed")
            else:
                self.test_obj.yakshaAssert("test_container_running", False, "functional")
                print("test_container_running = Failed")
        except Exception as e:
            self.test_obj.yakshaAssert("test_container_running", False, "exception")
            print("test_container_running = Failed due to Exception", str(e))

    def test_apache_installed(self):
        """Test if Apache HTTP server is installed in the container."""
        try:
            if self.container is None:
                self.test_obj.yakshaAssert("test_apache_installed", False, "functional")
                print("test_apache_installed = Failed - Container does not exist")
                return

            result = self.container.exec_run("httpd -v")
            expected_text = "Apache"
            actual_output = result.output.decode()
            if expected_text in actual_output:
                self.test_obj.yakshaAssert("test_apache_installed", True, "functional")
                print("test_apache_installed = Passed")
            else:
                self.test_obj.yakshaAssert("test_apache_installed", False, "functional")
                print("test_apache_installed = Failed")
        except Exception as e:
            self.test_obj.yakshaAssert("test_apache_installed", False, "exception")
            print("test_apache_installed = Failed due to Exception", str(e))

    def test_apache_service_running(self):
        """Test if Apache HTTP server is running."""
        try:
            if self.container is None:
                self.test_obj.yakshaAssert("test_apache_service_running", False, "functional")
                print("test_apache_service_running = Failed - Container does not exist")
                return

            result = self.container.exec_run("pgrep -fl httpd")
            expected_length = 0
            actual_length = len(result.output.decode())
            if actual_length > expected_length:
                self.test_obj.yakshaAssert("test_apache_service_running", True, "functional")
                print("test_apache_service_running = Passed")
            else:
                self.test_obj.yakshaAssert("test_apache_service_running", False, "functional")
                print("test_apache_service_running = Failed")
        except Exception as e:
            self.test_obj.yakshaAssert("test_apache_service_running", False, "exception")
            print("test_apache_service_running = Failed due to Exception", str(e))

    def test_apache_access(self):
        """Test if the Apache server is accessible via HTTP request."""
        try:
            if self.container is None:
                self.test_obj.yakshaAssert("test_apache_access", False, "functional")
                print("test_apache_access = Failed - Container does not exist")
                return

            # Access Apache via localhost:8080
            response = requests.get("http://localhost:8081")
            expected_status_code = 200
            actual_status_code = response.status_code
            if actual_status_code == expected_status_code:
                self.test_obj.yakshaAssert("test_apache_access", True, "functional")
                print("test_apache_access = Passed")
            else:
                self.test_obj.yakshaAssert("test_apache_access", False, "functional")
                print("test_apache_access = Failed")
        except Exception as e:
            self.test_obj.yakshaAssert("test_apache_access", False, "exception")
            print("test_apache_access = Failed due to Exception", str(e))

    def test_apache_default_page(self):
        """Test if the Apache default page contains expected content."""
        try:
            if self.container is None:
                self.test_obj.yakshaAssert("test_apache_default_page", False, "functional")
                print("test_apache_default_page = Failed - Container does not exist")
                return

            response = requests.get("http://localhost:8081")
            expected_content = "It works!"
            actual_content = response.text
            if expected_content in actual_content:
                self.test_obj.yakshaAssert("test_apache_default_page", True, "functional")
                print("test_apache_default_page = Passed")
            else:
                self.test_obj.yakshaAssert("test_apache_default_page", False, "functional")
                print("test_apache_default_page = Failed")
        except Exception as e:
            self.test_obj.yakshaAssert("test_apache_default_page", False, "exception")
            print("test_apache_default_page = Failed due to Exception", str(e))

if __name__ == "__main__":
    unittest.main()
