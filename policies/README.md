# IAM Policy Library

This library documents the least-privilege identity-based policies, resource-based bucket policies, and security boundary controls engineered and deployed during the project. Each policy enforces strict cloud security baselines, ABAC tagging strategies, and administrative segregation of duties.

| Policy Category & File Name | Target Entity / Resource | Core Purpose & Scope |
| :--- | :--- | :--- |
| **`Policy-DevOps-Dev-TagBased.json`** | `DevOps-Dev` Group | Network infrastructure management coupled with mandatory "Dev" tag enforcement. |
| **`Policy-Allow-Assume-ProdRole.json`** | `DevOps-Prod` Group | STS temporary privilege elevation via secure production role assumption. |
| **`Policy-Prod-FullAccess-Tagged.json`** | `Role-Production-Admin` | Strict ABAC production control requiring explicit "Prod" resource tags. |
| **`PermissionBoundary.json`** | IAM Users & Roles | Enterprise SCP simulation capping maximum permissions and enforcing regional geofencing. |
| **`my-cloud-app-bucket-2027.json`** | Central S3 Audit Bucket | Secure logging destination policy for VPC Flow Logs and CloudTrail. |
| **`aws-config-251880984053-2026.json`** | AWS Config S3 Bucket | Compliance tracking and configuration history delivery authorization. |

Identity-based policies attach directly to users, groups, or roles, whereas resource-based policies attach directly to resources such as S3 buckets.

---

### 1. Central Logging & Audit S3 Bucket Policy (`my-cloud-app-bucket-2027`)

This S3 bucket policy governs the centralized auditing and logging bucket. It securely permits AWS services—specifically Amazon VPC Flow Log delivery (`delivery.logs.amazonaws.com`) and AWS CloudTrail (`cloudtrail.amazonaws.com`)—to write operational logs and audit trails into structured account and organization paths. Furthermore, it enforces strict encryption in transit by denying any non-SSL (HTTP) requests.

| Statement SID | Purpose & Description | Allowed / Denied Operations | Security Condition / Guardrail |
| --- | --- | --- | --- |
| **AWSLogDeliveryWrite1** | Grants log delivery services permission to write VPC flow log objects into the account log path. | **Allow:** `s3:PutObject` | Restricted to source account ID and forces bucket-owner full control ACL. |
| **AWSLogDeliveryAclCheck1** | Allows log delivery services to verify bucket ACLs prior to writing network logs. | **Allow:** `s3:GetBucketAcl` | Restricted to source account ID and specific VPC log service ARNs. |
| **AWSCloudTrailAclCheck** | Permits CloudTrail to perform ACL checks on the central auditing bucket. | **Allow:** `s3:GetBucketAcl` | Restricted to the official organizational trail (`lz-org-trail`). |
| **AWSCloudTrailWriteAccount / Org** | Grants CloudTrail permission to archive account and organizational API activity logs securely. | **Allow:** `s3:PutObject` | Must match the specific CloudTrail ARN and require bucket-owner full control. |
| **AllowSSLRequestsOnly** | Explicit Security Guardrail: Enforces secure transport (HTTPS) for all interactions with the bucket. | **Deny:** `s3:*` on bucket and objects | Denies all actions if `aws:SecureTransport` is set to `false`. |

**Policy JSON:** `/policies/my-cloud-app-bucket-2027.json`

---

### 2. AWS Config S3 Bucket Policy (`aws-config-251880984053-2026`)

This S3 bucket policy is dedicated to the AWS Config storage bucket. It authorizes the AWS Config service (`config.amazonaws.com`) to evaluate permissions, verify bucket existence, and deliver resource configuration history logs securely, while enforcing strict HTTPS transport security.

| Statement SID | Purpose & Description | Allowed / Denied Operations | Security Condition / Guardrail |
| --- | --- | --- | --- |
| **AWSConfigBucketPermissionsCheck** | Allows AWS Config to check bucket ACL configurations. | **Allow:** `s3:GetBucketAcl` | Restricted to the designated AWS source account ID. |
| **AWSConfigBucketExistenceCheck** | Permits AWS Config to verify bucket existence and list its structure. | **Allow:** `s3:ListBucket` | Restricted to the designated AWS source account ID. |
| **AWSConfigBucketDelivery** | Authorizes AWS Config to write resource configuration history items to the storage path. | **Allow:** `s3:PutObject` | Scanned against specific source account and forces full control ownership. |
| **AllowSSLRequestsOnly** | Explicit Security Guardrail: Prevents unencrypted data transfers by blocking HTTP requests. | **Deny:** `s3:*` on bucket and contents | Denies all operations if `aws:SecureTransport` evaluates to `false`. |

**Policy JSON:** `/policies/aws-config-251880984053-2026.json`

---

### 3. Tag-Based Development Access Policy (`Policy-DevOps-Dev-TagBased`)

Attached to the `DevOps-Dev` group, this policy allows network infrastructure management while strictly enforcing ABAC (tagging) for compute and storage resources. It includes a strong deny guardrail to prevent tampering with security services.

