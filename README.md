
# SSL Certificate Renewal System

## Overview

The SSL Certificate Renewal System is an automated infrastructure solution designed to manage Let's Encrypt SSL certificates for web applications deployed on Oracle Cloud Infrastructure (OCI). The system handles the complete lifecycle of SSL certificates including generation, renewal, synchronization, and deployment to load balancers.

## System Architecture

### Core Components

The system consists of two main components:

1. **Certificate Renewal Function** (**components/functions/renew/**)
2. **Infrastructure as Code** (**components/iac/**)

### Technology Stack

* **Runtime** : Python 3.13
* **Cloud Provider** : Oracle Cloud Infrastructure (OCI) + AWS Lambda
* **Certificate Authority** : Let's Encrypt via Certbot
* **DNS Provider** : Cloudflare (for DNS-01 challenges)
* **Infrastructure** : Terraform
* **Notifications** : Slack integration
* **Secret Management** : Doppler SDK
* **Container Platform** : Docker with AWS ECR

## How It Works

### Certificate Renewal Process

The renewal process is triggered automatically via AWS EventBridge Scheduler on the first Sunday of each month at 09:00 Mauritius Time. The Lambda function handles the complete certificate lifecycle in a single operation.

**Workflow:**

* AWS Lambda function checks existing certificate expiration (15 days before expiry)
* If renewal is needed, initiates Let's Encrypt certificate generation using Certbot
* Uses Cloudflare DNS-01 challenge for domain validation
* Supports wildcard certificates for ***.mervinhemaraju.com** and ***.plagueworks.org**
* Backs up existing certificates to OCI Object Storage before replacing them
* Uploads new certificates to OCI Object Storage in organized directory structure
* Creates new certificate entries in OCI Load Balancer
* Updates all SSL listeners on the load balancer with the new certificate
* Sends Slack notifications for success/failure throughout the process

## Infrastructure Details

### AWS Components

* **Lambda Function** : Containerized Python application for certificate renewal
* **ECR Repository** : Stores Docker images for Lambda deployment
* **EventBridge Scheduler** : Automated monthly execution
* **IAM Roles** : Secure access permissions for Lambda and Scheduler

### OCI Components

* **Object Storage** : Certificate storage with live/backup/dumps organization
* **Load Balancer** : Target for certificate deployment
* **Cross-Account Access** : Secure communication between different OCI accounts

### Storage Organization

<pre class="code-block" data-language="" data-prosemirror-content-type="node" data-prosemirror-node-name="codeBlock" data-prosemirror-node-block="true"><div class="code-block--start" contenteditable="false"></div><div class="code-block-content-wrapper"><div contenteditable="false"><div class="code-block-gutter-pseudo-element" data-label="1
2
3
4
5
6
7
8"></div></div><div class="code-content"><code data-language="" spellcheck="false" data-testid="code-block--code" aria-label="">certificates/
├── live/san-mervinhemaraju-com-plagueworks-org/
│   ├── cert.pem
│   ├── chain.pem
│   ├── fullchain.pem
│   └── privkey.pem
├── backup/san-mervinhemaraju-com-plagueworks-org/
</code></div></div><div class="code-block--end" contenteditable="false"></div></pre>

## Security Features

### Secret Management

* Doppler SDK for centralized secret management
* Cross-account OCI authentication using API keys and fingerprints
* Environment-specific secret isolation (production configuration)
* Secure token management for Cloudflare and Slack integrations

### Access Control

* IAM roles with least-privilege access for AWS Lambda
* OCI Instance Principals and cross-account authentication
* Encrypted secret storage and retrieval

## Monitoring and Notifications

### Slack Integration

* Real-time notifications to **#certificates** channel for normal operations
* Error alerts sent to **#alerts** channel for immediate attention
* Threaded conversations for better organization
* Detailed progress updates throughout the renewal process

### Logging

* Comprehensive CloudWatch logging for Lambda execution
* Structured logging with different severity levels
* Error tracking and debugging capabilities
