from aws_cdk import core, aws_ecs_patterns, aws_ecs


class AlbFargateStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # The code that defines your stack goes here
        self.wordpress_lb_service = aws_ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "WordPressALBService",
            cpu=512,
            memory_limit_mib=1024,
            listener_port=80,
            task_image_options=aws_ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=aws_ecs.ContainerImage.from_registry('wordpress:latest'),
                container_port=8080
            )
        )
