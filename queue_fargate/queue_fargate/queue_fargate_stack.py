from aws_cdk import core, aws_ecs, aws_ecs_patterns


class QueueFargateStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # The code that defines your stack goes here
        self.fargate_queue_service = aws_ecs_patterns.QueueProcessingFargateService(
            self, "QueueService",
            cpu=512,
            memory_limit_mib=2048,
            image=aws_ecs.ContainerImage.from_asset(
                directory='.',
                file='Dockerfile.queue_service',
                exclude=["cdk.out"]
            ),
            desired_task_count=1
        )
