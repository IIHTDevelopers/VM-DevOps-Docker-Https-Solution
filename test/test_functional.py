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

        try:
            cls.container = cls.client.containers.get("httpd-container")
            print(f"Found existing container: {cls.container.name}")
            cls.wait_for_container_to_be_running()
        except docker.errors.NotFound:
            print("Container 'httpd-container' not found. Tests will fail.")
            cls.test_obj.yakshaAssert("container_exists", False, "functional")
            cls.container = None

    @classmethod
    def tearDownClass(cls):
        if cls.container is None:
            print("Tests complete. No container was found to clean up.")
        else:
            print("Tests complete. Container remains unchanged.")

    @classmethod
    def wait_for_container_to_be_running(cls, timeout=30):
        if cls.container is None:
            print("Cannot wait - container does not exist")
            return

        start_time = time.time()
        while time.time() - start_time < timeout:
            cls.container.reload()
            if cls.container.status == 'running':
                print(f"Container {cls.container.name} is now running.")
                return
            print(f"Waiting for container {cls.container.name} to start...")
            time.sleep(2)
        raise Exception(f"Container {cls.container.name} did not start in {timeout} seconds.")

    def test_container_running(self):
        try:
            if self.container is None:
                self.test_obj.yakshaAssert("test_container_running", False, "functional")
                print("test_container_running = Failed - No container")
                return

            self.container.reload()
            if self.container.status == "running":
                self.test_obj.yakshaAssert("test_container_running", True, "functional")
                print("test_container_running = Passed")
            else:
                self.test_obj.yakshaAssert("test_container_running", False, "functional")
                print("test_container_running = Failed")
        except Exception as e:
            self.test_obj.yakshaAssert("test_container_running", False, "exception")
            print("test_container_running = Failed - Exception:", str(e))

    def test_apache_installed(self):
        try:
            if self.container is None:
                self.test_obj.yakshaAssert("test_apache_installed", False, "functional")
                print("test_apache_installed = Failed - No container")
                return

            result = self.container.exec_run("httpd -v")
            output = result.output.decode()
            if "Apache" in output:
                self.test_obj.yakshaAssert("test_apache_installed", True, "functional")
                print("test_apache_installed = Passed")
            else:
                self.test_obj.yakshaAssert("test_apache_installed", False, "functional")
                print("test_apache_installed = Failed")
        except Exception as e:
            self.test_obj.yakshaAssert("test_apache_installed", False, "exception")
            print("test_apache_installed = Failed - Exception:", str(e))

    def test_apache_service_running(self):
        try:
            if self.container is None:
                self.test_obj.yakshaAssert("test_apache_service_running", False, "functional")
                print("test_apache_service_running = Failed - No container")
                return

            result = self.container.exec_run("pgrep -fl httpd")
            output = result.output.decode()
            if len(output) > 0:
                self.test_obj.yakshaAssert("test_apache_service_running", True, "functional")
                print("test_apache_service_running = Passed")
            else:
                self.test_obj.yakshaAssert("test_apache_service_running", False, "functional")
                print("test_apache_service_running = Failed")
        except Exception as e:
            self.test_obj.yakshaAssert("test_apache_service_running", False, "exception")
            print("test_apache_service_running = Failed - Exception:", str(e))

    def test_apache_access(self):
        try:
            if self.container is None:
                self.test_obj.yakshaAssert("test_apache_access", False, "functional")
                print("test_apache_access = Failed - No container")
                return

            response = requests.get("http://localhost:8081")
            if response.status_code == 200:
                self.test_obj.yakshaAssert("test_apache_access", True, "functional")
                print("test_apache_access = Passed")
            else:
                self.test_obj.yakshaAssert("test_apache_access", False, "functional")
                print("test_apache_access = Failed")
        except Exception as e:
            self.test_obj.yakshaAssert("test_apache_access", False, "exception")
            print("test_apache_access = Failed - Exception:", str(e))

    def test_apache_default_page(self):
        try:
            if self.container is None:
                self.test_obj.yakshaAssert("test_apache_default_page", False, "functional")
                print("test_apache_default_page = Failed - No container")
                return

            response = requests.get("http://localhost:8081")
            if "It works!" in response.text:
                self.test_obj.yakshaAssert("test_apache_default_page", True, "functional")
                print("test_apache_default_page = Passed")
            else:
                self.test_obj.yakshaAssert("test_apache_default_page", False, "functional")
                print("test_apache_default_page = Failed")
        except Exception as e:
            self.test_obj.yakshaAssert("test_apache_default_page", False, "exception")
            print("test_apache_default_page = Failed - Exception:", str(e))


# 🔐 Function to trigger test runs externally
def run_all_tests():
    unittest.main(module=__name__, exit=False)
