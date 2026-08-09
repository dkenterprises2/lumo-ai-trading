from typing import Optional
from sqlalchemy import String, Float, Integer, Boolean, DateTime, func, JSON
from sqlalchemy.orm import Mapped, mapped_column
from backend.database.session import Base

class OrganizationModel(Base):
    """Organizations Table."""
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    org_id: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    slug: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    owner_id: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())

class OrganizationMemberModel(Base):
    """Organization Members Table."""
    __tablename__ = "organization_members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    org_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    role: Mapped[str] = mapped_column(String, default="MEMBER")
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())

class OrganizationInvitationModel(Base):
    """Organization Invitations Table."""
    __tablename__ = "organization_invitations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    org_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    token: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    role: Mapped[str] = mapped_column(String, default="MEMBER")
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())

class OrganizationAuditLogModel(Base):
    """Organization Audit Logs Table."""
    __tablename__ = "organization_audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    org_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    actor: Mapped[str] = mapped_column(String, nullable=False)
    action: Mapped[str] = mapped_column(String, nullable=False)
    details: Mapped[str] = mapped_column(String, default="")
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())

class SubscriptionPlanModel(Base):
    """Subscription Plans Table."""
    __tablename__ = "subscription_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    plan_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    price_usd: Mapped[float] = mapped_column(Float, nullable=False)

class SubscriptionModel(Base):
    """Subscriptions Table."""
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    org_id: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    plan_id: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, default="ACTIVE")
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())

class InvoiceModel(Base):
    """Invoices Table."""
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    invoice_id: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    org_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    amount_usd: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String, default="PAID")
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())

class PaymentModel(Base):
    """Payments Table."""
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    payment_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    org_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    amount_usd: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())

class APIKeyModel(Base):
    """API Keys Table."""
    __tablename__ = "api_keys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    key_id: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    org_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    key_prefix: Mapped[str] = mapped_column(String, nullable=False)
    secret_hash: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())

class APIUsageRecordModel(Base):
    """API Usage Records Table."""
    __tablename__ = "api_usage_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    org_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    endpoint: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())

class TenantBrandingModel(Base):
    """Tenant Branding Table."""
    __tablename__ = "tenant_branding"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    org_id: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    company_name: Mapped[str] = mapped_column(String, nullable=False)
    logo_url: Mapped[str] = mapped_column(String, default="")

class TenantSettingsModel(Base):
    """Tenant Settings Table."""
    __tablename__ = "tenant_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    org_id: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    settings: Mapped[dict] = mapped_column(JSON, default={})

class RateLimitBucketModel(Base):
    """Rate Limit Buckets Table."""
    __tablename__ = "rate_limit_buckets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    org_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    requests_count: Mapped[int] = mapped_column(Integer, default=0)

class UsageQuotaModel(Base):
    """Usage Quotas Table."""
    __tablename__ = "usage_quotas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    org_id: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    monthly_limit: Mapped[int] = mapped_column(Integer, default=100000)
