terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

resource "aws_vpc" "supportflow" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name        = "supportflow-vpc"
    Project     = "SupportFlow"
    Environment = var.environment
  }
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.supportflow.id
  cidr_block              = var.public_subnet_cidr
  availability_zone       = var.availability_zone
  map_public_ip_on_launch = true

  tags = {
    Name    = "supportflow-public-subnet"
    Project = "SupportFlow"
  }
}

resource "aws_internet_gateway" "supportflow" {
  vpc_id = aws_vpc.supportflow.id

  tags = {
    Name    = "supportflow-igw"
    Project = "SupportFlow"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.supportflow.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.supportflow.id
  }

  tags = {
    Name    = "supportflow-public-route-table"
    Project = "SupportFlow"
  }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

resource "aws_security_group" "web" {
  name        = "supportflow-web"
  description = "Security group for SupportFlow web server"
  vpc_id      = aws_vpc.supportflow.id

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name    = "supportflow-web-sg"
    Project = "SupportFlow"
  }
}