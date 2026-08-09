import React from "react";
import Navbar from "../../components/landing/Navbar";
import Footer from "../../components/landing/Footer";

export const metadata = {
  title: "Contact Us — Lumo AI Trading Platform",
  description: "Get in touch with the Lumo AI quantitative engineering and enterprise sales teams."
};

export default function ContactPage() {
  return (
    <div className="min-h-screen bg-black text-white">
      <Navbar />
      <div className="py-20 max-w-3xl mx-auto px-6 space-y-8">
        <h1 className="text-4xl font-extrabold text-center">Contact Enterprise Sales & Support</h1>
        <p className="text-gray-400 text-center">Speak with our quantitative engineers about enterprise K8s deployment and custom SLAs.</p>

        <form className="bg-gray-950 border border-gray-800 p-8 rounded-2xl space-y-4">
          <div>
            <label className="block text-xs font-semibold text-gray-300 mb-1">Full Name</label>
            <input type="text" placeholder="John Doe" className="w-full bg-black border border-gray-800 rounded-lg p-3 text-sm text-white focus:outline-none focus:border-indigo-500" />
          </div>
          <div>
            <label className="block text-xs font-semibold text-gray-300 mb-1">Work Email</label>
            <input type="email" placeholder="john@fund.com" className="w-full bg-black border border-gray-800 rounded-lg p-3 text-sm text-white focus:outline-none focus:border-indigo-500" />
          </div>
          <div>
            <label className="block text-xs font-semibold text-gray-300 mb-1">Message</label>
            <textarea rows={4} placeholder="Describe your fund requirements..." className="w-full bg-black border border-gray-800 rounded-lg p-3 text-sm text-white focus:outline-none focus:border-indigo-500"></textarea>
          </div>
          <button type="button" className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-3 rounded-lg text-sm transition-colors">
            Send Inquiry
          </button>
        </form>
      </div>
      <Footer />
    </div>
  );
}
