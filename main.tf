terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region                      = "us-east-1"
  access_key                  = "mock_access_key"
  secret_key                  = "mock_secret_key"
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  endpoints {
    ec2 = "http://localhost:4566"
  }
}

resource "aws_security_group" "alert_engine_sg" {
  name        = "crypto-alert-engine-sg"
  description = "Security group for Crypto Alert Engine"

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "alert_engine_server" {
  ami           = "ami-12345678" # LocalStack accepts dummy AMI IDs
  instance_type = "t2.micro"

  vpc_security_group_ids = [aws_security_group.alert_engine_sg.id]

  tags = {
    Name = "Crypto-Alert-Engine-Server"
  }
}

output "instance_id" {
  description = "ID of EC2 instance"
  value       = aws_instance.alert_engine_server.id
}