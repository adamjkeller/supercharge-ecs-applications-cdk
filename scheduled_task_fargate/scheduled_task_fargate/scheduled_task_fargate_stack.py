from aws_cdk import core, aws_ecs, aws_ecs_patterns, aws_applicationautoscaling, aws_sqs


class ScheduledTaskFargateStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.scheduled_task_fargate = aws_ecs_patterns.ScheduledFargateTask(
            self, "ScheduledQueueTask",
            scheduled_fargate_task_image_options=aws_ecs_patterns.ScheduledFargateTaskImageOptions(
                image=aws_ecs.ContainerImage.from_asset(
                    directory='.',
                    file='Dockerfile.queue_service',
                    exclude=["cdk.out"]
                ),
                command=["/queue_service.py", "send"],
                environment={
                    'QUEUE_NAME': 'queue-fargate-QueueServiceEcsProcessingQueue354FA9E5-1GJOWKT1W18XX'
                },
            ),
            schedule=aws_applicationautoscaling.Schedule.rate(
                core.Duration.seconds(60)
            )
        )
        
        #DYNAMICALLY PULL THIS DOWN
        sqs_queue = aws_sqs.Queue.from_queue_arn(
            self, "Queue",
            "arn:aws:sqs:us-west-2:317933635802:queue-fargate-QueueServiceEcsProcessingQueue354FA9E5-1GJOWKT1W18XX"
            #core.Fn.import_value('QueueServiceSQSQueueArnAC83255E')
        )
        
        sqs_queue.grant_send_messages(self.scheduled_task_fargate.task_definition.task_role)