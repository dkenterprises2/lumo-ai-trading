from typing import Optional
from sqlalchemy import String, Float, Integer, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from backend.database.session import Base

class TenantModel(Base):
    """Tenants Table."""
    __tablename__ = "tenants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tenant_id: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)

class OrganizationModel(Base):
    """Organizations Table."""
    __tablename__ = "organizations"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    org_id: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)

class WorkspaceModel(Base):
    """Workspaces Table."""
    __tablename__ = "workspaces"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    workspace_id: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)

class TenantUserModel(Base):
    """Tenant Users Table."""
    __tablename__ = "tenant_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_email: Mapped[str] = mapped_column(String, index=True, nullable=False)

class RoleModel(Base):
    """Roles Table."""
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    role_name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class PermissionModel(Base):
    """Permissions Table."""
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    permission_name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class RoleAssignmentModel(Base):
    """Role Assignments Table."""
    __tablename__ = "role_assignments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_email: Mapped[str] = mapped_column(String, index=True, nullable=False)

class SSOProviderModel(Base):
    """SSO Providers Table."""
    __tablename__ = "sso_providers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    provider_name: Mapped[str] = mapped_column(String, nullable=False)

class TenantSessionModel(Base):
    """Tenant Sessions Table."""
    __tablename__ = "tenant_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class SubscriptionModel(Base):
    """Subscriptions Table."""
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tenant_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class InvoiceModel(Base):
    """Invoices Table."""
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    invoice_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class UsageRecordModel(Base):
    """Usage Records Table."""
    __tablename__ = "usage_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    category: Mapped[str] = mapped_column(String, index=True, nullable=False)

class QuotaLimitModel(Base):
    """Quota Limits Table."""
    __tablename__ = "quota_limits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    category: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class FeatureFlagAssignmentModel(Base):
    """Feature Flag Assignments Table."""
    __tablename__ = "feature_flag_assignments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    flag_name: Mapped[str] = mapped_column(String, nullable=False)

class LicenseEntitlementModel(Base):
    """License Entitlements Table."""
    __tablename__ = "license_entitlements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    license_key: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class BrandingAssetModel(Base):
    """Branding Assets Table."""
    __tablename__ = "branding_assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tenant_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class CustomDomainModel(Base):
    """Custom Domains Table."""
    __tablename__ = "custom_domains"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    domain: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class SSLCertificateModel(Base):
    """SSL Certificates Table."""
    __tablename__ = "ssl_certificates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    domain: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class APIKeyModel(Base):
    """API Keys Table."""
    __tablename__ = "api_keys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    key_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class DeveloperAppModel(Base):
    """Developer Apps Table."""
    __tablename__ = "developer_apps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    app_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class WebhookEndpointModel(Base):
    """Webhook Endpoints Table."""
    __tablename__ = "webhook_endpoints"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    webhook_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class WebhookDeliveryModel(Base):
    """Webhook Deliveries Table."""
    __tablename__ = "webhook_deliveries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    delivery_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class IntegrationInstallationModel(Base):
    """Integration Installations Table."""
    __tablename__ = "integration_installations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    integration_name: Mapped[str] = mapped_column(String, nullable=False)

class TenantBackupJobModel(Base):
    """Tenant Backup Jobs Table."""
    __tablename__ = "tenant_backup_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    backup_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class RestoreOperationModel(Base):
    """Restore Operations Table."""
    __tablename__ = "restore_operations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    operation_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class TenantAdminActionModel(Base):
    """Tenant Admin Actions Table."""
    __tablename__ = "tenant_admin_actions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    action_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class OnboardingFlowModel(Base):
    """Onboarding Flows Table."""
    __tablename__ = "onboarding_flows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    flow_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
