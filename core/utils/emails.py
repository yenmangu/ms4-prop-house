from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string


class TransactionalMail(EmailMessage):
    """
    Core custom email class inheriting from native
    Django EmailMessage.

    Simplifies HTML template rendering whilst retaining
    native mail capabilities.
    """

    def __init__(
        self,
        template_name,
        subject,
        context=None,
        to=None,
        *args,
        **kwargs,
    ):

        # Default config fallback
        if "from_email" not in kwargs:
            kwargs["from_email"] = settings.DEFAULT_FROM_EMAIL

        # Render out the HTML body content using
        # template paths.
        html_body = render_to_string(
            template_name,
            context or {},
        )

        # Pass the rendered body and remaining
        # arguments to the parent constructor
        super().__init__(
            subject=subject,
            body=html_body,
            to=to,
            *args,
            **kwargs,
        )

        # Explicitly tell Django/Anymail to treat
        # payload string as HTML markup.
        self.content_subtype = "html"
