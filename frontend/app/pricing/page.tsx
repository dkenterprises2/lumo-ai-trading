import React from "react";
import Navbar from "../../components/landing/Navbar";
import PricingCards from "../../components/landing/PricingCards";
import FaqSection from "../../components/landing/FaqSection";
import Footer from "../../components/landing/Footer";

export const metadata = {
  title: "Pricing Plans — Lumo AI Trading Platform",
  description: "Subscription pricing tiers for traders, funds, and institutional quantitative managers."
};

export default function PricingPage() {
  return (
    <div className="min-h-screen bg-black text-white">
      <Navbar />
      <PricingCards />
      <FaqSection />
      <Footer />
    </div>
  );
}