| Statement SID | Purpose & Description | Allowed / Denied Operations | Security Condition / Guardrail |
| :--- | :--- | :--- | :--- |
| **AllowNetworkAndVPCManagement** | Grants permission to build and manage network infrastructure components (VPC, Subnets, SGs, Flow Logs). | **Allow:** `ec2:CreateVpc`, `ec2:CreateSubnet`, Security Groups, and Flow Logs management. | None. |
| **AllowS3ListingAndViewing** | Provides basic visibility into S3 buckets across the account. | **Allow:** `s3:ListAllMyBuckets`, `s3:GetBucketLocation`, `s3:ListBucket`. | None. |
| **EnforceMandatoryTaggingOnCreation** | Enforces the creation of new compute, database, and storage resources exclusively with the required "Dev" tag. | **Allow:** `s3:CreateBucket`, `ec2:RunInstances`, `ec2:CreateTags`, `rds:CreateDBInstance`. | Request MUST include: `Environment = Dev` (`aws:RequestTag`). |
| **AllowManagementOfDevResourcesWithTags** | Grants full management actions over resources, provided they are tagged as Development. | **Allow:** `s3:*`, `ec2:*`, `rds:*`, `lambda:*`. | Target resource MUST have: `Environment = Dev` (`aws:ResourceTag`). |
| **DenySecurityAndGovernanceModification** | Explicit Security Guardrail: Prevents DevOps users from modifying or disabling security, logging, and identity services. | **Deny:** `iam:*`, `cloudtrail:*`, `config:*`, `guardduty:*`. | Absolute Deny (Overrides any other allows). | 

**Policy JSON:** `/policies/Policy-DevOps-Dev-TagBased.json`

---

### 4. Least-Privilege & ABAC (Attribute-Based Access Control) Policies

To enforce strict access control and least-privilege principles, custom IAM policies were engineered. These policies utilize tagging strategies (ABAC) and the STS Assume Role mechanism to securely restrict and manage production workloads without granting blanket administrative access.

#### A. Assume Role Policy (`Policy-Allow-Assume-ProdRole`)
Attached to the `DevOps-Prod` group, this identity-based policy grants authorized users the ability to dynamically elevate their privileges by assuming a specific production role. This ensures credentials remain temporary and all actions are rigorously audited via CloudTrail.

| Statement SID | Purpose & Description | Action Effect | Target Resource |
| :--- | :--- | :--- | :--- |
| **AllowAssumeProductionRole** | Grants Secure Token Service (STS) permission to assume the Production Admin role. | Allow `sts:AssumeRole` | `arn:aws:iam::<YOUR-ACCOUNT-ID>:role/Role-Production-Admin` |

**Policy JSON:** `/policies/Policy-Allow-Assume-ProdRole.json`

---

#### B. Tag-Based Production Access Policy (`Policy-Prod-FullAccess-Tagged`)

This policy enforces strict tagging compliance. Users can only provision or manage resources if they explicitly associate them with the Production environment, eliminating untracked shadow IT resources.

| Statement SID | Purpose & Description | Allowed Operations | Security Condition / Guardrail |
| :--- | :--- | :--- | :--- |
| **AllowGeneralListingAndViewing** | Provides basic read-only access required to navigate the AWS Console and list current infrastructure. | • `s3:ListAllMyBuckets`<br>• `s3:GetBucketLocation`<br>• `s3:ListBucket`<br>• `ec2:Describe*` | None (Global read access allowed for visibility). |
| **EnforceMandatoryTaggingOnProdCreation** | Forces users to apply the required environmental tag exactly during resource creation. Resource creation fails if the tag is missing. | • `s3:CreateBucket`<br>• `s3:TagResource`<br>• `ec2:RunInstances` | Request MUST include the tag key-value pair: `Environment = Prod` (`aws:RequestTag`). |
| **AllowFullControlOnProdResourcesWithTags** | Restricts all administrative and management actions exclusively to resources that possess the authorized tag. | • `ec2:*`<br>• `s3:*`<br>• `rds:*`<br>• `cloudwatch:*` | Target resource MUST already possess the tag: `Environment = Prod` (`aws:ResourceTag`). |

**Policy JSON:** `/policies/Policy-Prod-FullAccess-Tagged.json`

---

### 5. Implement Permission Boundaries (Simulating SCP Guardrails)

Due to single-account environment constraints for this project, Enterprise SCP Guardrails were simulated using **IAM Permission Boundaries**. This boundary policy is attached to IAM Users and Roles (e.g., DevOps and Admin roles) to define the absolute maximum permissions they can have, overriding even `AdministratorAccess` to prevent destructive actions and enforce data residency.

#### Permission Boundary Policy Rules & Effects

| Boundary Statement | Purpose & Description | Allowed Operations | Blocked/Denied Operations |
| :--- | :--- | :--- | :--- |
| **Region Restriction (Geofencing)** | Enforces data residency by restricting resource provisioning to authorized AWS regions only. | • Global services (IAM, STS, Route53, Support).<br>• Any operations within `us-east-1` and `eu-central-1`. | • Creating or modifying any AWS resources outside of `us-east-1` and `eu-central-1`. |
| **Security Log Protection** | Ensures continuous compliance monitoring and prevents anti-forensic activities by protecting audit trails. | • Viewing CloudTrail logs.<br>• Creating new trails or Config rules. | • Deleting CloudTrail trails.<br>• Stopping CloudTrail logging.<br>• Deleting or stopping AWS Config recorders. |
| **Audit Bucket Retention** | Protects the centralized S3 logging archive (immutable storage) from being deleted or tampered with. | • Writing logs to the bucket.<br>• Reading and querying archived logs. | • Deleting the central S3 audit bucket.<br>• Deleting the S3 bucket policy. |
| **Maximum Permitted Access** | Establishes the maximum possible permissions (allowing all other actions not explicitly denied above). | • All other standard AWS actions within approved regions. | • N/A (Access is further restricted by the user's actual IAM Identity policies). |

**Policy JSON:** `/policies/PermissionBoundary.json`