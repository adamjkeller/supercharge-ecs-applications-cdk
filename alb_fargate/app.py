#!/usr/bin/env python3

import os
from aws_cdk import core

from alb_fargate.alb_fargate_stack import AlbFargateStack

_env=core.Environment(account=os.environ["CDK_DEFAULT_ACCOUNT"],region=os.environ["CDK_DEFAULT_REGION"])
app = core.App()
AlbFargateStack(app, "alb-fargate", env=_env)

app.synth()
