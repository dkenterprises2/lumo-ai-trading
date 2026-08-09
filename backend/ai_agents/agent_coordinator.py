from typing import Dict, Any, List

class MultiAgentCoordinator:
    """Multi-Agent Voting & Consensus Coordinator."""

    @staticmethod
    def coordinate_decisions(agent_decisions: List[Dict[str, Any]]) -> Dict[str, Any]:
        votes = {"BUY": 0, "SELL": 0, "HOLD": 0}
        for d in agent_decisions:
            act = d.get("action", "HOLD")
            if act in votes:
                votes[act] += 1
            else:
                votes["HOLD"] += 1
        
        consensus = max(votes, key=votes.get)
        return {
            "consensus_action": consensus,
            "vote_distribution": votes,
            "agent_count": len(agent_decisions)
        }

agent_coordinator = MultiAgentCoordinator()
