from typing import Optional
from sqlalchemy import String, Float, Integer, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from backend.database.session import Base

class SecurityModel(Base):
    """Securities Master Table."""
    __tablename__ = "securities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    asset_id: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    asset_class: Mapped[str] = mapped_column(String, nullable=False)
    exchange: Mapped[str] = mapped_column(String, nullable=False)

class AssetPriceModel(Base):
    """Asset Prices Table."""
    __tablename__ = "asset_prices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    asset_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)

class BrokerAccountModel(Base):
    """Broker Accounts Table."""
    __tablename__ = "broker_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    broker_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class PrimeBrokerRelationshipModel(Base):
    """Prime Broker Relationships Table."""
    __tablename__ = "prime_broker_relationships"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    relationship_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class OMSOrderModel(Base):
    """OMS Orders Table."""
    __tablename__ = "oms_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    order_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class EMSRouteModel(Base):
    """EMS Routes Table."""
    __tablename__ = "ems_routes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    route_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class WalletAddressModel(Base):
    """Wallet Addresses Table."""
    __tablename__ = "wallet_addresses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    address: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class OnChainBalanceModel(Base):
    """On-Chain Balances Table."""
    __tablename__ = "onchain_balances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    address: Mapped[str] = mapped_column(String, index=True, nullable=False)

class UnifiedPositionModel(Base):
    """Unified Positions Table."""
    __tablename__ = "unified_positions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    symbol: Mapped[str] = mapped_column(String, nullable=False)

class ArbitrageOpportunityModel(Base):
    """Arbitrage Opportunities Table."""
    __tablename__ = "arbitrage_opportunities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    opp_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class CollateralAllocationModel(Base):
    """Collateral Allocations Table."""
    __tablename__ = "collateral_allocations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    allocation_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class MarginRequirementModel(Base):
    """Margin Requirements Table."""
    __tablename__ = "margin_requirements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    venue: Mapped[str] = mapped_column(String, nullable=False)

class TreasuryPositionModel(Base):
    """Treasury Positions Table."""
    __tablename__ = "treasury_positions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    asset: Mapped[str] = mapped_column(String, nullable=False)

class YieldOpportunityModel(Base):
    """Yield Opportunities Table."""
    __tablename__ = "yield_opportunities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    venue: Mapped[str] = mapped_column(String, nullable=False)

class GlobalRiskSnapshotModel(Base):
    """Global Risk Snapshots Table."""
    __tablename__ = "global_risk_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    snapshot_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class SettlementInstructionModel(Base):
    """Settlement Instructions Table."""
    __tablename__ = "settlement_instructions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    instruction_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class CustodyAccountModel(Base):
    """Custody Accounts Table."""
    __tablename__ = "custody_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    custodian: Mapped[str] = mapped_column(String, nullable=False)

class HedgingProgramModel(Base):
    """Hedging Programs Table."""
    __tablename__ = "hedging_programs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    program_name: Mapped[str] = mapped_column(String, nullable=False)

class MultiEntityPortfolioModel(Base):
    """Multi-Entity Portfolios Table."""
    __tablename__ = "multi_entity_portfolios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    entity_name: Mapped[str] = mapped_column(String, nullable=False)
