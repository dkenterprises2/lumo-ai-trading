import PortfolioRiskDashboard from "@/components/risk/PortfolioRiskDashboard";

export const metadata = {
  title: "Portfolio Risk Intelligence | Lumo AI Trading Platform",
  description: "Portfolio Risk & Safety Engine — Dynamic risk limits, portfolio heat, drawdown protection, and circuit breakers.",
};

export default function RiskPage() {
  return (
    <main className="container mx-auto px-4 py-8 max-w-7xl">
      <PortfolioRiskDashboard />
    </main>
  );
}
