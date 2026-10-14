variable "scp_name" {
  type        = string
  description = "Name of the Service Control Policy"
}

resource "aws_organizations_policy" "secure_scp" {
  name        = var.scp_name
  description = "Security baseline SCP to prevent disabling core security services"
  type        = "SERVICE_CONTROL_POLICY"

  content = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "DenyDisablingSecurityServices"
        Effect    = "Deny"
        Action    = [
          "cloudtrail:DeleteTrail",
          "guardduty:DisableGuardDuty",
          "iam:DeleteAccountPasswordPolicy"
        ]
        Resource = "*"
      }
    ]
  })
}

output "policy_id" {
  value       = aws_organizations_policy.secure_scp.id
  description = "The ID of the SCP policy"
}