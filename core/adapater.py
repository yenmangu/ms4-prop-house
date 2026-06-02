# =========================================================================
# EXTERNAL DEPENDENCY ATTRIBUTION
# Source: django-allauth (https://codeberg.org/allauth/django-allauth)
# Purpose: DefaultAccountAdapter foundation class to override lifecycle
#          account communication logic.
# Localisation: Intercepts automated email workflows to seamlessly map
#               them to internal transactional email layouts.
# =========================================================================
from allauth.account.adapter import DefaultAccountAdapter
from core.utils.emails import TransactionalMail


class PropHouseAccountAdapter(DefaultAccountAdapter):
    """
    Custom account adapter for allauth to intercept
    internal system notifications and handle using
    `core.utils.emails`
    """

    def send_mail(self, template_prefix, email, context):
        """
        Itercept allauth email triggers and processes with TransactionalMail class.
        """

        subject = self.format_email_subject(
            self.render_mail(
                template_prefix=template_prefix,
                email=email,
                context=context,
            ).subject
        )

        # Builds template name using naming convention
        # allauth expects.
        template_name = f"{template_prefix}_message.html"

        # Initialise class, forwarding props
        msg = TransactionalMail(
            subject=subject,
            template_name=template_name,
            context=context,
            to=[email] if isinstance(email, str) else email,
        )

        msg.send()
