#! /usr/bin/python

import sys
import time
import logging
from aws_wrapper import AwsWrapper
from ssh_helper import SSHWrapper

logger = logging.getLogger("builder")
hdlr = logging.StreamHandler(stream=sys.stdout)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)

class Settings:
	Id = "AWS_ACCESS_KEY_ID"
	Secret = "AWS_SECRET_ACCESS_KEY"
	Region = "eu-west-1" # Ireland
	AvailabilityZone = "eu-west-1a" # Availability zone within the region (where the EBS volume located)

	InstanceName = "alexander-builder"
	InstanceOwner = "Alexander Sirotin"

	KeyPair = "key-pair-name"
	SecurityGroup = "sg-xxxxxx"
	AmiId = "ami-xxxxxx"
	EniId = "eni-xxxxxx"
	DataVolume = "vol-xxxxxx"

	UserName = "ubuntu"

	InstanceType = "c4.2xlarge"
	Price = 0.15

if __name__ == "__main__":
	settings = Settings()

	aws = AwsWrapper(settings)
	aws.createInstance()
	aws.prepareInstance()
