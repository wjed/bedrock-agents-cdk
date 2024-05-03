"""
Pieced togethere from https://github.com/PieterjanCriel/bedrock-agents-cdk 
and https://github.com/trevorspires/Bedrock-Agents-Demo-Final
as well as https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_bedrock/CfnAgent.html#aws_cdk.aws_bedrock.CfnAgent
Note that you need to be using aws-cdk >= 2.140.0 since that's the first version that has aws_bedrock in it.

This CDK stack is designed to build infrastructure for a Bedrock agent that can be used to search for recipes on the Budget Bytes website.
"""

from aws_cdk import (
    Duration,
    Stack,
    aws_lambda as _lambda,
    CfnOutput,
    aws_iam as iam,
    aws_bedrock as bedrock,
)
import os
from constructs import Construct


class CdkStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create a lambda execution role so the lambda can be invoked
        lambda_role = iam.Role(
            self,
            "LambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
        )

        # Add lambda AWSLambdaBasicExecutionRole managed policy to lambda execution role
        lambda_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AWSLambdaBasicExecutionRole"
            )
        )

        # Create the bundle of python resources to run in the lambda function.
        # We have to do this because we need some custom libs like beautifulsoup
        os.system("pushd lambda && pip install -r requirements.txt -t package && popd")
        os.system(
            "pushd lambda/package && zip -r ../my_deployment_package.zip . && popd"
        )
        os.system(
            "pushd lambda && zip my_deployment_package.zip lambda_function.py && popd"
        )
        # Create a lambda function to handle feature requests from the lambda directory
        lambda_function = _lambda.Function(
            self,
            "DeviceAgentHandler",
            runtime=_lambda.Runtime.PYTHON_3_10,
            handler="lambda_function.lambda_handler",
            code=_lambda.AssetCode("lambda/my_deployment_package.zip"),
            role=lambda_role,
            timeout=Duration.seconds(30),
        )

        # Add a resource based policy to the lambda function
        # This is what will allow bedrock to call the lambda
        principal = iam.ServicePrincipal("bedrock.amazonaws.com")
        lambda_function.add_permission(
            "agent-invoke-lambda", principal=principal, action="lambda:InvokeFunction"
        )

        # create a new bedrock agent, using Claude-3 Haiku
        agent_role = iam.Role(
            self,
            "AgentIamRole",
            role_name="AmazonBedrockExecutionRoleForAgents_" + "budgetbytesAgent",
            assumed_by=iam.ServicePrincipal("bedrock.amazonaws.com"),
            description="Agent role created by CDK.",
        )
        # This agent has permissions to do all things Bedrock
        agent_role.add_to_policy(
            iam.PolicyStatement(
                actions=["*"],
                resources=["arn:aws:bedrock:*"],
            )
        )
        # This is the OpenAPI that the agent will use to validate the input
        with open("assets/recipe-agent-schema.yaml", "r") as file:
            schema = file.read()
        action_group = bedrock.CfnAgent.AgentActionGroupProperty(
            action_group_name="recipeSearch",
            action_group_executor=bedrock.CfnAgent.ActionGroupExecutorProperty(
                lambda_=lambda_function.function_arn
            ),
            # the properties below are optional
            api_schema=bedrock.CfnAgent.APISchemaProperty(payload=schema),
            description="Action that will trigger the lambda",
            skip_resource_in_use_check_on_delete=False,
        )

        # At long last, create the bedrock agent!
        cfn_agent = bedrock.CfnAgent(
            self,
            "budgetbytesAgent",
            agent_name="budgetbytesAgent",
            # the properties below are optional
            action_groups=[action_group],
            auto_prepare=True,
            description="Chat and get recipes",
            foundation_model="anthropic.claude-3-haiku-20240307-v1:0",
            instruction="You are a cooking recipe generation chatbot.",
            agent_resource_role_arn=agent_role.role_arn,
        )
        """
        An alias points to a specific version of your Agent. Once you create and associate a version with an alias, you can test it. 
        With an alias, you can also update the Agent version that your client applications use.
        """
        cfn_agent_alias = bedrock.CfnAgentAlias(
            self,
            "recipeAgentAlias",
            agent_alias_name="recipeAgent",
            agent_id=cfn_agent.attr_agent_id,
        )

        # Print out the values which will need to be used if someone plans to invoke the model
        CfnOutput(self, "AgentId", value=cfn_agent.attr_agent_id)
        CfnOutput(self, "AgentAliasId", value=cfn_agent_alias.attr_agent_alias_id)
