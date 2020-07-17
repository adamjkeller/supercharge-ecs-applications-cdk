## Deploy a Fargate SQS queue consumer 

#### Prerequisites

- npm, python3.x

```bash
npm i -g aws-cdk@1.51.0
pip install -r requirements.txt
```

#### Meet the application

We will be deploying a simple python application that will consume messages from an [SQS Queue](https://aws.amazon.com/sqs/). This application will poll the message queue for any new messages and process them by simply printing the message content.
The docker image calls the python application via the CMD instruction defined in the Dockerfile, and passes the receive parameter to the application. Let's look at the Dockerfile CMD:

```Bash
CMD ["/queue_service.py","receive"]
```

The receive method is straightforward and simple. As you can see, we grab the queue by name via an environment variable, and then iterate over messages in a while loop.
```python
def get_queue_details():
    sqs = resource('sqs')
    return sqs.get_queue_by_name(QueueName=getenv('QUEUE_NAME'))

def receive():
    queue = get_queue_details()
    while True:
        for message in queue.receive_messages():
            print("MESSAGE CONSUMED: {}".format(message.body))
            print(message.delete())
            sleep(1)
```

#### CDK Code review

Now that we understand the application, let's see how we get it from an idea to a real world environment in AWS.
First, let's look at the `app.py`, as this is the "main" or entrypoint to define our cdk app(s).

The core module is what we will use to instantiate our cdk app(s), as well as synthesize the code into the assembly Cloudformation templates.
```python
#!/usr/bin/env python3

from aws_cdk import core
```
Next, we are importing our stack class QueueFargateStack, which is where we are defining our resources to be built within the Stack.
We then instantiate the cdk app, call our QueueFargateStack class, pass in the scope of the cdk app as well as the name of the stack, and lastly synthesize the app. The synth() call is ultimately what will compile our code into CloudFormation.
```python
from queue_fargate.queue_fargate_stack import QueueFargateStack

app = core.App()
QueueFargateStack(app, "queue-fargate")

app.synth()
```

Ok, now let's get into the code that actually defines our environment. Spoiler alert, a lot is going to get built with not a whole lot of code :-)

Breaking this down, we will import the ecs and ecs_patterns modules which will provide us with the constructs to build our resources. 
```python
from aws_cdk import core, aws_ecs, aws_ecs_patterns
```

In our class, we are defining the resources we want to build via constructs. The [QueueProcessingFargateService](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-ecs-patterns.QueueProcessingFargateService.html) construct is going to do a lot of work for us, while asking for very little in return :-)

We are passing in some basic requirements such as cpu, memory, the container image we want deployed, as well as how many tasks we want running.
Do you notice that I am not pointing to any particular docker repository? This is because within the [ContainerImage](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-ecs.ContainerImage.html) construct, we can point to an asset (Dockerfile) on disk, and the cdk will build the image, ECR repository, and push the image up for us. Neat, right? So long clunky bash docker build/deploy logic!

That's it. In 10 lines of python code, I am building a docker image, an ECR repo, a vpc (with all resources included, like subnets, route tables, etc), a queue and dead letter queue in SQS, and all the rest of the boilerplate to connect all of the pieces together. Oh, and it also includes autoscaling built in. Yes, you heard right, autoscaling is built in.
```python
class QueueFargateStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.fargate_queue_service = aws_ecs_patterns.QueueProcessingFargateService(
            self, "QueueService",
            cpu=512,
            memory_limit_mib=2048,
            image=aws_ecs.ContainerImage.from_asset(
                directory='.',
                exclude=["cdk.out"]
            ),
            desired_task_count=1
        )

```

