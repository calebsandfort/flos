from aws_cdk import (
    Stack,
    aws_ecr as ecr,
    RemovalPolicy,
)
from constructs import Construct

class EcrStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.repo_api = ecr.Repository(
            self, "ApiRepo",
            repository_name="flos-api",
            removal_policy=RemovalPolicy.DESTROY, # For dev/demo only, usually RETAIN
            empty_on_delete=True
        )

        self.repo_worker = ecr.Repository(
            self, "WorkerRepo",
            repository_name="flos-worker",
            removal_policy=RemovalPolicy.DESTROY,
            empty_on_delete=True
        )
