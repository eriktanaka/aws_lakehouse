terraform {
  backend "s3" {
    bucket         = "datashi-projects"        
    key            = "datalake/terraform.tfstate"   
    region         = "us-east-2"                    
    dynamodb_table = "terraform-state-lock"         
    encrypt        = true
  }
}