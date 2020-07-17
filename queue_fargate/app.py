#!/usr/bin/env python3

from aws_cdk import core
from os import environ

from queue_fargate.queue_fargate_stack import QueueFargateStack

_env=core.Environment(account=environ["CDK_DEFAULT_ACCOUNT"], region=environ["CDK_DEFAULT_REGION"])
app = core.App()
QueueFargateStack(app, "queue-fargate", env=_env)

app.synth()
