import sys
import json
import pulumi
from pulumi import automation as auto
from pulumi_aws import dynamodb


# Inline Pulumi program
def pulumi_program():
    table = dynamodb.Table("my-table",
        attributes=[
            dynamodb.TableAttributeArgs(
                name="id",
                type="S"
            )
        ],
        hash_key="id",
        billing_mode="PAY_PER_REQUEST",  # On-demand billing
    )

    pulumi.export("table_name", table.name)


# Handle CLI args
destroy = False
if len(sys.argv) > 1 and sys.argv[1] == "destroy":
    destroy = True

project_name = "inline_dynamodb_project"
stack_name = "dev"

stack = auto.create_or_select_stack(
    stack_name=stack_name,
    project_name=project_name,
    program=pulumi_program,
)

print("✅ Stack initialized")

print("📦 Installing AWS plugin...")
stack.workspace.install_plugin("aws", "v4.0.0")
print("✅ Plugin installed")

print("🔧 Setting AWS region...")
stack.set_config("aws:region", auto.ConfigValue(value="us-west-2"))
print("✅ Config set")

print("🔄 Refreshing stack...")
stack.refresh(on_output=print)
print("✅ Refresh complete")

if destroy:
    print("🧨 Destroying stack...")
    stack.destroy(on_output=print)
    print("✅ Stack destroyed")
    sys.exit(0)

print("🚀 Updating stack...")
up_res = stack.up(on_output=print)
print(f"\n📊 Update Summary:\n{json.dumps(up_res.summary.resource_changes, indent=4)}")
print(f"🔗 DynamoDB Table Name: {up_res.outputs['table_name'].value}")
