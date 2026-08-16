'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';

export interface CurrencyConfig {
  code: string;
  name: string;
  symbol: string;
  rate: number; // Conversion rate relative to 1 USD
  flag: string;
  locale: string;
}

export const SUPPORTED_CURRENCIES: CurrencyConfig[] = [
  { code: 'USD', name: 'US Dollar', symbol: '$', rate: 1.0, flag: '🇺🇸', locale: 'en-US' },
  { code: 'INR', name: 'Indian Rupee', symbol: '₹', rate: 87.50, flag: '🇮🇳', locale: 'en-IN' },
  { code: 'EUR', name: 'Euro', symbol: '€', rate: 0.92, flag: '🇪🇺', locale: 'de-DE' },
  { code: 'GBP', name: 'British Pound', symbol: '£', rate: 0.78, flag: '🇬🇧', locale: 'en-GB' },
  { code: 'AED', name: 'UAE Dirham', symbol: 'د.إ', rate: 3.67, flag: '🇦🇪', locale: 'en-AE' },
  { code: 'CAD', name: 'Canadian Dollar', symbol: 'CA$', rate: 1.38, flag: '🇨🇦', locale: 'en-CA' },
  { code: 'AUD', name: 'Australian Dollar', symbol: 'A$', rate: 1.54, flag: '🇦🇺', locale: 'en-AU' },
  { code: 'JPY', name: 'Japanese Yen', symbol: '¥', rate: 155.0, flag: '🇯🇵', locale: 'ja-JP' },
  { code: 'SGD', name: 'Singapore Dollar', symbol: 'S$', rate: 1.35, flag: '🇸🇬', locale: 'en-SG' },
  { code: 'CHF', name: 'Swiss Franc', symbol: 'CHF', rate: 0.89, flag: '🇨🇭', locale: 'de-CH' },
  { code: 'CNY', name: 'Chinese Yuan', symbol: '¥', rate: 7.24, flag: '🇨🇳', locale: 'zh-CN' },
  { code: 'RUB', name: 'Russian Ruble', symbol: '₽', rate: 92.0, flag: '🇷🇺', locale: 'ru-RU' },
  { code: 'BRL', name: 'Brazilian Real', symbol: 'R$', rate: 5.40, flag: '🇧🇷', locale: 'pt-BR' },
  { code: 'KRW', name: 'South Korean Won', symbol: '₩', rate: 1380.0, flag: '🇰🇷', locale: 'ko-KR' },
];

interface CurrencyContextType {
  currency: string;
  currentCurrency: CurrencyConfig;
  setCurrency: (code: string) => void;
  formatCurrency: (usdAmount: number, options?: { decimals?: number; showSymbol?: boolean; showCode?: boolean }) => string;
  convertFromUSD: (usdAmount: number) => number;
  convertToUSD: (targetAmount: number) => number;
  currencies: CurrencyConfig[];
}

const CurrencyContext = createContext<CurrencyContextType | undefined>(undefined);

export const CurrencyProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currencyCode, setCurrencyCode] = useState<string>('USD');

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('lumo_preferred_currency');
      if (stored && SUPPORTED_CURRENCIES.some(c => c.code === stored.toUpperCase())) {
        setCurrencyCode(stored.toUpperCase());
      } else {
        // Check if user object has currency
        try {
          const userStr = localStorage.getItem('lumo_user_data');
          if (userStr) {
            const parsed = JSON.parse(userStr);
            if (parsed.currency && SUPPORTED_CURRENCIES.some(c => c.code === parsed.currency.toUpperCase())) {
              setCurrencyCode(parsed.currency.toUpperCase());
            }
          }
        } catch (e) {
          // ignore
        }
      }
    }
  }, []);

  const handleSetCurrency = (code: string) => {
    const upper = (code || 'USD').toUpperCase();
    if (SUPPORTED_CURRENCIES.some(c => c.code === upper)) {
      setCurrencyCode(upper);
      if (typeof window !== 'undefined') {
        localStorage.setItem('lumo_preferred_currency', upper);
      }
    }
  };

  const currentCurrency = SUPPORTED_CURRENCIES.find(c => c.code === currencyCode) || SUPPORTED_CURRENCIES[0];

  const convertFromUSD = (usdAmount: number): number => {
    if (typeof usdAmount !== 'number' || isNaN(usdAmount)) return 0;
    return usdAmount * currentCurrency.rate;
  };

  const convertToUSD = (targetAmount: number): number => {
    if (typeof targetAmount !== 'number' || isNaN(targetAmount)) return 0;
    return targetAmount / currentCurrency.rate;
  };

  const formatCurrency = (
    usdAmount: number,
    options?: { decimals?: number; showSymbol?: boolean; showCode?: boolean }
  ): string => {
    if (typeof usdAmount !== 'number' || isNaN(usdAmount)) {
      return `${options?.showSymbol !== false ? currentCurrency.symbol : ''}0.00`;
    }

    const converted = convertFromUSD(usdAmount);
    const isNegative = converted < 0;
    const absVal = Math.abs(converted);

    const decimals = options?.decimals !== undefined
      ? options.decimals
      : absVal >= 1000 ? 2 : absVal >= 1 ? 2 : 4;

    const formattedNum = absVal.toLocaleString(currentCurrency.locale, {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    });

    const prefix = isNegative ? '-' : '';
    const symbolStr = options?.showSymbol !== false ? `${currentCurrency.symbol} ` : '';
    const codeStr = options?.showCode ? ` ${currentCurrency.code}` : '';

    return `${prefix}${symbolStr}${formattedNum}${codeStr}`;
  };

  return (
    <CurrencyContext.Provider
      value={{
        currency: currencyCode,
        currentCurrency,
        setCurrency: handleSetCurrency,
        formatCurrency,
        convertFromUSD,
        convertToUSD,
        currencies: SUPPORTED_CURRENCIES,
      }}
    >
      {children}
    </CurrencyContext.Provider>
  );
};

export const useCurrency = () => {
  const context = useContext(CurrencyContext);
  if (!context) {
    throw new Error('useCurrency must be used within a CurrencyProvider');
  }
  return context;
};
