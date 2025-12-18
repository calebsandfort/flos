from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_rds as rds,
    RemovalPolicy,
)
from constructs import Construct

class NetworkDbStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # VPC
        self.vpc = ec2.Vpc(
            self, "FlosVpc",
            max_azs=2,
            nat_gateways=1, # Save cost for dev
        )

        # Security Group for App (API and Worker)
        self.app_security_group = ec2.SecurityGroup(
            self, "AppSecurityGroup",
            vpc=self.vpc,
            description="Security Group for Flos API and Worker",
            allow_all_outbound=True
        )

        # Database
        self.db = rds.DatabaseInstance(
            self, "FlosDB",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_15
            ),
            vpc=self.vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3,
                ec2.InstanceSize.MICRO
            ),
            allocated_storage=20,
            removal_policy=RemovalPolicy.DESTROY, # For dev/demo
            deletion_protection=False,
            database_name="flos"
        )

        # Allow access from App SG
        self.db.connections.allow_default_port_from(
            self.app_security_group,
            "Allow connection from App SG"
        )

        self.db_secret = self.db.secret
