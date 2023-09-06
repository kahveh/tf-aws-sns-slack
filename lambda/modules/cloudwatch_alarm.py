from enum import Enum
from typing import Any, Dict
import urllib.parse
from .aws_service import AwsService


class CloudWatchAlarm(Enum):
    """Maps CloudWatch notification state to Slack message format color"""

    OK = "good"
    INSUFFICIENT_DATA = "warning"
    ALARM = "danger"

    @staticmethod
    def format(message: Dict[str, Any], region: str) -> Dict[str, Any]:
        """Format CloudWatch alarm event into Slack message format

        :params message: SNS message body containing CloudWatch alarm event
        :region: AWS region where the event originated from
        :returns: formatted Slack message payload
        """

        cloudwatch_url = AwsService.get_service_url(region=region, service="cloudwatch")
        alarm_name = message["AlarmName"]

        return {
            "color": CloudWatchAlarm[message["NewStateValue"]].value,
            "fallback": f"Alarm {alarm_name} triggered",
            "fields": [
                {"title": "Alarm Name", "value": f"`{alarm_name}`", "short": True},
                {
                    "title": "Alarm Description",
                    "value": f"`{message['AlarmDescription']}`",
                    "short": False,
                },
                {
                    "title": "Alarm reason",
                    "value": f"`{message['NewStateReason']}`",
                    "short": False,
                },
                {
                    "title": "Old State",
                    "value": f"`{message['OldStateValue']}`",
                    "short": True,
                },
                {
                    "title": "Current State",
                    "value": f"`{message['NewStateValue']}`",
                    "short": True,
                },
                {
                    "title": "Link to Alarm",
                    "value": f"{cloudwatch_url}#alarm:alarmFilter=ANY;name={urllib.parse.quote(alarm_name)}",
                    "short": False,
                },
            ],
            "text": f"AWS CloudWatch notification - {message['AlarmName']}",
        }
