"use client";

import React from "react";
import Link from "next/link";

export default function Navbar() {
  return (
    <header className="sticky top-0 z-50 backdrop-blur-md bg-black/70 border-b border-gray-800/80">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center font-bold text-white text-lg">
            L
          </div>
          <span className="font-bold text-white text-xl tracking-tight">Lumo <span className="text-indigo-400">AI</span></span>
        </Link>

        <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-gray-300">
          <Link href="/features" className="hover:text-white transition-colors">Features</Link>
          <Link href="/pricing" className="hover:text-white transition-colors">Pricing</Link>
          <Link href="/security" className="hover:text-white transition-colors">Security</Link>
          <Link href="/docs" className="hover:text-white transition-colors">Docs</Link>
          <Link href="/demo" className="hover:text-white transition-colors">Demo</Link>
          <Link href="/about" className="hover:text-white transition-colors">About</Link>
          <Link href="/contact" className="hover:text-white transition-colors">Contact</Link>
        </nav>

        <div className="flex items-center gap-4">
          <Link href="/login" className="text-sm font-medium text-gray-300 hover:text-white transition-colors">
            Sign In
          </Link>
          <Link href="/register" className="bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold px-4 py-2 rounded-lg transition-colors shadow-lg shadow-indigo-600/30">
            Start Free
          </Link>
        </div>
      </div>
    </header>
  );
}
