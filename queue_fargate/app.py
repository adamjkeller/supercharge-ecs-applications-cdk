#!/usr/bin/env python3

from aws_cdk import core

from queue_fargate.queue_fargate_stack import QueueFargateStack


app = core.App()
QueueFargateStack(app, "queue-fargate")

app.synth()
