#!/usr/bin/env python3
import os
import aws_cdk as cdk
from stacks.ecr_stack import EcrStack
from stacks.network_db_stack import NetworkDbStack
from stacks.app_stack import AppStack

app = cdk.App()

env = cdk.Environment(
    account=os.getenv("CDK_DEFAULT_ACCOUNT"),
    region=os.getenv("CDK_DEFAULT_REGION")
)

ecr = EcrStack(app, "FlosEcrStack", env=env)
network = NetworkDbStack(app, "FlosNetworkDbStack", env=env)

app_stack = AppStack(app, "FlosAppStack",
    vpc=network.vpc,
    repo_api=ecr.repo_api,
    repo_worker=ecr.repo_worker,
    db=network.db,
    env=env
)

app.synth()
