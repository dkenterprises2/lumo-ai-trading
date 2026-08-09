"use client";

import React from "react";

export default function Testimonials() {
  const testimonials = [
    {
      quote: "Lumo's Smart Order Router reduced our average execution slippage by 14 basis points across our crypto fund portfolio.",
      author: "Chief Investment Officer",
      company: "Alpha Digital Capital"
    },
    {
      quote: "The Mean-Variance portfolio optimizer and Kelly fractional sizing allowed us to scale from 2 to 14 active AI strategies effortlessly.",
      author: "Lead Quant Engineer",
      company: "Apex Quant Labs"
    },
    {
      quote: "The drift detection and shadow deployment engine gave us total confidence when deploying new XGBoost models to production.",
      author: "Head of ML Ops",
      company: "Sovereign Trading Tech"
    }
  ];

  return (
    <section className="py-20 bg-gray-950 border-b border-gray-800/60">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-4">
          <h2 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight">Trusted by Institutional Traders</h2>
          <p className="text-gray-400">Powering high-frequency and quantitative digital asset strategies.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {testimonials.map((t, idx) => (
            <div key={idx} className="bg-black/60 border border-gray-800 p-8 rounded-2xl flex flex-col justify-between">
              <p className="text-gray-300 text-sm italic leading-relaxed mb-6">"{t.quote}"</p>
              <div>
                <div className="font-bold text-white text-sm">{t.author}</div>
                <div className="text-xs text-indigo-400 mt-0.5">{t.company}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
