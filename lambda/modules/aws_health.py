from enum import Enum
from typing import Any, Dict
from .aws_service import AwsService


class AwsHealth(Enum):
    """Maps AWS Health eventTypeCategory to Slack message format color

    eventTypeCategory
        The category code of the event. The possible values are issue,
        accountNotification, and scheduledChange.
    """

    accountNotification = "#777777"
    scheduledChange = "warning"
    issue = "danger"

    @staticmethod
    def format(message: Dict[str, Any], region: str) -> Dict[str, Any]:
        """
        Format AWS Health event into Slack message format

        :params message: SNS message body containing AWS Health event
        :params region: AWS region where the event originated from
        :returns: formatted Slack message payload
        """

        aws_health_url = AwsService.get_service_url(region, "awshealth")

        detail = message["detail"]
        resources = message.get("resources", "<unknown>")
        service = detail.get("service", "<unknown>")

        return {
            "color": AwsHealth[detail["eventTypeCategory"]].value,
            "text": f"New AWS Health Event for {service}",
            "fallback": f"New AWS Health Event for {service}",
            "fields": [
                {"title": "Affected Service", "value": f"`{service}`", "short": True},
                {
                    "title": "Affected Region",
                    "value": f"`{message.get('region')}`",
                    "short": True,
                },
                {
                    "title": "Code",
                    "value": f"`{detail.get('eventTypeCode')}`",
                    "short": False,
                },
                {
                    "title": "Event Description",
                    "value": f"`{detail['eventDescription'][0]['latestDescription']}`",
                    "short": False,
                },
                {
                    "title": "Affected Resources",
                    "value": f"`{', '.join(resources)}`",
                    "short": False,
                },
                {
                    "title": "Start Time",
                    "value": f"`{detail.get('startTime', '<unknown>')}`",
                    "short": True,
                },
                {
                    "title": "End Time",
                    "value": f"`{detail.get('endTime', '<unknown>')}`",
                    "short": True,
                },
                {
                    "title": "Link to Event",
                    "value": f"{aws_health_url}",
                    "short": False,
                },
            ],
        }
