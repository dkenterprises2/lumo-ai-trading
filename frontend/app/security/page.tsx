import React from "react";
import Navbar from "../../components/landing/Navbar";
import SecuritySection from "../../components/landing/SecuritySection";
import Footer from "../../components/landing/Footer";

export const metadata = {
  title: "Security & Compliance — Lumo AI Trading Platform",
  description: "Bank-grade AES-256 encryption, multi-tenant isolation, and SOC 2 security compliance."
};

export default function SecurityPage() {
  return (
    <div className="min-h-screen bg-black text-white">
      <Navbar />
      <SecuritySection />
      <Footer />
    </div>
  );
}