Now I understand that this may not be enough on its own for every use case, and the beauty of the cdk is you can use the attributes available to extend the underlying components as needed. For example, if you want to modify the autoscaling max capacity, you can do so via the [max_capacity](https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ecs_patterns/QueueProcessingFargateService.html#aws_cdk.aws_ecs_patterns.QueueProcessingFargateService.max_capacity) attribute.

Ok, so now we have a good grasp on what we're building and how we're defining the components. Let's deploy it.

#### Deploy the environment

First step is to confirm that we can synthesize the assembly code

```bash
cdk synth
```

The output should contain a lot of Cloudformation. This means that the cdk was able to translate our code into the lower level assembly Cloudformation.

Ok, let's look at a couple of snippets of CloudFormation and explain what is happening. Below, you can see that the cdk generated the Cloudformation for my SQS queue, as well as the DLQ, and connected them together.

```json
    "QueueServiceEcsProcessingDeadLetterQueueCDE7AAF7": {
      "Type": "AWS::SQS::Queue",
      "Properties": {
        "MessageRetentionPeriod": 1209600
      },
      "Metadata": {
        "aws:cdk:path": "queue-fargate/QueueService/EcsProcessingDeadLetterQueue/Resource"
      }
    },
    "QueueServiceEcsProcessingQueue354FA9E5": {
      "Type": "AWS::SQS::Queue",
      "Properties": {
        "RedrivePolicy": {
          "deadLetterTargetArn": {
            "Fn::GetAtt": [
              "QueueServiceEcsProcessingDeadLetterQueueCDE7AAF7",
              "Arn"
            ]
          },
          "maxReceiveCount": 3
        }
      },
      "Metadata": {
        "aws:cdk:path": "queue-fargate/QueueService/EcsProcessingQueue/Resource"
      }
    },
```

Looks good so far, let's run a diff to see what will actually be deployed.

```bash
cdk diff
```

Because we haven't deployed anything yet, everything will be new, and you'll see all the proposed changes in the output. Here is a snippet of what that looks like:

```
Resources
[+] AWS::SQS::Queue QueueService/EcsProcessingDeadLetterQueue QueueServiceEcsProcessingDeadLetterQueueCDE7AAF7 
[+] AWS::SQS::Queue QueueService/EcsProcessingQueue QueueServiceEcsProcessingQueue354FA9E5 
[+] AWS::IAM::Role QueueService/QueueProcessingTaskDef/TaskRole QueueServiceQueueProcessingTaskDefTaskRoleBE3B7BDD 
[+] AWS::IAM::Policy QueueService/QueueProcessingTaskDef/TaskRole/DefaultPolicy QueueServiceQueueProcessingTaskDefTaskRoleDefaultPolicy460AE3C0 
[+] AWS::ECS::TaskDefinition QueueService/QueueProcessingTaskDef QueueServiceQueueProcessingTaskDef3543A790 
[+] AWS::Logs::LogGroup QueueService/QueueProcessingTaskDef/QueueProcessingContainer/LogGroup QueueServiceQueueProcessingTaskDefQueueProcessingContainerLogGroup17F34FDA 
[+] AWS::IAM::Role QueueService/QueueProcessingTaskDef/ExecutionRole QueueServiceQueueProcessingTaskDefExecutionRole6B164E94 
[+] AWS::IAM::Policy QueueService/QueueProcessingTaskDef/ExecutionRole/DefaultPolicy QueueServiceQueueProcessingTaskDefExecutionRoleDefaultPolicyCF36A0AF 
[+] AWS::ECS::Service QueueService/QueueProcessingFargateService/Service QueueServiceQueueProcessingFargateService18D74DE3 
[+] AWS::EC2::SecurityGroup QueueService/QueueProcessingFargateService/SecurityGroup QueueServiceQueueProcessingFargateServiceSecurityGroupB0BF1DFD 
[+] AWS::ApplicationAutoScaling::ScalableTarget QueueService/QueueProcessingFargateService/TaskCount/Target QueueServiceQueueProcessingFargateServiceTaskCountTargetF12D965F 
[+] AWS::ApplicationAutoScaling::ScalingPolicy QueueService/QueueProcessingFargateService/TaskCount/Target/CpuScaling QueueServiceQueueProcessingFargateServiceTaskCountTargetCpuScaling52636849 
[+] AWS::ApplicationAutoScaling::ScalingPolicy QueueService/QueueProcessingFargateService/TaskCount/Target/QueueMessagesVisibleScaling/LowerPolicy QueueServiceQueueProcessingFargateServiceTaskCountTargetQueueMessagesVisibleScalingLowerPolicyEAB08C8E 
```

Ok, deploy time!

```bash
cdk deploy --require-approval never
```

Enjoy the output in the terminal as you watch the resources get built. Once it's done, let's go for a spin in the console and see all that was built.

The output should look something like this once it's done:

```
   queue-fargate

Outputs:
queue-fargate.QueueServiceSQSQueueArnAC83255E = arn:aws:sqs:us-west-2:111111111111:queue-fargate-QueueServiceEcsProcessingQueue354FA9E5-12LSY80PDJA90
queue-fargate.QueueServiceSQSDeadLetterQueueArnA35E4048 = arn:aws:sqs:us-west-2:111111111111:queue-fargate-QueueServiceEcsProcessingDeadLetterQueueCDE7AAF7-1PDHO9XLIBWNV
queue-fargate.QueueServiceSQSDeadLetterQueueDC6D0C1E = queue-fargate-QueueServiceEcsProcessingDeadLetterQueueCDE7AAF7-1PDHO9XLIBWNV
queue-fargate.QueueServiceSQSQueue650B4850 = queue-fargate-QueueServiceEcsProcessingQueue354FA9E5-12LSY80PDJA90
```


#### Review in the console