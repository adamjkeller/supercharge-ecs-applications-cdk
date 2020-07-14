#!/usr/bin/env python3

from aws_cdk import core

from alb_fargate.alb_fargate_stack import AlbFargateStack

app = core.App()
AlbFargateStack(app, "alb-fargate")

app.synth()
