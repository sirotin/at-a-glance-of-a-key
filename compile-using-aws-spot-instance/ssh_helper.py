import logging
import paramiko
import time

logger = logging.getLogger("builder")

class SSHWrapper(object):
	def __init__(self):
		self.ssh = paramiko.SSHClient()
		self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

		self.connected = False

	def __del__(self):
		if self.connected:
			self.disconnect()

	def connect(self, hostname, username, pem, timeout=60):
		key = paramiko.RSAKey.from_private_key_file(pem)

		try:
			logger.debug("Connecting to %s" % hostname)
			self.ssh.connect(hostname, username=username, pkey=key, timeout=timeout)
			logger.debug("Successfully connected to %s" % hostname)

			self.hostname = hostname
			self.connected = True

			return True

		except Exception as e:
			logger.warn("Failed connecting to %s - retry limit exceeded" % hostname)
			self.hostname = ""
			self.connected = False
			return False

	def disconnect(self):
		if self.connected:
			logger.debug("Disconnecting from %s" % self.hostname)
			self.ssh.close()
			self.hostname = ""
			self.connected = False

	def execute(self, cmd, show_output=True, throw_on_error=True):
		if not(self.connected):
			logger.error("Cannot execute ssh command - not connected")
			return 255

		logger.info("Running on remote host %s: '%s'" % (self.hostname, cmd))
		_, stdout, stderr = self.ssh.exec_command(cmd)
		rc = stdout.channel.recv_exit_status()

		logger.info("Command returned rc=%d" % rc)
		if show_output:
			for line in stdout:
				logger.debug("STDOUT - %s" % line)
			for line in stderr:
				logger.debug("STDERR - %s" % line)

		if throw_on_error and rc != 0:
			raise Exception("Command failed, rc=%d" % rc)

		return rc
