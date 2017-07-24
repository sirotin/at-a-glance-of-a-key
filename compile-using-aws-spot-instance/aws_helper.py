# Author: Alexander Sirotin / sirotin@gmail.com
# Copyright (c) 2017 Alexander Sirotin.
# Licensed under MIT license:
# https://opensource.org/licenses/mit-license.php
# Your use is on an "AS-IS" basis, and subject to the terms and conditions of this license.

import time
import logging
import boto.ec2

logger = logging.getLogger("builder")

class AwsHelper:
	def __init__(self, ec2, settings):
		self.ec2 = ec2
		self.settings = settings

	def checkSpotRequestState(self, sir_id):
		logger.debug("Checking spot request: %s" % sir_id)

		active_requests = self.ec2.get_all_spot_instance_requests()
		for sir in active_requests:
			if (sir_id == sir.id):
				logger.debug("Spot request %s is in state %s" % (sir_id, sir.state))
				return sir

		logger.warn("Cannot find an active request for %s" % sir_id)
		return None

	def getInstanceIdFromSpotRequest(self, sir_id, timeout):
		instance_id = None
		retries = timeout
		while (retries > 0):
			sir = self.checkSpotRequestState(sir_id)
			if (sir != None):
				if (sir.state.lower() == "active"):
					instance_id = sir.instance_id
					break

			retries -= 2
			time.sleep(2)

		return instance_id

	def prepareInstance(self, instance_id):
		instance = self.getInstanceObject(instance_id)

		logger.info("Waiting for instance %s to be running" % instance_id)
		is_running = self.waitForRunningState(instance, timeout=120)
		if not(is_running):
			logger.warn("Instance %s is not running, terminating the instance" % instance_id)
			self.terminateInstance(instance_id)
			return None

		logger.info("Tagging instance %s" % instance_id)
		self.tagInstance(instance, self.settings.InstanceName)

		logger.info("Attaching volume %s" % self.settings.DataVolume)
		attached = self.ec2.attach_volume(volume_id=self.settings.DataVolume, instance_id=instance_id, device="/dev/sdf")
		if not(attached):
			logger.warn("Failed attaching volume %s to instance %s" % (self.settings.DataVolume, instance_id))
			self.terminateInstance(instance_id)
			return None

		logger.info("Instance %s was successfully created (ip: %s)" % (instance_id, instance.private_ip_address))
		return instance

	def cancelSpotRequest(self, sir_id):
		try:
			logger.warn("Canceling spot request %s" % sir_id)
			self.ec2.cancel_spot_instance_requests([sir_id])
		except Exception as e:
			logger.error("Failed canceling spot request: %d - %s (%s)" % (e.status, e.error_code, e.reason))
			return None

	def getInstanceObject(self, instance_id):
		try:
			result = self.ec2.get_all_instances([instance_id])
			instance = result[0].instances[0]
			return instance

		except Exception as e:
			logger.error("Failed getting instance: %d - %s (%s)" % (e.status, e.error_code, e.reason))
			return None

	def waitForRunningState(self, instance, timeout):
		if (instance == None):
			return False

		status = ""
		retries = timeout
		while (retries > 0):
			status = instance.update()
			if (status.lower() == "running"):
				logger.info("Instance %s is in running state" % instance.id)
				return True

			retries -= 5
			time.sleep(5)

		logger.warn("Failed waiting for instance %s to be in running state (state: %s)" % (instance.id, status))
		return False

	def tagInstance(self, instance, name):
		if (instance == None):
			return False

		status = instance.update()
		if (status.lower() != "running"):
			logger.warn("Cannot mark instance %s in status: %s" % (instance.id, status))
			return False

		instance.add_tag("Name", name)
		instance.add_tag("Owner", self.settings.InstanceOwner)
		return True

	def waitForHealthchecks(self, instance, timeout):
		if (instance == None):
			return False

		logger.debug("Waiting until instance %s will become healthy (timeout: %d seconds)" % (instance.id, timeout))
		retries = timeout
		while (retries > 0):
			health = self.ec2.get_all_instance_status([instance.id])
			instance_status = health[0].instance_status.status.lower()
			system_status = health[0].system_status.status.lower()

			if (instance_status == "ok") and (system_status == "ok"):
				logger.info("Instance %s health is ok" % instance.id)
				return True

			retries -= 5
			time.sleep(5)

		logger.warn("Instance %s health is not ok after the given timeout (instance: %s, system: %s)" % (instance.id, instance_status, system_status))
		return False

	def requestSpotInstance(self):
		eni = boto.ec2.networkinterface.NetworkInterfaceSpecification(network_interface_id=self.settings.EniId,
																	  device_index=0,
																	  delete_on_termination=False)
		network_interfaces = boto.ec2.networkinterface.NetworkInterfaceCollection(eni)

		logger.info("Requesting spot instance of type %s" % self.settings.InstanceType)
		req = self.ec2.request_spot_instances(price=self.settings.Price,
		                                      image_id=self.settings.AmiId,
		                                      instance_type=self.settings.InstanceType,
		                                      availability_zone_group=self.settings.Region,
											  placement=self.settings.AvailabilityZone,
		                                      key_name=self.settings.KeyPair,
											  network_interfaces=network_interfaces)

		sir_id = req[0].id
		instance_id = self.getInstanceIdFromSpotRequest(sir_id, timeout=120)
		if (instance_id == None):
			logger.warn("Spot request %s completed with failure, canceling the request" % sir_id)
			self.helper.cancelSpotRequest(sir_id)
			return

		logger.info("Spot request completed, instance id: %s" % instance_id)
		instance = self.prepareInstance(instance_id)

		return instance
