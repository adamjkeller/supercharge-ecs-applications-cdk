#!/usr/bin/env python3

from aws_cdk import core

from scheduled_task_fargate.scheduled_task_fargate_stack import ScheduledTaskFargateStack


app = core.App()
ScheduledTaskFargateStack(app, "scheduled-task-fargate")

app.synth()
