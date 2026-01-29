import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../context/AuthContext';
import { PRICING_TIERS } from '../config/pricing';

export default function PricingScreen({ navigation }: any) {
  const { profile, updateTier } = useAuth();
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('monthly');
  const [loading, setLoading] = useState(false);

  const currentTier = profile?.tier || 'FREE';

  const handleSubscribe = async () => {
    if (currentTier === 'PRO') {
      Alert.alert('Already Subscribed', 'You already have a Pro subscription!');
      return;
    }

    setLoading(true);

    // TODO: Integrate with actual payment provider (Stripe, RevenueCat, etc.)
    Alert.alert(
      'Subscribe to Pro',
      `This would redirect to payment for $${billingCycle === 'monthly' ? PRICING_TIERS.PRO.price : PRICING_TIERS.PRO.priceYearly}/${billingCycle === 'monthly' ? 'month' : 'year'}`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Simulate Subscribe',
          onPress: async () => {
            await updateTier('PRO');
            Alert.alert('Success!', 'Welcome to MyFolio Pro!');
            navigation.goBack();
          },
        },
      ]
    );

    setLoading(false);
  };

  const features = [
    {
      icon: 'list',
      title: 'Watchlist Size',
      free: '5 tickers',
      pro: '50 tickers',
    },
    {
      icon: 'document-text',
      title: 'Daily Reports',
      free: false,
      pro: true,
    },
    {
      icon: 'school',
      title: 'Coach Summary',
      free: 'Basic',
      pro: 'Detailed + Actions',
    },
    {
      icon: 'analytics',
      title: 'Conviction Scores',
      free: false,
      pro: true,
    },
    {
      icon: 'git-network',
      title: 'Pivot Levels',
      free: false,
      pro: true,
    },
    {
      icon: 'pulse',
      title: 'Market Regime',
      free: 'Basic',
      pro: 'Full Analysis',
    },
    {
      icon: 'notifications',
      title: 'Push Notifications',
      free: false,
      pro: true,
    },
    {
      icon: 'time',
      title: 'Historical Reports',
      free: 'None',
      pro: '30 days',
    },
  ];

  return (
    <ScrollView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity
          style={styles.closeButton}
          onPress={() => navigation.goBack()}
        >
          <Ionicons name="close" size={28} color="#fff" />
        </TouchableOpacity>
        <Text style={styles.title}>Upgrade to Pro</Text>
        <Text style={styles.subtitle}>Unlock the full power of your trading coach</Text>
      </View>

      {/* Billing Toggle */}
      <View style={styles.billingToggle}>
        <TouchableOpacity
          style={[styles.billingOption, billingCycle === 'monthly' && styles.billingActive]}
          onPress={() => setBillingCycle('monthly')}
        >
          <Text style={[styles.billingText, billingCycle === 'monthly' && styles.billingTextActive]}>
            Monthly
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.billingOption, billingCycle === 'yearly' && styles.billingActive]}
          onPress={() => setBillingCycle('yearly')}
        >
          <Text style={[styles.billingText, billingCycle === 'yearly' && styles.billingTextActive]}>
            Yearly
          </Text>
          <View style={styles.saveBadge}>
            <Text style={styles.saveText}>Save 33%</Text>
          </View>
        </TouchableOpacity>
      </View>

      {/* Price Display */}
      <View style={styles.priceContainer}>
        <Text style={styles.currency}>$</Text>
        <Text style={styles.price}>
          {billingCycle === 'monthly' ? PRICING_TIERS.PRO.price : PRICING_TIERS.PRO.priceYearly}
        </Text>
        <Text style={styles.period}>/{billingCycle === 'monthly' ? 'mo' : 'yr'}</Text>
      </View>

      {billingCycle === 'yearly' && (
        <Text style={styles.yearlyNote}>
          Just ${(PRICING_TIERS.PRO.priceYearly / 12).toFixed(2)}/month
        </Text>
      )}

      {/* Feature Comparison */}
      <View style={styles.featuresContainer}>
        <View style={styles.featureHeader}>
          <Text style={styles.featureHeaderText}>Feature</Text>
          <Text style={styles.featureHeaderFree}>Free</Text>
          <Text style={styles.featureHeaderPro}>Pro</Text>
        </View>

        {features.map((feature, index) => (
          <View key={index} style={styles.featureRow}>
            <View style={styles.featureInfo}>
              <Ionicons name={feature.icon as any} size={18} color="#888" />
              <Text style={styles.featureTitle}>{feature.title}</Text>
            </View>
            <View style={styles.featureFree}>
              {typeof feature.free === 'boolean' ? (
                <Ionicons
                  name={feature.free ? 'checkmark-circle' : 'close-circle'}
                  size={20}
                  color={feature.free ? '#4CAF50' : '#666'}
                />
              ) : (
                <Text style={styles.featureValue}>{feature.free}</Text>
              )}
            </View>
            <View style={styles.featurePro}>
              {typeof feature.pro === 'boolean' ? (
                <Ionicons
                  name={feature.pro ? 'checkmark-circle' : 'close-circle'}
                  size={20}
                  color={feature.pro ? '#4CAF50' : '#666'}
                />
              ) : (
                <Text style={styles.featureValuePro}>{feature.pro}</Text>
              )}
            </View>
          </View>
        ))}
      </View>

      {/* Subscribe Button */}
      <TouchableOpacity
        style={[styles.subscribeButton, currentTier === 'PRO' && styles.subscribedButton]}
        onPress={handleSubscribe}
        disabled={loading || currentTier === 'PRO'}
      >
        {currentTier === 'PRO' ? (
          <>
            <Ionicons name="checkmark-circle" size={24} color="#fff" />
            <Text style={styles.subscribeText}>Currently Subscribed</Text>
          </>
        ) : (
          <>
            <Ionicons name="rocket" size={24} color="#1a1a2e" />
            <Text style={[styles.subscribeText, { color: '#1a1a2e' }]}>
              {loading ? 'Processing...' : 'Subscribe to Pro'}
            </Text>
          </>
        )}
      </TouchableOpacity>

      {/* Terms */}
      <Text style={styles.terms}>
        Cancel anytime. Subscription auto-renews unless cancelled at least 24 hours before the end of the current period.
      </Text>

      {/* Testimonials */}
      <View style={styles.testimonialContainer}>
        <Text style={styles.testimonialTitle}>What traders are saying</Text>

        <View style={styles.testimonial}>
          <Text style={styles.testimonialText}>
            "The daily coach summaries have completely changed how I approach my watchlist. Worth every penny."
          </Text>
          <Text style={styles.testimonialAuthor}>— @SwingTrader_Mike</Text>
        </View>

        <View style={styles.testimonial}>
          <Text style={styles.testimonialText}>
            "Finally, an app that gives me actionable insights instead of just raw data."
          </Text>
          <Text style={styles.testimonialAuthor}>— @TechStockJenny</Text>
        </View>
      </View>

      <View style={styles.footer} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a2e',
  },
  header: {
    padding: 20,
    paddingTop: 60,
    alignItems: 'center',
  },
  closeButton: {
    position: 'absolute',
    top: 50,
    right: 20,
    zIndex: 10,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#888',
    textAlign: 'center',
  },
  billingToggle: {
    flexDirection: 'row',
    marginHorizontal: 20,
    backgroundColor: '#252540',
    borderRadius: 12,
    padding: 4,
    marginTop: 20,
  },
  billingOption: {
    flex: 1,
    paddingVertical: 12,
    alignItems: 'center',
    borderRadius: 10,
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 6,
  },
  billingActive: {
    backgroundColor: '#3a3a5c',
  },
  billingText: {
    color: '#888',
    fontWeight: '600',
  },
  billingTextActive: {
    color: '#fff',
  },
  saveBadge: {
    backgroundColor: '#4CAF50',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
  },
  saveText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: 'bold',
  },
  priceContainer: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    justifyContent: 'center',
    marginTop: 30,
  },
  currency: {
    color: '#FFD700',
    fontSize: 24,
    fontWeight: 'bold',
    marginTop: 8,
  },
  price: {
    color: '#FFD700',
    fontSize: 56,
    fontWeight: 'bold',
  },
  period: {
    color: '#888',
    fontSize: 18,
    marginTop: 36,
  },
  yearlyNote: {
    color: '#4CAF50',
    textAlign: 'center',
    marginTop: 4,
  },
  featuresContainer: {
    margin: 20,
    backgroundColor: '#252540',
    borderRadius: 12,
    overflow: 'hidden',
  },
  featureHeader: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#1f1f35',
  },
  featureHeaderText: {
    flex: 2,
    color: '#888',
    fontSize: 12,
    fontWeight: '600',
  },
  featureHeaderFree: {
    flex: 1,
    color: '#888',
    fontSize: 12,
    fontWeight: '600',
    textAlign: 'center',
  },
  featureHeaderPro: {
    flex: 1,
    color: '#FFD700',
    fontSize: 12,
    fontWeight: '600',
    textAlign: 'center',
  },
  featureRow: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    paddingVertical: 14,
    borderBottomWidth: 1,
    borderBottomColor: '#1f1f35',
    alignItems: 'center',
  },
  featureInfo: {
    flex: 2,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  featureTitle: {
    color: '#fff',
    fontSize: 14,
  },
  featureFree: {
    flex: 1,
    alignItems: 'center',
  },
  featurePro: {
    flex: 1,
    alignItems: 'center',
  },
  featureValue: {
    color: '#888',
    fontSize: 12,
  },
  featureValuePro: {
    color: '#4CAF50',
    fontSize: 12,
    fontWeight: '600',
  },
  subscribeButton: {
    backgroundColor: '#FFD700',
    marginHorizontal: 20,
    marginTop: 20,
    paddingVertical: 16,
    borderRadius: 12,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 10,
  },
  subscribedButton: {
    backgroundColor: '#4CAF50',
  },
  subscribeText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
  },
  terms: {
    color: '#666',
    fontSize: 11,
    textAlign: 'center',
    marginHorizontal: 40,
    marginTop: 16,
    lineHeight: 16,
  },
  testimonialContainer: {
    padding: 20,
    marginTop: 20,
  },
  testimonialTitle: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  testimonial: {
    backgroundColor: '#252540',
    padding: 16,
    borderRadius: 10,
    marginBottom: 12,
  },
  testimonialText: {
    color: '#ccc',
    fontSize: 14,
    fontStyle: 'italic',
    lineHeight: 20,
  },
  testimonialAuthor: {
    color: '#888',
    fontSize: 12,
    marginTop: 8,
  },
  footer: {
    height: 40,
  },
});
