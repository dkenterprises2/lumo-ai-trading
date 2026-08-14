import ExecutionDashboard from "@/components/execution/ExecutionDashboard";

export const metadata = {
  title: "Execution Management System (EMS) | Lumo AI Trading Platform",
  description: "Phase 35 Institutional OMS / EMS Execution Layer & Smart Order Routing",
};

export default function ExecutionPage() {
  return (
    <main className="container mx-auto px-4 py-8 max-w-7xl">
      <ExecutionDashboard />
    </main>
  );
}
