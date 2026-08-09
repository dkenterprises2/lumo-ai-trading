"use client";

import React from "react";
import Link from "next/link";

export default function Footer() {
  return (
    <footer className="bg-black py-12 border-t border-gray-900 text-gray-400 text-sm">
      <div className="max-w-7xl mx-auto px-6 grid grid-cols-1 md:grid-cols-4 gap-8 mb-12">
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded bg-indigo-600 flex items-center justify-center font-bold text-white text-xs">
              L
            </div>
            <span className="font-bold text-white text-lg tracking-tight">Lumo AI Trading</span>
          </div>
          <p className="text-xs text-gray-500 leading-relaxed">
            Autonomous Institutional Quantitative Trading Platform for Crypto & Digital Assets.
          </p>
        </div>

        <div>
          <h4 className="font-bold text-white text-xs uppercase tracking-wider mb-4">Product</h4>
          <ul className="space-y-2 text-xs">
            <li><Link href="/features" className="hover:text-white transition-colors">Features</Link></li>
            <li><Link href="/pricing" className="hover:text-white transition-colors">Pricing</Link></li>
            <li><Link href="/security" className="hover:text-white transition-colors">Security</Link></li>
            <li><Link href="/docs" className="hover:text-white transition-colors">Documentation</Link></li>
          </ul>
        </div>

        <div>
          <h4 className="font-bold text-white text-xs uppercase tracking-wider mb-4">Company</h4>
          <ul className="space-y-2 text-xs">
            <li><Link href="/about" className="hover:text-white transition-colors">About Us</Link></li>
            <li><Link href="/contact" className="hover:text-white transition-colors">Contact Support</Link></li>
            <li><Link href="/demo" className="hover:text-white transition-colors">Live Demo</Link></li>
          </ul>
        </div>

        <div>
          <h4 className="font-bold text-white text-xs uppercase tracking-wider mb-4">Legal</h4>
          <ul className="space-y-2 text-xs">
            <li><span className="hover:text-white cursor-pointer">Privacy Policy</span></li>
            <li><span className="hover:text-white cursor-pointer">Terms of Service</span></li>
            <li><span className="hover:text-white cursor-pointer">Security Compliance</span></li>
          </ul>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 border-t border-gray-900 pt-6 flex flex-col sm:flex-row items-center justify-between text-xs text-gray-600">
        <div>© 2026 Lumo AI Trading Platform v2.7. All rights reserved.</div>
        <div className="mt-2 sm:mt-0 font-mono">Built for Institutional Quantitative Excellence</div>
      </div>
    </footer>
  );
}
