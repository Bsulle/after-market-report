// Pricing tiers for MyFolio
export const PRICING_TIERS = {
  FREE: {
    id: 'free',
    name: 'Free',
    price: 0,
    features: {
      maxWatchlistSize: 5,
      dailyReports: false,
      coachSummary: true,        // Basic coach summary
      detailedAnalysis: false,
      pivotLevels: false,
      convictionScores: false,
      marketRegime: true,        // Basic regime indicator
      pushNotifications: false,
      historicalReports: 0,
    },
    limits: {
      refreshesPerDay: 3,
      apiCallsPerDay: 10,
    },
  },

  PRO: {
    id: 'pro',
    name: 'Pro',
    price: 9.99,  // Monthly
    priceYearly: 79.99,  // ~33% discount
    features: {
      maxWatchlistSize: 50,
      dailyReports: true,        // Full after-market reports
      coachSummary: true,        // Detailed coach summary with actionables
      detailedAnalysis: true,    // Full ticker cards
      pivotLevels: true,         // Support/resistance levels
      convictionScores: true,    // Full conviction dashboard
      marketRegime: true,        // Detailed regime analysis
      pushNotifications: true,   // Alert on high-conviction setups
      historicalReports: 30,     // 30 days of reports
    },
    limits: {
      refreshesPerDay: -1,       // Unlimited
      apiCallsPerDay: -1,        // Unlimited
    },
  },
} as const;

export type PricingTier = keyof typeof PRICING_TIERS;

// Feature flags for checking access
export function canAccessFeature(
  tier: PricingTier,
  feature: keyof typeof PRICING_TIERS.FREE.features
): boolean {
  return PRICING_TIERS[tier].features[feature] !== false &&
         PRICING_TIERS[tier].features[feature] !== 0;
}

export function getWatchlistLimit(tier: PricingTier): number {
  return PRICING_TIERS[tier].features.maxWatchlistSize;
}
