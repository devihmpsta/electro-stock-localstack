import logging
from app.infrastructure.aws import get_ec2_client

logger = logging.getLogger(__name__)

class EC2Service:
    """
    Application Service for managing EC2 operations via Boto3 with LocalStack.
    """
    def __init__(self) -> None:
        self.ec2_client = get_ec2_client()

    def list_instances(self) -> list:
        """Lists all EC2 instances from the LocalStack environment."""
        instances = []
        try:
            response = self.ec2_client.describe_instances()
            for reservation in response.get('Reservations', []):
                for inst in reservation.get('Instances', []):
                    # Get Name tag if exists
                    name = '-'
                    for tag in inst.get('Tags', []):
                        if tag.get('Key') == 'Name':
                            name = tag.get('Value')
                            break
                            
                    state_name = inst.get('State', {}).get('Name', 'unknown')
                    
                    instances.append({
                        'instance_id': inst.get('InstanceId'),
                        'image_id': inst.get('ImageId'),
                        'instance_type': inst.get('InstanceType'),
                        'state': state_name,
                        'public_ip': inst.get('PublicIpAddress', '-'),
                        'private_ip': inst.get('PrivateIpAddress', '-'),
                        'launch_time': inst.get('LaunchTime'),
                        'name': name
                    })
        except Exception as e:
            logger.error(f"Error listing EC2 instances from LocalStack: {e}")
        return instances

    def create_instance(self, name: str | None = None, instance_type: str = 't2.micro', image_id: str = 'ami-df5de7b8') -> dict | None:
        """Launches a new mock EC2 instance in LocalStack."""
        try:
            tag_specifications = []
            if name:
                tag_specifications = [{
                    'ResourceType': 'instance',
                    'Tags': [{'Key': 'Name', 'Value': name}]
                }]
                
            response = self.ec2_client.run_instances(
                ImageId=image_id,
                InstanceType=instance_type,
                MinCount=1,
                MaxCount=1,
                TagSpecifications=tag_specifications
            )
            
            instances = response.get('Instances', [])
            if instances:
                inst = instances[0]
                inst_id = inst.get('InstanceId')
                logger.info(f"Successfully launched EC2 instance '{inst_id}' on LocalStack.")
                return {
                    'instance_id': inst_id,
                    'state': inst.get('State', {}).get('Name', 'pending'),
                    'name': name or '-'
                }
        except Exception as e:
            logger.error(f"Error launching EC2 instance: {e}")
        return None

    def stop_instance(self, instance_id: str) -> bool:
        """Stops a running EC2 instance."""
        try:
            self.ec2_client.stop_instances(InstanceIds=[instance_id])
            logger.info(f"Sent stop command to EC2 instance '{instance_id}'.")
            return True
        except Exception as e:
            logger.error(f"Error stopping EC2 instance '{instance_id}': {e}")
            return False

    def start_instance(self, instance_id: str) -> bool:
        """Starts a stopped EC2 instance."""
        try:
            self.ec2_client.start_instances(InstanceIds=[instance_id])
            logger.info(f"Sent start command to EC2 instance '{instance_id}'.")
            return True
        except Exception as e:
            logger.error(f"Error starting EC2 instance '{instance_id}': {e}")
            return False

    def terminate_instance(self, instance_id: str) -> bool:
        """Terminates an EC2 instance."""
        try:
            self.ec2_client.terminate_instances(InstanceIds=[instance_id])
            logger.info(f"Sent terminate command to EC2 instance '{instance_id}'.")
            return True
        except Exception as e:
            logger.error(f"Error terminating EC2 instance '{instance_id}': {e}")
            return False

    def describe_instance(self, instance_id: str) -> dict | None:
        """Retrieves details of a specific EC2 instance."""
        try:
            response = self.ec2_client.describe_instances(InstanceIds=[instance_id])
            for reservation in response.get('Reservations', []):
                for inst in reservation.get('Instances', []):
                    name = '-'
                    for tag in inst.get('Tags', []):
                        if tag.get('Key') == 'Name':
                            name = tag.get('Value')
                            break
                    return {
                        'instance_id': inst.get('InstanceId'),
                        'image_id': inst.get('ImageId'),
                        'instance_type': inst.get('InstanceType'),
                        'state': inst.get('State', {}).get('Name', 'unknown'),
                        'public_ip': inst.get('PublicIpAddress', '-'),
                        'private_ip': inst.get('PrivateIpAddress', '-'),
                        'launch_time': inst.get('LaunchTime'),
                        'name': name
                    }
        except Exception as e:
            logger.error(f"Error describing EC2 instance '{instance_id}': {e}")
        return None
