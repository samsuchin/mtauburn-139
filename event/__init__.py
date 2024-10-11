class EVENT:
    PEOPLE_CHOICES = [
        ("default", "Default"),
        ("member", "Member"),
        ("blacklist", "Blacklist"),
    ]

    DEFAULT_INVITE_TEMPLATE = """Hi {name},

You are invited to {event_name}.

Your unique QR code: {code}
    """
