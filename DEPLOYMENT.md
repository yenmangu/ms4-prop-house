# Deployment

> [!TIP]
> Return back to the [README.md](README.md) file.

This document explains the setup, connection, and deployment of the **Prop House** platform, both on a live server and locally on a machine.

The project implements a **split deployment strategy**:

- **Heroku:** Hosts the live, interactive Django web application.
- **GitHub:** Used exclusively to host public documentation and static assessment assets (such as testing logs and Lighthouse reports). The live application itself is never served via this channel.

---

## 1. External Service Accounts Setup

Prior to deploying to Heroku or running the application locally, accounts must be established with external services. The following sections outline the requirements from each respective dashboard:

### A. Cloudinary (Media Asset Storage)

Because Heroku utilises an ephemeral file system where uploaded files are deleted upon application restarts, all media assets and product images are offloaded to Cloudinary.

1. Registration for a free account is required at Cloudinary.
2. The **Cloud Name**, **API Key**, and **API Secret** must be retrieved from the dashboard console.
3. A combined connection string, designated as the **API Environment variable** (`CLOUDINARY_URL=cloudinary://...`), is provided and must be copied in its entirety.

### B. Stripe (Payment Processing)

Prop House integrates with Stripe to handle secure checkouts.

1. Access to the Stripe Dashboard is required via registration or login.
2. The dashboard must be toggled into **Test Mode** (live production keys must not be used for testing or grading purposes).
3. The **Publishable key** (`pk_test_...`) and **Secret key** (`sk_test_...`) must be obtained from the **Developers -> API Keys** section.
4. For the processing of automated webhooks (such as fulfilling orders after a successful payment), an endpoint pointing to the application webhook URL must be added under the **Webhooks** tab, and the generated **Webhook Signing Secret** (`whsec_...`) must be copied.

### C. Resend (Transactional Email Engine)

The application utilises `django-anymail` backed by Resend to deliver account confirmation and registration links.

1. An account must be created at Resend.
2. Two keys must be generated within the **API Keys** section: one for local development (`RESEND_DEV_KEY`) and one for the production server (`RESEND_PROD_KEY`).
3. **Sandbox Limitations:** By default, newly created accounts operate in sandbox mode. Emails are strictly restricted to the email address used during the creation of the Resend account. Any attempts to register with an alternative email address will result in an HTTP 403 error. To remove this restriction for production, a verified custom domain must be configured within the Resend dashboard.

---

## 2. Deploying Prop House to Heroku

The following steps outline the procedure to deploy the application live.

### Create a Heroku App

1. Login to the Heroku dashboard is required.
2. Selecting **New → Create new app** is necessary.
3. A unique application name must be specified, and the closest geographical region (e.g., Europe) selected.
4. The **Create app** button must be clicked.

### Attach a PostgreSQL Database

1. Navigation to the **Resources** tab of the newly created Heroku application is required.
2. Within the Add-ons search bar, **Heroku Postgres** must be located.
3. The appropriate tier (such as the free tier) must be selected and provisioned. This process automatically attaches a live database and injects the `DATABASE_URL` configuration variable.

### Configure Environment Variables

Sensitive keys are never committed to GitHub. Instead, these credentials must be added securely to Heroku:

1. Within the Heroku application dashboard, navigation to **Settings → Reveal Config Vars** is required.
2. The following keys must be appended exactly as specified below:

| Key                     | Value / Description                                                                                 |
| ----------------------- | --------------------------------------------------------------------------------------------------- |
| `SECRET_KEY`            | The custom Django secret key                                                                        |
| `CLOUDINARY_API`        | The Cloudinary API key                                                                              |
| `CLOUDINARY_SECRET`     | The Cloudinary API secret                                                                           |
| `CLOUDINARY_URL`        | The complete `cloudinary://...` connection string                                                   |
| `RESEND_PROD_KEY`       | The live production Resend API Key                                                                  |
| `STRIPE_PUBLIC`         | The Stripe Publishable Key (`pk_test_...`)                                                          |
| `STRIPE_SECRET`         | The Stripe Secret Key (`sk_test_...`)                                                               |
| `STRIPE_WH`             | The live production Stripe Webhook Signing Secret (`whsec_...`)                                     |
| `DISABLE_COLLECTSTATIC` | `1` _(Temporary: removal is required once the design layout and static files are fully configured)_ |

