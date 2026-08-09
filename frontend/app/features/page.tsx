import React from "react";
import Navbar from "../../components/landing/Navbar";
import FeatureGrid from "../../components/landing/FeatureGrid";
import Footer from "../../components/landing/Footer";

export const metadata = {
  title: "Platform Features — Lumo AI Trading Platform",
  description: "Explore Lumo's AI Signal Engine, Portfolio Optimizer, Smart Order Router, and MLOps Infrastructure."
};

export default function FeaturesPage() {
  return (
    <div className="min-h-screen bg-black text-white">
      <Navbar />
      <div className="py-16 text-center max-w-4xl mx-auto px-6">
        <h1 className="text-4xl font-extrabold mb-4">Enterprise Features</h1>
        <p className="text-gray-400">Deep dive into Lumo's quantitative AI technology stack.</p>
      </div>
      <FeatureGrid />
      <Footer />
    </div>
  );
}
