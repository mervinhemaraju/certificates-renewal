VALUE_COLOR_NEGATIVE = "#ff7b7b"
VALUE_COLOR_STATEMENT = "#ffac5a"
VALUE_COLOR_POSITIVE = "#71ff6e"


def block_completed():
    return [
        {
            "color": VALUE_COLOR_POSITIVE,
            "blocks": [
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": "Certificates renewal script completed successfully.",
                        }
                    ],
                },
            ],
        }
    ]


def block_info(message):
    return [
        {
            "color": VALUE_COLOR_STATEMENT,
            "blocks": [
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": message,
                        },
                    ],
                },
            ],
        }
    ]


def block_error(error_message):
    return [
        {
            "color": VALUE_COLOR_NEGATIVE,
            "blocks": [
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Error:*\n{error_message}",
                        },
                    ],
                },
            ],
        }
    ]
