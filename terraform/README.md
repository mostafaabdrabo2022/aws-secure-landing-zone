# Terraform

Infrastructure as Code for the landing zone baseline.

```
modules/
  vpc/          VPC, subnets, route tables, IGW, S3 gateway endpoint
  log_bucket/   Hardened S3 bucket (versioning, encryption, public access block)
  scp/          Service Control Policy + attachment
envs/
  prod/         Prod VPC (10.20.0.0/16) in the workload-prod account
  mgmt/         SCPs, applied from the management account
```

## Usage

```bash
aws sso login --profile <profile>
cd envs/prod
terraform init
terraform plan
terraform apply
```

State is stored in an S3 bucket with versioning enabled. State files are never committed (see .gitignore).
