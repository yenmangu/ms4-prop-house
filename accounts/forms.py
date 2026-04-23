from typing import Any, Dict, TYPE_CHECKING

from django import forms
from allauth.account.forms import SignupForm, LoginForm


class CustomSignupForm(SignupForm):
    """
    Extends the base Allauth SignupForm to include custom fields
    """

    # Explicitly type hint the fields attributes
    if TYPE_CHECKING:
        fields: Dict[str, forms.Field]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # Now editor knows self.fields['...'] is Field object

        if "email" in self.fields:
            self.fields["email"].label = "Email address"
            self.fields["email"].widget.attrs.update(
                {
                    "class": "industrial-input",
                    "placeholder": "Email address",
                    "type": "email",
                    "autocomplate": "email",
                }
            )

        if "password1" in self.fields:
            self.fields["password1"].widget.attrs.update(
                {
                    "class": "industrial-input",
                    "placeholder": "Password",
                    "type": "password",
                    "autocomplete": "new-password",
                }
            )

        if "password2" in self.fields:
            self.fields["password2"].widget.attrs.update(
                {
                    "class": "industrial-input",
                    "placeholder": "Confirm password",
                    "type": "password",
                    "autocomplete": "new-password",
                }
            )

        def save(self, request: Any) -> Any:
            """
            Standard save logic for allauth
            """
            user = super().save(request)
            return user


class CustomLoginForm(LoginForm):
    """
    Extends base LoginForm from allauth to modify the existing fields
    """

    fields: Dict[str, forms.Field]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "login" in self.fields:
            self.fields["login"].widget.attrs.update(
                {
                    "class": "industrial-input",
                    "placeholder": "Email or Username",
                }
            )

        if "password" in self.fields:
            self.fields["password"].widget.attrs.update(
                {
                    "class": "industrial-input",
                    "type": "password",
                    "placeholder": "Password",
                }
            )

        if "remember" in self.fields:
            self.fields["remember"].widget.attrs.update(
                {
                    "class": "industrial-checkbox",
                    "type": "checkbox",
                }
            )
