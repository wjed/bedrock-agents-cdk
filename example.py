import boto3
import uuid
import os
import argparse

# agent id and alias id are required via cli
parser = argparse.ArgumentParser()
parser.add_argument("--agent-id", required=True)
parser.add_argument("--alias-id", required=True)
parser.add_argument("--query", default="pancakes")

args = parser.parse_args()
agent_id = args.agent_id
alias_id = args.alias_id
query = args.query

session_id = uuid.uuid4().hex
# verify that AWS_PROFILE is set
assert "AWS_PROFILE" in os.environ, "Please set the AWS_PROFILE environment variable"
runtime_client = boto3.client(
    service_name="bedrock-agent-runtime",
)
response = runtime_client.invoke_agent(
    agentId=agent_id,
    agentAliasId=alias_id,
    sessionId=session_id,
    inputText=f"what's a good recipe for {query} from budget bytes?",
)
completion = ""
# It's a response stream so this is how to extract the text
for event in response.get("completion"):
    chunk = event["chunk"]
    completion += chunk["bytes"].decode()

print(completion)
