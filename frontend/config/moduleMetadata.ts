export interface ModuleMetadata {
  title: string;
  subtitle: string;
  description: string;
}

export const MODULE_METADATA: Record<string, ModuleMetadata> = {
  risk: {
    title: "Portfolio Risk & Safety Engine",
    subtitle: "Dynamic risk limits, portfolio heat, drawdown protection, and circuit breakers.",
    description: "Institutional Portfolio Intelligence & Risk Optimization Engine"
  },
  execution: {
    title: "Institutional Order & Execution Engine",
    subtitle: "Smart order routing, algorithmic execution, slippage control, and execution telemetry.",
    description: "Institutional OMS / EMS Execution Layer & Smart Order Routing"
  },
  shadow: {
    title: "Shadow Trading & Execution Simulation",
    subtitle: "Real-time shadow execution engine & deterministic market replay simulation.",
    description: "Shadow Trading & Market Replay Simulation Engine"
  },
  arbitrage: {
    title: "Cross-Exchange Arbitrage Intelligence",
    subtitle: "Multi-exchange opportunity detection, spread arbitrage, and dual-leg execution.",
    description: "Cross-Exchange Arbitrage Intelligence & Opportunity Engine"
  },
  news: {
    title: "AI News Intelligence & Event Engine",
    subtitle: "Sentiment analysis, NLP news processing, and event-driven market protection.",
    description: "AI News Intelligence & Event Engine"
  },
  autonomous: {
    title: "Autonomous Execution Control",
    subtitle: "Autonomous Decision → Risk → Governance → OMS/EMS → Shadow Execution Pipeline.",
    description: "Autonomous Trading & Shadow Execution Control"
  }
};
