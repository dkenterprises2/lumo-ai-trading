"""
Learning Governance Integration for Phase 25 Self-Learning Feedback Loop.
Manages multi-stage governance workflow and enforces human approval requirement before production deployment.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy import select, update

from backend.database.session import AsyncSessionLocal
from backend.models.domain import LearningDeploymentApproval, LearningWeightExperiment, ActiveStrategyWeights, AuditLogModel
from backend.learning.strategy_weight_loader import strategy_weight_loader
from backend.core.logger import logger


class LearningGovernanceManager:
    """Governance Workflow Manager for self-learning strategy weight deployments."""

    VALID_STATUSES = ["DRAFT", "UNDER_REVIEW", "SHADOW_APPROVED", "PRODUCTION_APPROVED", "REJECTED"]

    async def submit_for_review(self, experiment_id: str, notes: str = "") -> Dict[str, Any]:
        """
        Submits an experiment candidate for governance review.
        """
        async with AsyncSessionLocal() as session:
            stmt = select(LearningWeightExperiment).where(LearningWeightExperiment.experiment_id == experiment_id)
            res = await session.execute(stmt)
            exp = res.scalars().first()
            if not exp:
                return {"status": "error", "message": f"Experiment {experiment_id} not found"}

            import uuid
            approval_id = f"APP_{experiment_id}_{uuid.uuid4().hex[:8]}"

            approval = LearningDeploymentApproval(
                approval_id=approval_id,
                experiment_id=experiment_id,
                status="UNDER_REVIEW",
                human_approval=False,
                approved_by="",
                notes=notes or "Submitted for governance review after shadow evaluation",
                created_at=datetime.now(timezone.utc)
            )
            session.add(approval)
            await session.commit()
            await session.refresh(approval)

        logger.info(f"[GOVERNANCE] Submitted experiment {experiment_id} under approval_id={approval_id}")
        return {
            "status": "success",
            "approval_id": approval_id,
            "experiment_id": experiment_id,
            "governance_status": "UNDER_REVIEW"
        }

    async def approve_and_deploy(
        self,
        experiment_id: str,
        approver_email: str,
        human_approval: bool = True,
        notes: str = "Production deployment approved"
    ) -> Dict[str, Any]:
        """
        Approves and deploys candidate weights into production after strict human approval.
        """
        if not human_approval:
            return {"status": "error", "message": "Production deployment requires explicit human_approval = True."}

        async with AsyncSessionLocal() as session:
            stmt = select(LearningWeightExperiment).where(LearningWeightExperiment.experiment_id == experiment_id)
            res = await session.execute(stmt)
            exp = res.scalars().first()
            if not exp:
                return {"status": "error", "message": f"Experiment {experiment_id} not found"}

            weights = json.loads(exp.weights_json) if exp.weights_json else {}

            # Deactivate previous weights for this strategy and regime
            await session.execute(
                update(ActiveStrategyWeights)
                .where(
                    ActiveStrategyWeights.strategy_name == exp.strategy_name,
                    ActiveStrategyWeights.market_regime == exp.market_regime
                )
                .values(is_active=False)
            )

            # Get highest version
            stmt_ver = select(ActiveStrategyWeights).where(ActiveStrategyWeights.strategy_name == exp.strategy_name).order_by(ActiveStrategyWeights.version.desc())
            res_ver = await session.execute(stmt_ver)
            last_ver = res_ver.scalars().first()
            new_version = (last_ver.version + 1) if last_ver else 1

            new_weights_entry = ActiveStrategyWeights(
                strategy_name=exp.strategy_name,
                market_regime=exp.market_regime,
                version=new_version,
                is_active=True,
                weights_json=json.dumps(weights),
                deployed_by=approver_email,
                created_at=datetime.now(timezone.utc)
            )
            session.add(new_weights_entry)

            # Record or update governance approval
            stmt_app = select(LearningDeploymentApproval).where(LearningDeploymentApproval.experiment_id == experiment_id)
            res_app = await session.execute(stmt_app)
            approval = res_app.scalars().first()
            if approval:
                approval_id = approval.approval_id
                approval.status = "PRODUCTION_APPROVED"
                approval.human_approval = True
                approval.approved_by = approver_email
                approval.notes = notes
                approval.deployed_at = datetime.now(timezone.utc)

            else:
                import uuid
                approval_id = f"APP_{experiment_id}_{uuid.uuid4().hex[:8]}"
                approval = LearningDeploymentApproval(
                    approval_id=approval_id,
                    experiment_id=experiment_id,
                    status="PRODUCTION_APPROVED",
                    human_approval=True,
                    approved_by=approver_email,
                    notes=notes,
                    created_at=datetime.now(timezone.utc),
                    deployed_at=datetime.now(timezone.utc)
                )
                session.add(approval)


            # Add to audit log
            audit = AuditLogModel(
                event_type="STRATEGY_WEIGHT_DEPLOYMENT",
                details=f"Deployed version {new_version} for {exp.strategy_name} ({exp.market_regime}) by {approver_email}. Experiment={experiment_id}. Weights={weights}"
            )
            session.add(audit)

            await session.commit()

        # Trigger hot reload in strategy weight loader
        await strategy_weight_loader.reload_weights(exp.strategy_name, exp.market_regime)

        logger.info(f"[GOVERNANCE_DEPLOY] Successfully deployed version {new_version} for {exp.strategy_name} by {approver_email}")
        return {
            "status": "success",
            "approval_id": approval_id,
            "experiment_id": experiment_id,
            "deployed_version": new_version,
            "governance_status": "PRODUCTION_APPROVED",
            "weights": weights
        }

    async def get_approvals(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Gets recent governance approval records."""
        async with AsyncSessionLocal() as session:
            stmt = select(LearningDeploymentApproval).order_by(LearningDeploymentApproval.id.desc()).limit(limit)
            res = await session.execute(stmt)
            records = res.scalars().all()
            return [
                {
                    "approval_id": r.approval_id,
                    "experiment_id": r.experiment_id,
                    "status": r.status,
                    "human_approval": r.human_approval,
                    "approved_by": r.approved_by,
                    "notes": r.notes,
                    "created_at": r.created_at.isoformat() if r.created_at else "",
                    "deployed_at": r.deployed_at.isoformat() if r.deployed_at else ""
                }
                for r in records
            ]


learning_governance = LearningGovernanceManager()
