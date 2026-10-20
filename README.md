# 🛡️ Secure AWS Landing Zone & Governance

![AWS](https://img.shields.io/badge/AWS-232F3E?style=for-the-badge&logo=amazon-aws&logoColor=white)
![Terraform](https://img.shields.io/badge/Terraform-7B42BC?style=for-the-badge&logo=terraform&logoColor=white)
![Security](https://img.shields.io/badge/Cloud-Security-red?style=for-the-badge)
![IAM](https://img.shields.io/badge/AWS%20IAM-DD344C?style=for-the-badge)
![Organizations](https://img.shields.io/badge/Organizations-E7157B?style=for-the-badge)
![VPC](https://img.shields.io/badge/Amazon%20VPC-8C4FFF?style=for-the-badge)
![S3](https://img.shields.io/badge/Amazon%20S3-569A31?style=for-the-badge&logo=amazons3&logoColor=white)
![CloudTrail](https://img.shields.io/badge/CloudTrail-E7157B?style=for-the-badge)
![Config](https://img.shields.io/badge/AWS%20Config-E7157B?style=for-the-badge)
![GuardDuty](https://img.shields.io/badge/GuardDuty-DD344C?style=for-the-badge)
![Security Hub](https://img.shields.io/badge/Security%20Hub-DD344C?style=for-the-badge)
![Budgets](https://img.shields.io/badge/AWS%20Budgets-3F8624?style=for-the-badge)
![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white)
![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)

Secure AWS Landing Zone & Governance is a hands-on cloud security project that builds a secure baseline on AWS: hardened account access with MFA, least-privilege IAM, a segmented VPC (public / app / data tiers) with layered security groups and NACLs, and centralized logging, configuration tracking and threat detection with CloudTrail, AWS Config, GuardDuty and Security Hub, plus cost guardrails with AWS Budgets and Infrastructure as Code with Terraform.

---

## 📑 Table of Contents
- [Overview](#-overview)
- [Scope & Constraints](#-scope--constraints)
- [Features](#-features)
- [Architecture](#-architecture)
- [AWS Services Used](#-aws-services-used)
- [Design Decisions](#-design-decisions)
- [Project Structure](#-project-structure)
- [Security & Cost Notes](#-security--cost-notes)
- [Team](#-Team)

---

## 🎯 Overview

Many teams start on AWS with everything in one account: a wide blast radius, broad and unreviewed permissions, little visibility into who did what, no guardrails against dangerous changes, and weak cost control.

This project addresses that with a secure baseline built in four stages:

| Week | Focus | Main outcome |
| :--- | :--- | :--- |
| 1 | Foundations & account security | Organization setup, root/MFA hardening, budgets and cost guardrails |
| 2 | IAM & access security | Least-privilege policies, permission boundary, access analysis |
| 3 | Secure network foundation | VPC with tiered subnets, SGs, NACLs, endpoint, Flow Logs |
| 4 | Governance, logging & detection | CloudTrail, Config, GuardDuty, Security Hub |

---

## 🧭 Scope & Constraints

The project was implemented in a **single AWS account**, working through IAM users. Because of that:

- Everything that runs inside one account was **implemented and evidenced** with screenshots (see [Screenshots](/evidence)).
- Parts that need several accounts (member accounts and OUs, IAM Identity Center, enforced SCPs, cross-account roles, an organization-wide trail) are **covered as design and documentation** rather than deployed.

This is called out explicitly so the reader knows what is built versus designed.

---

## 🚀 Features

- ✅ **Account Hardening:** MFA enabled, root access reviewed, and billing alerts configured.
- ✅ **Cost Guardrails:** AWS Budgets with email alerts to catch unexpected spend early.
- ✅ **Least-Privilege IAM:** Policies scoped to specific actions and resources, with a permission boundary as a hard ceiling.
- ✅ **Layered Network Security:** Public, app and data subnets; security groups chained by reference (ALB → App → DB); stateless NACLs per tier; data tier with no internet route.
- ✅ **Controlled Egress:** Internet Gateway for public subnets, NAT Gateway only for the private app tier (temporary, for cost).
- ✅ **Network Visibility:** VPC Flow Logs enabled for the VPC.
- ✅ **Audit Logging:** CloudTrail records account activity.
- ✅ **Configuration Tracking:** AWS Config records resource configuration and evaluates rules.
- ✅ **Threat Detection & Posture:** GuardDuty findings and Security Hub standards and coverage.

---

## 📐 Architecture

![Architecture Diagram](docs/architecture.svg)

**Flow:**
1. Users sign in with **IAM users protected by MFA**.
2. **IAM policies** grant only the permissions each role needs, and a **permission boundary** caps what delegated roles can ever do.
3. Workloads live in a **VPC** with three tiers: public, app and data subnets across two Availability Zones.
4. The **Internet Gateway** serves the public tier. The app tier reaches the internet only through a **NAT Gateway**. The data tier has **no route to the internet**.
5. **Security groups** (ALB → App → DB) and **NACLs** filter traffic at the instance and subnet level.
6. **VPC Flow Logs** capture network traffic metadata.
7. **CloudTrail** records API activity, **AWS Config** tracks configuration changes, and **GuardDuty** and **Security Hub** surface threats and misconfigurations.
8. **AWS Budgets** alerts by email when spend approaches the limit.

---

## 🛠 AWS Services Used

| Service | Role | Week |
| :--- | :--- | :---: |
| **AWS Organizations** | Organization setup and consolidated billing | 1 |
| **AWS Budgets** | Monthly cost budget with email alerts | 1 |
| **AWS IAM** | Users, roles, least-privilege policies, permission boundary | 2 |
| **IAM Access Analyzer** | Finds resources shared outside the account | 2 |
| **Amazon VPC** | Subnets, route tables, Internet Gateway, NAT Gateway | 3 |
| **Security Groups & NACLs** | Layered traffic filtering per tier | 3 |
| **VPC Flow Logs** | Network traffic visibility | 3 |
| **VPC Endpoints (S3 Gateway & EICE)** | Secure private routing to S3 and private SSH access without Bastion hosts | 3 |
| **Application Load Balancer (ALB)** | Distributing web traffic securely across EC2 instances in multiple AZs | 4 |
| **Amazon EC2** | Compute instances hosting the "Rehlti" application backend | 4 |
| **Amazon RDS (PostgreSQL)** | Managed relational database for the application backend | 4 |
| **AWS CloudTrail** | Audit log of API activity | 4 |
| **AWS Config** | Resource configuration tracking and rules | 4 |
| **Amazon GuardDuty** | Threat detection | 4 |
| **AWS Security Hub** | Security standards, findings and coverage | 4 |
| **Amazon S3** | Log storage with versioning and blocked public access | 3-4 |
| **Terraform** | Infrastructure as Code for the VPC, log bucket and guardrail policies | 4 |
| **Git & GitHub** | Version control and project documentation | 1-4 |

---

## 🧠 Design Decisions

- **Tiered subnets (public / app / data):** limits how far an attacker can move if one tier is compromised.
- **Security groups reference other security groups, not IP ranges:** rules stay correct when instances change.
- **NACLs as a second, stateless layer:** they require explicit return-traffic rules (ephemeral ports), which is documented in the SG/NACL matrix.
- **Data tier without an internet route:** databases never need direct internet access.
- **NAT Gateway kept temporary:** it is billed hourly, so it is created for evidence and removed.
- **Least privilege first:** policies name specific actions and resources, and a permission boundary limits delegated roles.

---

## 📁 Project Structure

```text
aws-secure-landing-zone/
├── docs/                  # Architecture diagram and design documents
│   ├── architecture.png
│   └── architecture.svg
├── evidence/              # Screenshots per week
│   ├── week1/
│   ├── week2/
│   ├── week3/
│   └── week4/
├── policies/              # IAM policy library (JSON)
├── terraform/             # IaC modules and environments (optional / in progress)
├── .gitignore
└── README.md
```

---


# Week 1: AWS Foundations, Accounts & Organizations

This section outlines the foundational setup of the multi-account AWS environment, organizational structure, cost control mechanisms, and rigorous root account security hardening.

---

### Step 1 — AWS Organizations & Multi-Account Structure Setup

To implement an enterprise-grade landing zone, an AWS Organization was established to centrally manage multiple AWS accounts and enforce governance boundaries.

1. **Organizational Units (OUs) Hierarchy:**
    * **Root Organization**
    * **Sandbox OU** Allocated for experimental and testing workloads.
    * **Security OU** Dedicated to logging, auditing, and centralized security tooling.
    * **Workloads OU** Houses production and staging applications (e.g., the Rehlti travel booking platform).

2. **Account Management:**
    * **Management Account (`alisoliman` / `251880984053`):** Handles consolidated billing, organizational policies, and global governance.
    * **Member Accounts:** Provisioned and organized under their respective OUs with centralized consolidated billing.

---

### Step 2 — Cost Management & AWS Budgets Setup

To prevent unexpected cloud expenditures and maintain financial governance, AWS Budgets was configured for the project lifecycle.

1. **Budget Configuration:**
    * **Budget Name:** `DEPI Project - Free tier budget`
    * **Budget Amount:** `$30.00` Monthly limit.
    * **Tracking:** Monitors actual costs vs. forecasted expenses in primary billing view.

2. **Alert Mechanisms:**
    * Configured automated email notifications to trigger when actual costs exceed **80%** of the budgeted threshold.
    * Verified recipient email configuration (`alisoliimannegm@gmail.com`) for real-time alerting.

---

### Step 3 — Root Account Security Lockdown & MFA Configuration

In accordance with AWS security best practices and Well-Architected Framework guidelines, the management root account was rigorously locked down.

1. **Multi-Factor Authentication (MFA):**
    * Enabled hardware/virtual MFA device enforcement for the AWS Root user, requiring secondary verification on every administrative sign-in.

2. **Access Keys Management:**
    * Verified via the IAM Dashboard that **Root user has no active access keys**, eliminating long-term credential exposure.
    * Ensured adherence to the principle of least privilege by restricting root user usage strictly to tasks requiring root-level capabilities.
---

## Week 2: IAM, Federation& Account Security

This section establishes the identity baseline for the AWS environment, enforcing the principle of least privilege, role-based access control (RBAC), and continuous access auditing.

### Step 1 - IAM Baseline & Least-Privilege Architecture

A robust IAM structure was designed to segregate duties among different operational teams using groups, custom policies, and permission boundaries.

![Accounts, Groups, Roles, Policeis.png](docs/Accounts-Groups-Roles-Policeis.png)

1. **IAM Groups & Roles Design**:
    * **Admin:** Full administrative access for environment bootstrapping.
    * **DevOps-Dev:** Granted restricted access using custom tag-based policies (`Policy-DevOps-Dev-TagBased`) to manage development resources.
    * **DevOps-Prod:** Assigned a custom policy (`Policy-Allow-Assume-ProdRole`) permitting users to securely elevate privileges via role assumption.
    * **SecurityAuditors:** Configured with `SecurityAudit` and `ReadOnlyAccess` for compliance monitoring.
2. **IAM Users:** Provisioned distinct IAM users (e.g., `admin-fullaccess`, `ahmeds`, `mostafa`) distributed across the defined groups with MFA enforcement.

    *You will find all json files for policies in `/policies` Folder*
### Step 2 - Cross-Account Access Lab (STS Assume Role)

To simulate and validate cross-account delegation securely without sharing long-term credentials, the STS Assume Role pattern was implemented and tested.

* **Configuration:** Created a dedicated target role (`Role-Production-Admin`) equipped with `Policy-Prod-FullAccess-Tagged`.
* **Trust Policy:** Configured the role's trust relationship to only allow entities originating from the `DevOps-Prod` group.
* **Validation:** Successfully tested the delegation by using the AWS Console **Switch Role** feature, validating that authorized users can dynamically assume the `Role-Production-Admin` role, while unauthorized attempts are blocked.

### Step 3 - Identity Auditing with IAM Access Analyzer

To proactively monitor resource policies and detect unintended public or cross-account access, IAM Access Analyzer was deployed.

* **Analyzer Deployment:** Created an organization-wide analyzer (`Main-LandingZone-Analyzer`) configured with the zone of trust set to the current organization.
* **Integration:** The analyzer continuously scans policies and integrates findings with AWS Security Hub.

### Step 4 - Federation & SSO Design (Enterprise Architecture Concept)

*Note: This section outlines the architectural design for identity federation intended for production environments.*

* **AWS IAM Identity Center (Successor to AWS SSO):** Designed to centralize access management across all AWS accounts, replacing individual IAM users with centralized workforce identities.
* **ADFS & SAML 2.0 Integration:** The architecture integrates AWS with an on-premises Active Directory via AD Federation Services (ADFS). SAML 2.0 assertions are mapped directly to AWS IAM Roles, allowing seamless, credential-free Single Sign-On (SSO) for corporate users based on their existing AD group memberships.


### Step 5 — Implement Permission Boundaries (Simulating SCP Guardrails)

Due to single-account environment constraints for this project, Enterprise SCP Guardrails were simulated using **IAM Permission Boundaries**. This boundary policy is attached to IAM Users and Roles (e.g., DevOps and Admin roles) to define the absolute maximum permissions they can have, overriding even `AdministratorAccess` to prevent destructive actions and enforce data residency.

#### Permission Boundary Policy Rules & Effects

| Boundary Statement | Purpose & Description | Allowed Operations | Blocked/Denied Operations |
| :--- | :--- | :--- | :--- |
| **Region Restriction (Geofencing)** | Enforces data residency by restricting resource provisioning to authorized AWS regions only. | • Global services (IAM, STS, Route53, Support).<br>• Any operations within `us-east-1` and `eu-central-1`. | • Creating or modifying any AWS resources outside of `us-east-1` and `eu-central-1`. |
| **Security Log Protection** | Ensures continuous compliance monitoring and prevents anti-forensic activities by protecting audit trails. | • Viewing CloudTrail logs.<br>• Creating new trails or Config rules. | • Deleting CloudTrail trails.<br>• Stopping CloudTrail logging.<br>• Deleting or stopping AWS Config recorders. |
| **Audit Bucket Retention** | Protects the centralized S3 logging archive (immutable storage) from being deleted or tampered with. | • Writing logs to the bucket.<br>• Reading and querying archived logs. | • Deleting the central S3 audit bucket.<br>• Deleting the S3 bucket policy. |
| **Maximum Permitted Access** | Establishes the maximum possible permissions (allowing all other actions not explicitly denied above). | • All other standard AWS actions within approved regions. | • N/A (Access is further restricted by the user's actual IAM Identity policies). |

---

## Week 3: Secure Network Foundation

### Step 1 — Create VPC

1. Open **VPC** → **Create VPC** → choose **VPC only**
2. Name: `VPC-LZ-vpc` | IPv4 CIDR: `10.10.0.0/16`
3. Click **Create VPC**

---

### Step 2 — Create Subnets

Go to **VPC** → **Subnets** → **Create subnet** → select `VPC-LZ-vpc`

| Name | AZ | CIDR |
|---|---|---|
| `VPC-LZ-subnet-public1-us-east-1a` | us-east-1**a** | `10.10.1.0/24` |
| `VPC-LZ-subnet-public2-us-east-1b` | us-east-1**b** | `10.10.2.0/24` |
| `VPC-LZ-subnet-private1-us-east-1a` | us-east-1**a** | `10.10.10.0/24` |
| `VPC-LZ-subnet-private2-us-east-1b` | us-east-1**b** | `10.10.11.0/24` |


After creation, enable **Auto-assign public IPv4** on both subnets:
- Select subnet → **Actions** → **Edit subnet settings** → enable → **Save**

---

### Step 3 — Create Internet Gateway

1. **VPC** → **Internet Gateways** → **Create internet gateway**
2. Name: `VPC-LZ-igw` → **Create**
3. **Actions** → **Attach to VPC** → select `VPC-LZ-vpc` → **Attach**

---

### Step 4 — Create NAT Gateway

1. **VPC** → **NAT gateways** → **Create NAT gateway**
2. Name: `LZ-NAT` → **Create**
3. **VPC** → select `VPC-LZ-vpc`

---

### Step 5 — Create Route Table

#### Public Subnets
1. **VPC** → **Route Tables** → **Create route table**
2. Name: `LZ-Public-RT` | VPC: `VPC-LZ-vpc`
3. Open the route table → **Routes** → **Edit routes** → **Add route**:
   - Destination: `0.0.0.0/0` | Target: `VPC-LZ-igw`
4. **Subnet associations** → **Edit** → select both public subnets → **Save**

#### Private Subnets
1. **VPC** → **Route Tables** → **Create route table**
2. Name: `LZ-Private-RT` | VPC: `VPC-LZ-vpc`
3. Open the route table → **Routes** → **Edit routes** → **Add route**:
   - Destination: `0.0.0.0/0` | Target: `LZ-NAT`
   - Destination: `pl-63a5400a`(Managed Prefix) | Target: `S3-Gateway-Endpoint`
4. **Subnet associations** → **Edit** → select both public subnets → **Save**

#### Default that connect with Edge Association
Open the route table → **Routes** → **Edit routes** → **Add route**:
   - Destination: `0.0.0.0/0` | Target: `VPC-LZ-igw`

---

### Step 6 — Create Security Groups

**ALB Security Group (`Sg-alb`)**
| Direction | Type | Protocol | Port Range | Source type | Source |
|---|---|---|---|---|---|
| Inbound | HTTP | TCP | 443| Custom  | `0.0.0.0/0` |
| Inbound | HTTPS | TCP | 80 | Custom  | Custom | `0.0.0.0/0` |

| Direction | Type | Protocol | Port Range | Destination type | Destination |
|---|---|---|---|---|---|
| Outbound | All Traffic | All | All | Custom | `0.0.0.0/0` |

**EC2 Security Group (`Sg-app`)**
| Direction | Type | Protocol | Port Range | Source type | Source |
|---|---|---|---|---|---|
| Inbound | Custom TCP | TCP | 8080 | Custom | `Sg-alb` |

| Direction | Type | Protocol | Port Range | Destination type | Destination |
|---|---|---|---|---|---|
| Outbound | All Traffic | All | All | Custom | `0.0.0.0/0` |

**DataBase Security Group (`Sg-DB`)**
| Direction | Type | Protocol | Port Range | Source type | Source |
|---|---|---|---|---|---|
| Inbound | PostgreSQL | TCP | 5432 | Custom | `Sg-app` |

| Direction | Type | Protocol | Port Range | Destination type | Destination |
|---|---|---|---|---|---|
| Outbound | PostgreSQL | TCP | 5432 | Custom | `Sg-app` |

### Step 7 — Create Network ACL

1. **ALB Security Group (`NACL-Public`)**

#### Inbound Rules
| Role Number | Type | Protocol | Port range | Source | Allow/Deny | 
|---|---|---|---|---|---|
| 100 | HTTP (443) | TCP (6) | `443` | `0.0.0.0/0` | Allow
| 110 | HTTP (80) | TCP (6) | `80` | `0.0.0.0/0` | Allow
| 120 | Custom TCP | TCP (6) | `1024 - 65535` | `0.0.0.0/0` | Allow
| 130 | All ICMP - IPv4 | ICMP (1) | `All` | `0.0.0.0/0` | Allow
| * | All Traffic | All | All | `0.0.0.0/0` | Deny

#### Outbound Rules
| Role Number | Type | Protocol | Port range | Source | Allow/Deny | 
|---|---|---|---|---|---|
| 100 | HTTP (443) | TCP (6) | `443` | `0.0.0.0/0` | Allow
| 110 | HTTP (80) | TCP (6) | `80` | `0.0.0.0/0` | Allow
| 120 | Custom TCP | TCP (6) | `1024 - 65535` | `0.0.0.0/0` | Allow
| 130 | All ICMP - IPv4 | ICMP (1) | `All` | `0.0.0.0/0` | Allow
| * | All Traffic | All | All | `0.0.0.0/0` | Deny

2. **EC2 Security Group (`NACL-app`)**

#### Inbound Rules
| Role Number | Type | Protocol | Port range | Source | Allow/Deny | 
|---|---|---|---|---|---|
| 90 | HTTPS (443) | TCP (6) | `443` | `0.0.0.0/0` | Allow
| 100 | Custom TCP | TCP (6) | `1024 - 65535` | `0.0.0.0/0` | Allow
| 110 | HTTP (80) | TCP (6) | `443` | `10.10.1.0/24` | Allow
| 120 | HTTP (80) | TCP (6) | `443` | `10.10.2.0/24` | Allow
| 130 | HTTPS* (8080) | TCP (6) | `8080` | `10.10.0.0/16` | Allow
| * | All Traffic | All | All | `0.0.0.0/0` | Deny

#### Outbound Rules
| Role Number | Type | Protocol | Port range | Source | Allow/Deny | 
|---|---|---|---|---|---|
| 90 | HTTPS (443) | TCP (6) | `443` | `0.0.0.0/0` | Allow
| 100 | Custom TCP | TCP (6) | `1024 - 65535` | `10.10.1.0/24` | Allow
| 110 | Custom TCP | TCP (6) | `1024 - 65535` | `10.10.2.0/24` | Allow
| 120 | Custom TCP | TCP (6) | `1024 - 65535` | `0.0.0.0/0` | Allow
| 130 | HTTPS* (8080) | TCP (6) | `8080` | `10.10.0.0/16` | Allow
| * | All Traffic | All | All | `0.0.0.0/0` | Deny

---

### Step 8 — Create VPC Gateway Endpoint (Amazon S3)

To enable secure and private communication between resources in your private subnets and Amazon S3 without traversing the public internet or requiring a NAT Gateway, configure a VPC Gateway Endpoint for S3.

1. **Navigate to VPC Endpoints:**
    * Go to the **VPC Console** → Click on **Endpoints** under the *PrivateLink and Lattice* section in the left sidebar.
    * Click **Create endpoint**.


2. **Configure Endpoint Settings:**
    * **Name tag:** `S3-Gateway-Endpoint`
    * **Service category:** Select **AWS services**
    * **Services:** Search for and select `com.amazonaws.us-east-1.s3` (Ensure the type is **Gateway**).


3. **Select VPC and Route Tables:**
    * **VPC:** Select your project VPC (`VPC-LZ-vpc`).
    * **Configure route tables:** Select the private route table (`LZ-Private-RT`) so that routes to S3 are automatically added to it.


4. **Policy and Finalization:**
    * **Policy:** Keep it as **Full access** (or configure a custom bucket policy if needed).
    * Click **Create endpoint** to complete the secure S3 gateway connection.

---
### Step 9 — Create VPC Flow Logs (Network Monitoring & Auditing)

To monitor, capture, and archive network traffic metadata traversing your VPC for security and auditing purposes, configure VPC Flow Logs and publish them to an Amazon S3 bucket.

1. **Create S3 Bucket**
* Go to **S3** → Click on **Create bucket**
* Name: my-cloud-app-bucket-2027 (must be globally unique)
* Region: same as all other resources
* Keep it: **Block public access (bucket settings)**
* All other settings: default
* Add Bucket Policy below in Permissions:
```json
{
    "Version": "2012-10-17",
    "Id": "AWSLogDeliveryWrite20150319",
    "Statement": [
        {
            "Sid": "AWSLogDeliveryWrite1",
            "Effect": "Allow",
            "Principal": {
                "Service": "delivery.logs.amazonaws.com"
            },
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::YOUR_BUCKET_NAME/AWSLogs/YOUR_ACCOUNT_ID/*",
            "Condition": {
                "StringEquals": {
                    "aws:SourceAccount": "YOUR_ACCOUNT_ID",
                    "s3:x-amz-acl": "bucket-owner-full-control"
                },
                "ArnLike": {
                    "aws:SourceArn": "arn:aws:logs:us-east-1:YOUR_ACCOUNT_ID:*"
                }
            }
        },
        {
            "Sid": "AWSLogDeliveryAclCheck1",
            "Effect": "Allow",
            "Principal": {
                "Service": "delivery.logs.amazonaws.com"
            },
            "Action": "s3:GetBucketAcl",
            "Resource": "arn:aws:s3:::YOUR_BUCKET_NAME",
            "Condition": {
                "StringEquals": {
                    "aws:SourceAccount": "YOUR_ACCOUNT_ID"
                },
                "ArnLike": {
                    "aws:SourceArn": "arn:aws:logs:us-east-1:YOUR_ACCOUNT_ID:*"
                }
            }
        },
        {
            "Sid": "AWSCloudTrailAclCheck",
            "Effect": "Allow",
            "Principal": {
                "Service": "cloudtrail.amazonaws.com"
            },
            "Action": "s3:GetBucketAcl",
            "Resource": "arn:aws:s3:::YOUR_BUCKET_NAME",
            "Condition": {
                "StringEquals": {
                    "AWS:SourceArn": "arn:aws:cloudtrail:us-east-1:YOUR_ACCOUNT_ID:trail/lz-org-trail"
                }
            }
        },
        {
            "Sid": "AWSCloudTrailWriteAccount",
            "Effect": "Allow",
            "Principal": {
                "Service": "cloudtrail.amazonaws.com"
            },
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::YOUR_BUCKET_NAME/AWSLogs/YOUR_ACCOUNT_ID/*",
            "Condition": {
                "StringEquals": {
                    "AWS:SourceArn": "arn:aws:cloudtrail:us-east-1:YOUR_ACCOUNT_ID:trail/lz-org-trail",
                    "s3:x-amz-acl": "bucket-owner-full-control"
                }
            }
        },
        {
            "Sid": "AWSCloudTrailWriteOrg",
            "Effect": "Allow",
            "Principal": {
                "Service": "cloudtrail.amazonaws.com"
            },
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::YOUR_BUCKET_NAME/AWSLogs/YOUR_ORG_ID/*",
            "Condition": {
                "StringEquals": {
                    "AWS:SourceArn": "arn:aws:cloudtrail:us-east-1:YOUR_ACCOUNT_ID:trail/lz-org-trail",
                    "s3:x-amz-acl": "bucket-owner-full-control"
                }
            }
        },
        {
            "Sid": "AllowSSLRequestsOnly",
            "Effect": "Deny",
            "Principal": "*",
            "Action": "s3:*",
            "Resource": [
                "arn:aws:s3:::YOUR_BUCKET_NAME",
                "arn:aws:s3:::YOUR_BUCKET_NAME/*"
            ],
            "Condition": {
                "Bool": {
                    "aws:SecureTransport": "false"
                }
            }
        }
    ]
}   
```

2. **Navigate to VPC Service:**
    * Go to the **VPC Console** → Click on **Your VPCs** in the left sidebar.
    * Select your project VPC (`VPC-LZ-vpc`).

3. **Initiate Flow Log Creation:**
    * Select the **Flow logs** tab in the details pane, then click **Create flow log**.

4. **Configure Flow Log Settings:**
    * **Name tag:** `lz-dev-vpc-flow-logs`
    * **Filter:** Select **All** (to capture both accepted and rejected traffic).
    * **Maximum aggregation interval:** Select **10 minutes**.

5. **Set Destination and Storage:**
    * **Destination:** Choose **Send to an Amazon S3 bucket**.  
    * **S3 bucket ARN:** Enter the destination S3 bucket ARN (`arn:aws:s3:::my-cloud-app-bucket-2027`).

6. **Format and Advanced Settings:**
    * **Log record format:** Choose **AWS default format**.
    * **Log file format:** Select **Text (default)**.
    * **Partition logs by time:** Select **Every 24 hours (default)**.

7. **Finalize:**
    * Click **Create flow log** to successfully enable network auditing and link the logs to your S3 archive bucket.

---

## Week 4: Governance, Logging, Compliance & Automation

#### Step 1 — Configure Organization-Wide AWS CloudTrail

To ensure comprehensive auditing and compliance tracking across all accounts within your AWS Organization, configure a multi-region organizational trail.

1. **Navigate to CloudTrail Service:**
    * Open the **AWS CloudTrail Console**.
    * In the left sidebar, click on **Trails**, then click **Create trail**.

2. **Configure Trail Settings:**
    * **Trail name:** `lz-org-trail`.
    * **Storage location:** Choose **Create a new S3 bucket** (or select your existing archiving bucket, e.g., `my-cloud-app-bucket-2027`).
    * **Apply to all accounts in my organization:** **Enable (Check)** this option to make it an organization-wide trail.

3. **Configure Log Events & Review:**
    * Select log events (Management events, Data events, and Insight events as needed).
    * Review settings and click **Create trail** to start capturing organizational API activity and storing logs securely in S3.

---

#### Step 2 — Configure AWS Config for Resource Auditing & Compliance

To continuously audit, evaluate, and track configuration changes of your AWS resources against security best practices, set up AWS Config.

1. **Create S3 Bucket**
* Go to **S3** → Click on **Create bucket**
* Name: aws-config-{Account_ID}-2026 (must be globally unique)
* Region: same as all other resources
* Keep it: **Block public access (bucket settings)**
* All other settings: default
* Add Bucket Policy below in Permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AWSConfigBucketPermissionsCheck",
            "Effect": "Allow",
            "Principal": {
                "Service": "config.amazonaws.com"
            },
            "Action": "s3:GetBucketAcl",
            "Resource": "arn:aws:s3:::aws-config-251880984053-2026",
            "Condition": {
                "StringEquals": {
                    "AWS:SourceAccount": "251880984053"
                }
            }
        },
        {
            "Sid": "AWSConfigBucketExistenceCheck",
            "Effect": "Allow",
            "Principal": {
                "Service": "config.amazonaws.com"
            },
            "Action": "s3:ListBucket",
            "Resource": "arn:aws:s3:::aws-config-251880984053-2026",
            "Condition": {
                "StringEquals": {
                    "AWS:SourceAccount": "251880984053"
                }
            }
        },
        {
            "Sid": "AWSConfigBucketDelivery",
            "Effect": "Allow",
            "Principal": {
                "Service": "config.amazonaws.com"
            },
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::aws-config-251880984053-2026/AWSLogs/251880984053/Config/*",
            "Condition": {
                "StringEquals": {
                    "s3:x-amz-acl": "bucket-owner-full-control",
                    "AWS:SourceAccount": "251880984053"
                }
            }
        },
        {
            "Sid": "AllowSSLRequestsOnly",
            "Effect": "Deny",
            "Principal": "*",
            "Action": "s3:*",
            "Resource": [
                "arn:aws:s3:::aws-config-251880984053-2026",
                "arn:aws:s3:::aws-config-251880984053-2026/*"
            ],
            "Condition": {
                "Bool": {
                    "aws:SecureTransport": "false"
                }
            }
        }
    ]
}
```

2. **Navigate to AWS Config Service:**
    * Open the **AWS Config Console**.
    * If it's your first time, click **Get Started**; otherwise, navigate to **Settings**.

3. **Configure Recording & Data Delivery:**
    * **Recording strategy:** Set to **Record all resource types with customizable overrides** (or select specific critical resources) to ensure full visibility.
    * **Data retention period:** Configure retention (e.g., Default period of 7 years or custom retention rules).
    * **S3 Bucket:** Select your central logging/auditing S3 bucket (`aws-config-251880984053-2026` or your custom logs bucket).

4. **Finalize Setup:**
    * Save the configuration settings to initiate the **Customer managed recorder**, allowing AWS Config to begin tracking configuration items and compliance statuses.

---

### Step 3 — Enable Amazon GuardDuty for Threat Detection & Protection Plans

To continuously monitor malicious activity, unauthorized behavior, and potential compromises across your AWS environment, enable Amazon GuardDuty along with its advanced protection plans (EKS, RDS, Lambda, S3, and Runtime Monitoring).

1. **Navigate to GuardDuty Service:**
    * Open the **Amazon GuardDuty Console**.
    * Ensure GuardDuty is enabled for the account to start detecting threats.

2. **Configure Protection Plans (Extended Threat Detection):**
    * Go to **Protection Plans** in the left sidebar.
    * Enable critical protection layers to secure workloads:
    * **EKS Protection & Audit Log Monitoring**
    * **RDS Protection** (Login Activity & Data Activity Monitoring)
    * **Lambda Protection** (Network Activity Monitoring)
    * **S3 Protection & Runtime Monitoring**

3. **Monitor Security Findings & Summary:**
    * Review the **GuardDuty Summary Dashboard** to track threat metrics, severity distribution (Critical, High, Medium, Low), and affected resources in real time.

---

### Step 4 — Configure AWS Security Hub & Compliance Baseline

To centralize security alerts, perform automated security checks, and monitor posture management across your AWS environment, configure AWS Security Hub.

1. **Navigate to Security Hub:**
    * Open the **AWS Security Hub Console**.
    * Enable Security Hub to aggregate findings from GuardDuty, IAM, S3, and other integrated AWS security services.

2. **Monitor Security Standards & Account Coverage:**
    * Review the **Security Hub Summary** dashboard to track overall threats, exposures, and resource findings.
    * Navigate to **Account coverage** to verify posture management status (e.g., 100% CSPM coverage) and service integration metrics like Amazon Inspector and GuardDuty.

## 🏷️ Enterprise Tagging Strategy & ABAC Implementation

To maintain strict cost allocation (FinOps), operational ownership, and resource governance across the AWS environment, a mandatory tagging strategy was enforced using Attribute-Based Access Control (ABAC). 

### 1. Standard Tagging Taxonomy (Key-Value Schema)
All AWS resources provisioned within the Landing Zone must adhere to the following standardized tag keys:

| Tag Key | Type | Description & Purpose | Example Values |
| :--- | :--- | :--- | :--- |
| **`Environment`** | Mandatory | Defines the deployment lifecycle stage of the resource. Used heavily in IAM policies to restrict permissions. | `Prod`, `Dev`, `Staging`, `Sandbox` |
| **`Project`** | Mandatory | Identifies the specific business initiative, application, or project utilizing the resource. | `Rehlti`, `LandingZone`, `CoreInfra` |
| **`Owner` / `Team`** | Mandatory | Specifies the technical team or individual responsible for the maintenance and security of the resource. | `Cloud-Security-Team`, `DevOps-Team` |
| **`CostCenter`** | Mandatory | Enables financial tracking and consolidated billing allocation across organizational departments. | `CC-1002-Eng`, `CC-2040-Sec` |

### 2. Enforcement Mechanism (ABAC Guardrails)
* **Creation-Time Enforcement:** Custom IAM policies (`Policy-DevOps-Dev-TagBased` and `Policy-Prod-FullAccess-Tagged`) use the `aws:RequestTag` condition key to block resource creation (such as S3 buckets, EC2 instances, and RDS databases) if the mandatory `Environment` tag is omitted.
* **Lifecycle Management:** Existing resources are continuously monitored to ensure compliance with the tagging taxonomy, preventing un-tracked "shadow IT" resources across the landing zone.

---

## 🚀 Rehlti Application Deployment & Server Configuration Guide

This guide details the end-to-end execution steps to deploy the **Rehlti** Python/Flask web application across high-availability EC2 instances connected to an Amazon RDS (PostgreSQL) database, fronted by an Application Load Balancer (ALB).

---

## 📂 Project Directory Structure

```text
rehlti-app/
├── app.py                 # Main Flask application and database initialization
├── schema.sql             # Database schema definition
├── requirements.txt       # Python dependencies
├── static/                # Client-facing frontend files
│   ├── index.html         # Main user booking interface
│   ├── app.js             # Client interaction logic
│   └── style.css          # Tailwind / Custom styling
└── admin/                 # Administrator portal
    ├── login.html         # Secure admin authentication interface
    ├── dashboard.html     # Reservation management and control panel
    └── style.css          # Admin styling rules
```

---

## ⚙️ Step-by-Step Server Setup & Execution

### Step 1 — Launch EC2 Instances

Launch two **t3.micro Amazon Linux 2023** instances:

| Setting | Instance 1 | Instance 2 |
|---|---|---|
| Name | `LZ-App-EC2-1` | `LZ-App-EC2-2` |
| Subnet | `VPC-LZ-subnet-private1-us-east-1a` | `VPC-LZ-subnet-private2-us-east-1b` |
| Security Group | `Sg-app` | `Sg-app` |
| Key Pair | `ats-keypair` | `ats-keypair` |


---

### Step 2 — Create Target Group & Load Balancer

**Target Group:**
1. **EC2** → **Target Groups** → **Create target group**
2. Type: Instances | Name: `LZ-App-TG` | Protocol: HTTP | Port: 8080 | VPC: `VPC-LZ-vpc`
3. Health check path: `/health`
4. Register both EC2 instances as targets: `LZ-App-EC2-1`, `LZ-App-EC2-2`

**Application Load Balancer:**
1. **EC2** → **Load Balancers** → **Create load balancer** → **Application Load Balancer**
2. Name: `LZ-App-ALB` | Scheme: Internet-facing | VPC: `VPC-LZ-vpc`
3. Select both public subnets | Security group: `Sg-alb`
4. Listener: HTTP:80 → forward to `LZ-App-TG`
5. Save the **DNS name** — this is your application URL

---

### Step 3 — Create Amazon RDS (PostgreSQL) Database Instance

To support the Rehlti application backend with a reliable relational database while maintaining strict security isolation, an Amazon RDS PostgreSQL instance was provisioned within the private network tier.

1. **Database Engine & Template:**
   * **Engine:** PostgreSQL (v18.6-R1).
   * **Template:** Sandbox / Dev-Test configuration optimized for project lifecycle[cite: 26].
   * **Deployment:** Single-AZ DB instance deployment using a cost-effective `db.t4g.micro` burstable class[cite: 27, 29].

2. **Network & Security Isolation:**
   * **VPC:** Deployed inside the project VPC (`VPC-LZ-vpc`).
   * **Public Access:** Set to **No** (completely isolated from the public internet)[cite: 30].
   * **Security Group:** Associated exclusively with **`Sg-DB`**, restricting incoming PostgreSQL traffic (`Port 5432`) strictly to the application server security group[cite: 30].

3. **Database Options & Encryption:**
   * **Initial Database Name:** `rehlaty`.
   * **Encryption:** Enabled (`Enabled encryption`) utilizing the default AWS KMS key (`alias/aws/rds`) for data-at-rest security[cite: 31].
   * **Backup:** Automated backups enabled with a 1-day retention period[cite: 31].

---

### Step 4: Connect to the EC2 Instance & Navigate to the Project Directory

Connect to your EC2 instance via SSH, then create and move into the application directory:

```bash
mkdir -p /home/ec2-user/rehlti-app
cd /home/ec2-user/rehlti-app
```

---

### Step 5: Initialize the Python Virtual Environment & Install Dependencies

Set up an isolated Python environment and install the required packages (`Flask`, `psycopg2-binary`, and `gunicorn`):

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install flask psycopg2-binary gunicorn
```

---

### Step 6: Create and Configure Application Files

#### 1. Main Application File (`app.py`)

Create the main Flask backend file:

```bash
nano app.py
```

*(Paste the complete backend application code containing routes, database connection, and initialization logic from `/rehlti-app/app.py`, then save using `Ctrl + O`, press `Enter`, and exit using `Ctrl + X`)*.

#### 2. Requirements File (`requirements.txt`)

Create the dependencies file:

```bash
nano requirements.txt
```

*(Paste the package requirements: `Flask`, `psycopg2-binary`, `gunicorn`, then save and exit)*.
```
cat << 'EOF' > requirements.txt
Flask==3.1.0
gunicorn==23.0.0
psycopg2-binary==2.9.9
EOF
```
```
pip install -r requirements.txt
```

#### 1. Preparing The Schema

```bash
nano schema.sql
```

*(Paste the HTML code from `/rehlti-app/schema.sql`, save with `Ctrl + O` -> `Enter`, and exit with `Ctrl + X`)*

---

### Step 7: Set Up the Main Application Pages

Create the `static` subdirectory:

```bash
mkdir -p static
cd static/
```

#### 1. Main Page (`static/index.html`)

Create and edit the login page:

```bash
nano index.html
```

*(Paste the HTML code from `/rehlti-app/static/index.html`, save with `Ctrl + O` -> `Enter`, and exit with `Ctrl + X`)*

#### 2. JS File (`static/app.js`)

Create and edit the dashboard page:

```bash
nano app.html
```

*(Paste the HTML code from `/rehlti-app/static/app.js`, save with `Ctrl + O` -> `Enter`, and exit with `Ctrl + X`)*

#### 3. Main Website Style

Create and edit the dashboard page:

```bash
nano style.html
```

*(Paste the HTML code from `/rehlti-app/static/syle.css`, save with `Ctrl + O` -> `Enter`, and exit with `Ctrl + X`)*

---

### Step 8: Set Up the Admin Portal Directory & Files

Create the `admin` subdirectory:

```bash
mkdir -p admin
cd admin/
```

#### 1. Admin Login Page (`admin/login.html`)

Create and edit the login page:

```bash
nano login.html
```

*(Paste the HTML code from `/rehlti-app/admin/login.html`, save with `Ctrl + O` -> `Enter`, and exit with `Ctrl + X`)*

#### 2. Admin Dashboard Panel (`admin/dashboard.html`)

Create and edit the dashboard page:

```bash
nano dashboard.html
```

*(Paste the HTML code from `/rehlti-app/admin/dashboard.html`, save with `Ctrl + O` -> `Enter`, and exit with `Ctrl + X`)*

#### 3. Admin Style

Create and edit the dashboard page:

```bash
nano style.html
```

*(Paste the HTML code from `/rehlti-app/admin/syle.css`, save with `Ctrl + O` -> `Enter`, and exit with `Ctrl + X`)*

----

### Step 9: Configure Environment Variables & Run Gunicorn

Export your secure Amazon RDS PostgreSQL connection string as an environment variable, ensure your virtual environment is active, and launch the application using Gunicorn bound to port `8080` (matched with your ALB Target Group):

```bash
export DATABASE_URL="postgresql://postgres:YOUR_DB_PASSWORD@YOUR_RDS_ENDPOINT:5432/postgres"
source venv/bin/activate
gunicorn -w 4 -b 0.0.0.0:8080 app:app
```
---

### Step 10: Check Database on EC2

1. Command to access the database
```bash
psql -h [end_point_link] -U {master_username} -d {database_name}
or
mysql -h [end_point_link] -U {master_username} -d {database_name}
```

2. Write your password `=> PASSWORD`
3. Use Query Language (ex: `SELECT * FROM users;`) to check

---

### Step 11: Architecture & Security Validation

- **Database Connectivity:** The application connects securely to Amazon RDS (PostgreSQL) residing in a private subnet, authorized via Security Groups allowing inbound traffic on port `5432` strictly from the EC2 application security group.

- **Load Balancer Integration:** The Application Load Balancer (ALB) receives external client requests on HTTP Port `80` (Internet-facing) and routes traffic transparently to the EC2 instances registered in the Target Group on Port `8080`.

- **High Availability:** Multiple EC2 instances running identical application code structures across different Availability Zones (Multi-AZ) ensure seamless fault tolerance and load distribution.

---

## 🔒 Security & Cost Notes

- No credentials, access keys or Terraform state are committed (see `.gitignore`).
- Account identifiers are masked in published screenshots.
- NAT Gateways, Elastic IPs and interface endpoints are billed hourly, so they are created for evidence and removed in the same session.
- Budgets and anomaly alerts are configured to catch unexpected spend early.

---

## 👤 Team

| Team Member | Professional Links & Contact |
| :--- | :--- |
| **Ali Wael Ali Soliman** | [![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/alisoliiman/) [![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/Alisoliiman) [![Email](https://img.shields.io/badge/Email-D14836?style=flat-square&logo=gmail&logoColor=white)](mailto:alisoliimannegm@gmail.com) |
| **Mostafa Mohamed Abdrabo** | [![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/mostafa-m-abdrabo/) [![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/mostafaabdrabo2022) [![Email](https://img.shields.io/badge/Email-D14836?style=flat-square&logo=gmail&logoColor=white)](mailto:mostafaabdrabo4900@gmail.com) |
| **Aya Eid Ahmed Mousa** | [![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](https://linkedin.com/in/ayaeid0/) [![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white)]([https://github.com/aya-eid](https://ayaeid15.github.io/ayaeid15/)) [![Email](https://img.shields.io/badge/Email-D14836?style=flat-square&logo=gmail&logoColor=white)](mailto:ayaeid1501@gmail.com) |
| **Ahmed Sayed Hatem Mohamed** | [![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/ahmed-sayed-59601b37a) [![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/as22w44a-2020) [![Email](https://img.shields.io/badge/Email-D14836?style=flat-square&logo=gmail&logoColor=white)](mailto:as1122w33a@gmail.com) |
| **Lamees Mamdouh Ibrahim Abdelhamed** | [![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/lamees-mamdouh-606b7a373) [![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/lamees-mamdouh1) [![Email](https://img.shields.io/badge/Email-D14836?style=flat-square&logo=gmail&logoColor=white)](mailto:lameesmamdouh2005@gmail.com) |
| **Ahmed Zakaria Ismail Elmahdy** | [![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/ahmed-zakaria2/) [![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/AHMED-ZEKOo) [![Email](https://img.shields.io/badge/Email-D14836?style=flat-square&logo=gmail&logoColor=white)](mailto:ahmedzaka557@gmail.com) |
---
