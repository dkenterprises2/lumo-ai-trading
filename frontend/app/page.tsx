import React from "react";
import Metadata from "next";
import Navbar from "../components/landing/Navbar";
import Hero from "../components/landing/Hero";
import FeatureGrid from "../components/landing/FeatureGrid";
import HowItWorks from "../components/landing/HowItWorks";
import TradingShowcase from "../components/landing/TradingShowcase";
import PricingCards from "../components/landing/PricingCards";
import SecuritySection from "../components/landing/SecuritySection";
import Testimonials from "../components/landing/Testimonials";
import FaqSection from "../components/landing/FaqSection";
import Footer from "../components/landing/Footer";

export const metadata = {
  title: "Lumo AI Trading Platform — Autonomous Institutional Quantitative Trading",
  description: "Autonomous Institutional Quantitative Trading for Crypto & Digital Assets. AI Signal Engine, Smart Order Router, Portfolio Optimizer, and Risk Controls.",
  openGraph: {
    title: "Lumo AI Trading Platform",
    description: "Autonomous Institutional Quantitative Trading for Crypto & Digital Assets.",
    url: "https://lumo.trade",
    type: "website"
  }
};

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-black text-white selection:bg-indigo-600 selection:text-white">
      <Navbar />
      <main>
        <Hero />
        <FeatureGrid />
        <HowItWorks />
        <TradingShowcase />
        <PricingCards />
        <SecuritySection />
        <Testimonials />
        <FaqSection />
      </main>
      <Footer />
    </div>
  );
}
