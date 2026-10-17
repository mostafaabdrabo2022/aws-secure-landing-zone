# Data subnet: no internet route
resource "aws_subnet" "data" {
  vpc_id            = aws_vpc.this.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, 20)
  availability_zone = "us-east-1a"

  tags = {
    Name = "${var.environment}-data-subnet"
  }
}

# Private route table (local only, no default route)
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.this.id

  tags = {
    Name = "${var.environment}-private-rt"
  }
}

resource "aws_route_table_association" "private" {
  subnet_id      = aws_subnet.private.id
  route_table_id = aws_route_table.private.id
}

# Data route table (local only, no internet)
resource "aws_route_table" "data" {
  vpc_id = aws_vpc.this.id

  tags = {
    Name = "${var.environment}-data-rt"
  }
}

resource "aws_route_table_association" "data" {
  subnet_id      = aws_subnet.data.id
  route_table_id = aws_route_table.data.id
}

# S3 Gateway endpoint (free)
data "aws_region" "current" {}

resource "aws_vpc_endpoint" "s3" {
  vpc_id            = aws_vpc.this.id
  service_name      = "com.amazonaws.${data.aws_region.current.name}.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = [aws_route_table.private.id, aws_route_table.data.id]

  tags = {
    Name = "${var.environment}-s3-endpoint"
  }
}