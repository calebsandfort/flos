from aws_cdk import (
    Stack,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_ecr as ecr,
    aws_secretsmanager as secretsmanager,
    CfnOutput,
)
from constructs import Construct

class AppStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, 
                 vpc: ec2.Vpc, 
                 repo_api: ecr.Repository, 
                 repo_worker: ecr.Repository,
                 db: rds.DatabaseInstance,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        cluster = ecs.Cluster(self, "FlosCluster", vpc=vpc)
        
        # Security Group for App (API and Worker)
        security_group = ec2.SecurityGroup(
            self, "AppSecurityGroup",
            vpc=vpc,
            description="Security Group for Flos API and Worker",
            allow_all_outbound=True
        )
        
        # Allow DB access
        # This creates the rule in the AppStack using a low-level construct
        # avoiding the cyclic dependency that occurs when using db.connections.allow... 
        # (which tries to modify the NetworkStack)
        ec2.CfnSecurityGroupIngress(
            self, "DbIngressFromApp",
            group_id=db.connections.security_groups[0].security_group_id,
            source_security_group_id=security_group.security_group_id,
            ip_protocol="tcp",
            from_port=5432,
            to_port=5432,
            description="Allow access from App SG"
        )
        
        db_secret = db.secret

        # Define environment variables (DB Connection)
        environment = {
            "ENVIRONMENT": "production"
        }
        
        secrets = {
            "DB_SECRET": ecs.Secret.from_secrets_manager(db_secret) # Pass the whole JSON
        }

        # The app will need to be smart enough to parse this or we change the app to use `aws-env` etc.
        # Or we map:
        env_secrets = {
            "POSTGRES_USER": ecs.Secret.from_secrets_manager(db_secret, "username"),
            "POSTGRES_PASSWORD": ecs.Secret.from_secrets_manager(db_secret, "password"),
            "POSTGRES_HOST": ecs.Secret.from_secrets_manager(db_secret, "host"),
            "POSTGRES_PORT": ecs.Secret.from_secrets_manager(db_secret, "port"),
        }
        
        # Add explicit DB name to environment since it's not guaranteed in the generated secret
        environment["POSTGRES_DB"] = "flos"


        # API Task Definition
        task_def_api = ecs.FargateTaskDefinition(
            self, "ApiTaskDef",
            cpu=256,
            memory_limit_mib=512,
        )

        container_api = task_def_api.add_container(
            "ApiContainer",
            image=ecs.ContainerImage.from_ecr_repository(repo_api, "latest"),
            container_port=8000,
            logging=ecs.LogDriver.aws_logs(stream_prefix="flos-api"),
            environment=environment,
            secrets=env_secrets,
        )

        # Allow Inbound 8000 (We need to do this on the SG)
        security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(8000),
            "Allow API access from anywhere"
        )

        # API Service (Public IP, No LB)
        self.api_service = ecs.FargateService(
            self, "ApiService",
            cluster=cluster,
            task_definition=task_def_api,
            desired_count=1,
            assign_public_ip=True,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            security_groups=[security_group]
        )
        
        # Output Service Name so we can find it
        CfnOutput(self, "ApiServiceName", value=self.api_service.service_name)

        # Worker Service (No Load Balancer)
        task_def_worker = ecs.FargateTaskDefinition(
            self, "WorkerTaskDef",
            cpu=256,
            memory_limit_mib=512,
        )
        
        container_worker = task_def_worker.add_container(
            "WorkerContainer",
            image=ecs.ContainerImage.from_ecr_repository(repo_worker, "latest"),
            logging=ecs.LogDriver.aws_logs(stream_prefix="flos-worker"),
            environment=environment,
            secrets=env_secrets,
        )

        self.worker_service = ecs.FargateService(
            self, "WorkerService",
            cluster=cluster,
            task_definition=task_def_worker,
            desired_count=1,
            security_groups=[security_group] # Shared SG
        )


        CfnOutput(self, "ClusterName", value=cluster.cluster_name)
        CfnOutput(self, "WorkerTaskDefArn", value=task_def_worker.task_definition_arn)
        CfnOutput(self, "AppSecurityGroupId", value=security_group.security_group_id)
        CfnOutput(self, "AppSubnetIds", value=",".join([s.subnet_id for s in vpc.private_subnets]))

