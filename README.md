
# Bedrock Agents with AWS CDK

This is how to deploy all the infrastructure needed to deploy a Bedrock Agent with a single lambda function action that pulls study resources from AWS.com. Hopefully this is helpful to be adapted to more complex uses of Bedrock Agents and simplifies the process of getting started.

What is [AWS CDK](https://docs.aws.amazon.com/cdk/v2/guide/home.html)? Basically it's an alternative to Terraform. As of 5/3/2024, Terraform doesn't yet support bedrock agents, so CDK is one of the few options available for infrastructure as code (IaC) when it comes to bedrock. AWS CDK can be written in Python and is used to create AWS CloudFormation templates which are then deployed to create the necessary AWS resources.

## Prerequisites
* Mac or linux, untested on Windows but you can try in git bash or a miniconda terminal
* Install AWS CDK CLI and follow the get started guide to get the proper permissions enabled in your AWS account
    - https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html
* Install miniconda for python https://docs.anaconda.com/free/miniconda/miniconda-install/

## Quick Start

```bash
conda create -n bedrock-agents python=3 -y
conda activate bedrock-agents
pip install -r requirements.txt
cdk bootstrap # This will add the CDK roles to enable CDK to work in the account
cdk deploy # Deploys the bedrock agent infrastructure to your account
```
All the infrastructure is in place! Now, to test it, copy the agent id and alias ID outputted at the end of the `cdk deploy` command. It will look something like 
```txt
Outputs:
CdkStack.AgentAliasId = SIJ6NAPWJB
CdkStack.AgentId = BV8OL8URO7
```

Then run the example script to test it out. You'll need to use your own ID and alias ID values
```bash
python example.py --agent-id BV8OL8URO7 --alias-id SIJ6NAPWJB --query "IAM basics"
```

Once you're done, tear down the infrastructure with
```bash
cdk destroy # Remove the resources that were used
```



