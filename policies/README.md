# IAM policy library

Least-privilege example policies written during Week 2. Each file is a standalone IAM policy JSON.

| File | Purpose |
|---|---|
| s3-readonly-single-bucket.json | Read-only access to one bucket |
| ec2-start-stop-dev-tag.json | Start/stop only EC2 instances tagged Environment=dev |
| deny-outside-region.json | Deny actions outside the allowed Region |
| cloudwatch-logs-readonly.json | Read-only CloudWatch Logs |
| ssm-session-only.json | Session Manager access to dev-tagged instances |

Identity-based policies attach to a user, group or role. Resource-based policies attach to the resource (a bucket policy, a role trust policy).
