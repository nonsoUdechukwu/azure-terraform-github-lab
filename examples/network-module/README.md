# Network module v1.0.0

Creates one VNet and one standalone subnet per `subnets` map entry.
Never add inline `subnet` blocks to this VNet: mixing inline and standalone
subnets causes conflicting management.

Requires Terraform >=1.15.3,<2 and AzureRM >=4.50.0,<5. The root configures the
provider. `default_outbound_access_enabled = false` is intentional; this empty
network does not provide workloads with an outbound internet design.

| Input | Type | Required/default |
|---|---|---|
| name, resource_group_name, location | string | Required |
| address_space | list(string) | Required |
| subnets | map(object({name=string,address_prefixes=list(string)})) | Required |
| tags | map(string) | `{}` |

Outputs: `vnet_id`, `subnet_ids` (map keyed by input subnet keys).
There is **no `subnet_names` output in v1.0.0**.

For a complete caller, see [the live reference](../live/environments/dev/main.tf)
in the course repository. When copying this README to your independent module
repository, replace this relative link with your live repository's GitHub URL.

Run `terraform init -backend=false`, `terraform validate`, `terraform test`.
Mock tests do not contact Azure. Validate real address ranges and organizational
network rules before using this outside the lab.
