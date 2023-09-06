from enum import Enum
from typing import Any, Dict
from .aws_service import AwsService


class GuardDutyFinding(Enum):
    """Maps GuardDuty finding severity to Slack message format color"""

    Low = "#777777"
    Medium = "warning"
    High = "danger"

    @staticmethod
    def format(message: Dict[str, Any], region: str) -> Dict[str, Any]:
        """
        Format GuardDuty finding event into Slack message format

        :params message: SNS message body containing GuardDuty finding event
        :params region: AWS region where the event originated from
        :returns: formatted Slack message payload
        """

        guardduty_url = AwsService.get_service_url(region=region, service="guardduty")
        detail = message["detail"]
        service = detail.get("service", {})
        severity_score = detail.get("severity")

        if severity_score < 4.0:
            severity = "Low"
        elif severity_score < 7.0:
            severity = "Medium"
        else:
            severity = "High"

        return {
            "color": GuardDutyFinding[severity].value,
            "fallback": f"GuardDuty Finding: {detail.get('title')}",
            "fields": [
                {
                    "title": "Description",
                    "value": f"`{detail['description']}`",
                    "short": False,
                },
                {
                    "title": "Finding Type",
                    "value": f"`{detail['type']}`",
                    "short": False,
                },
                {
                    "title": "First Seen",
                    "value": f"`{service['eventFirstSeen']}`",
                    "short": True,
                },
                {
                    "title": "Last Seen",
                    "value": f"`{service['eventLastSeen']}`",
                    "short": True,
                },
                {"title": "Severity", "value": f"`{severity}`", "short": True},
                {"title": "Account ID", "value": f"`{detail['accountId']}`", "short": True},
                {
                    "title": "Count",
                    "value": f"`{service['count']}`",
                    "short": True,
                },
                {
                    "title": "Link to Finding",
                    "value": f"{guardduty_url}#/findings?search=id%3D{detail['id']}",
                    "short": False,
                },
            ],
            "text": f"AWS GuardDuty Finding - {detail.get('title')}",
        }
