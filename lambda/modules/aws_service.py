from enum import Enum


class AwsService(Enum):
    """AWS service supported by function"""

    cloudwatch = "cloudwatch"
    guardduty = "guardduty"
    awshealth = "awshealth"

    @staticmethod
    def get_service_url(region: str, service: str) -> str:
        """Get the appropriate service URL for the region

        :param region: name of the AWS region
        :param service: name of the AWS service
        :returns: AWS console url formatted for the region and service provided
        """
        try:
            service_name = AwsService[service].value
            if service_name == "awshealth":
                return f"https://phd.aws.amazon.com/phd/home?region={region}#/dashboard/open-issues"

            if region.startswith("us-gov-"):
                return f"https://console.amazonaws-us-gov.com/{service_name}/home?region={region}"
            else:
                return f"https://console.aws.amazon.com/{service_name}/home?region={region}"

        except KeyError:
            print(f"Service {service} is currently not supported")
            raise
