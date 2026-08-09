import React from "react";
import Navbar from "../../components/landing/Navbar";
import Footer from "../../components/landing/Footer";

export const metadata = {
  title: "About Us — Lumo AI Trading Platform",
  description: "Mission and vision behind the Lumo AI Quantitative Asset Management Platform."
};

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-black text-white">
      <Navbar />
      <div className="py-20 max-w-4xl mx-auto px-6 space-y-8">
        <h1 className="text-4xl font-extrabold">About Lumo AI</h1>
        <p className="text-gray-400 text-lg leading-relaxed">
          Lumo AI Trading Platform was built to bridge institutional quantitative finance with modern artificial intelligence. Our mission is to democratize high-frequency smart order routing, portfolio risk optimization, and continuous MLOps learning for asset managers and quantitative funds globally.
        </p>
      </div>
      <Footer />
    </div>
  );
}