### Prepare Code for Production

Prior to pushing the deployment branch, verification is required to ensure the project contains the vital production configurations listed below:

- **`requirements.txt`:** Holds all required project dependencies. The presence of `gunicorn`, `psycopg2`, `django-anymail`, and `whitenoise` must be verified.
- **`Procfile`:** Instructs Heroku on how to initiate the web server dyno. The file must contain:
  ```text
  web: gunicorn prop_house.wsgi
  ```
- **`settings.py`:** Verification is required to ensure that `DEBUG` is dynamically disabled when running on Heroku (`IS_HEROKU_APP`), `ALLOWED_HOSTS` includes the Heroku application domain, and `Whitenoise` is registered within the middleware array to manage static assets.

### Connect GitHub and Deploy

1. Within the Heroku application dashboard, the **Deploy** tab must be selected.
2. **GitHub** must be selected as the deployment method.
3. A search for the repository (`ms4-prop-house`) must be conducted, followed by selecting **Connect**.
4. Within the manual deployment section, the primary branch (typically `main`) must be selected, followed by clicking **Deploy Branch**.
5. Monitoring of the logs is required until a **"Build succeeded"** confirmation text is displayed.

### Run Database Migrations & Admin Accounts

Upon successful build completion, the remote database tables must be configured:

1. In the top right corner of the Heroku dashboard, **More -> Run console** must be selected.
2. The command `python manage.py migrate` must be entered and submitted.
3. To enable access to the administration panel on the live site, the console must be opened again to generate a superuser account via the following command:

```bash
python manage.py createsuperuser
```

---

## 3. Local Development Setup

The following steps outline the procedure to run the Prop House codebase on a local machine for development or testing purposes.

### Prerequisites

The installation of **Python 3.x**, **pip**, and **Git** on the system is required as a prerequisite.

### Installation Steps

1. The repository must be cloned from GitHub:
   ```bash
   git clone https://github.com/yenmangu/ms4-prop-house.git
   ```
2. Navigation directly into the root project directory is required:
   ```bash
   cd ms4-prop-house
   ```
3. An isolated Python virtual environment must be initialised and activated:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

   On Windows systems:

   ```cmd
   .venv\Scripts\activate
   ```

4. All required software packages and dependencies must be installed:
   ```bash
   pip install -r requirements.txt
   ```
5. A file designated as `env.py` must be created in the project root directory. This file stores local credentials and secrets securely outside of version control, and must be populated as follows:

   ```py
   import os

   os.environ.setdefault("SECRET_KEY", "your_local_development_secret_key")
   os.environ.setdefault("DATABASE_URL", "postgresql://user:password@localhost:5432/prop_house")
   os.environ.setdefault("CLOUDINARY_URL", "cloudinary://your_api_keys_here")
   os.environ.setdefault("RESEND_DEV_KEY", "re_your_local_dev_key")
   os.environ.setdefault("STRIPE_PUBLIC", "pk_test_your_key")
   os.environ.setdefault("STRIPE_SECRET", "sk_test_your_key")
   os.environ.setdefault("STRIPE_LOCAL_WH", "whsec_your_local_webhook_secret")
   ```

6. The initial database structural migrations must be executed:
   ```bash
   python manage.py migrate
   ```
7. A local superuser account must be generated to test administration features:
   ```bash
   python manage.py createsuperuser
   ```
8. The local development server engine must be started:
   ```bash
   python manage.py runserver
   ```

The running platform can be accessed and interacted with by opening `http://127.0.0.1:8000/` within a web browser.
