def block_success():
    return [
        {
            "color": "#38ff70",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "SSL Certificates Sync",
                        "emoji": False
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": "The Certificates have been synchronized successfully."},
                    ],
                },
            ],
        }
    ]

def block_error(error_message:str):
    return [
        {
            "color": "#ff5c5c",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "SSL Certificates Sync Error",
                        "emoji": False
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Error:*\n{error_message}"}
                    ],
                },
            ],
        }
    ]