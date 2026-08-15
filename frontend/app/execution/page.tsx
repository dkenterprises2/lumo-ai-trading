import ExecutionDashboard from "@/components/execution/ExecutionDashboard";

export const metadata = {
  title: "Execution Management System (EMS) | Lumo AI Trading Platform",
  description: "Institutional Order & Execution Engine — Smart order routing, algorithmic execution, slippage control, and execution telemetry.",
};

export default function ExecutionPage() {
  return (
    <main className="container mx-auto px-4 py-8 max-w-7xl">
      <ExecutionDashboard />
    </main>
  );
}
