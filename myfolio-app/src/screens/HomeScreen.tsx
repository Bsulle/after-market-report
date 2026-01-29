import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  TouchableOpacity,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../context/AuthContext';
import { useWatchlist } from '../context/WatchlistContext';
import { CoachSummary, mockCoachSummary } from '../services/api';
import { PRICING_TIERS } from '../config/pricing';

export default function HomeScreen({ navigation }: any) {
  const { profile } = useAuth();
  const { watchlist } = useWatchlist();
  const [coachSummary, setCoachSummary] = useState<CoachSummary | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(true);

  const isPro = profile?.tier === 'PRO';

  useEffect(() => {
    loadCoachSummary();
  }, [watchlist]);

  const loadCoachSummary = async () => {
    setLoading(true);
    try {
      // TODO: Replace with actual API call
      // const summary = await apiClient.getCoachSummary(watchlist.map(t => t.symbol));
      setCoachSummary(mockCoachSummary);
    } catch (error) {
      console.error('Error loading coach summary:', error);
    }
    setLoading(false);
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadCoachSummary();
    setRefreshing(false);
  };

  const getRegimeColor = (regime: string) => {
    switch (regime) {
      case 'Risk-On':
        return '#4CAF50';
      case 'Risk-Off':
        return '#F44336';
      default:
        return '#FF9800';
    }
  };

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.greeting}>
          {profile?.displayName ? `Hey ${profile.displayName}` : 'Welcome back'}
        </Text>
        <Text style={styles.subtitle}>Here's your trading coach summary</Text>
      </View>

      {/* Market Regime Card */}
      {coachSummary && (
        <View style={styles.regimeCard}>
          <View style={styles.regimeHeader}>
            <View
              style={[styles.regimeBadge, { backgroundColor: getRegimeColor(coachSummary.marketRegime) }]}
            >
              <Text style={styles.regimeText}>{coachSummary.marketRegime}</Text>
            </View>
            <Text style={styles.regimeScore}>Score: {coachSummary.regimeScore}/10</Text>
          </View>
          <Text style={styles.headline}>{coachSummary.headline}</Text>
        </View>
      )}

      {/* Key Insights */}
      {coachSummary && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Key Insights</Text>
          {coachSummary.keyInsights.map((insight, index) => (
            <View key={index} style={styles.insightRow}>
              <Ionicons name="bulb-outline" size={16} color="#FFD700" />
              <Text style={styles.insightText}>{insight}</Text>
            </View>
          ))}
        </View>
      )}

      {/* Top Picks */}
      {coachSummary && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Top Conviction Picks</Text>
          {coachSummary.topPicks.map((pick, index) => (
            <TouchableOpacity
              key={index}
              style={styles.pickCard}
              onPress={() => navigation.navigate('TickerDetail', { ticker: pick.symbol })}
            >
              <View style={styles.pickHeader}>
                <Text style={styles.pickEmoji}>{pick.convictionEmoji}</Text>
                <Text style={styles.pickSymbol}>{pick.symbol}</Text>
                <Text style={styles.pickScore}>{pick.convictionScore.toFixed(1)}</Text>
              </View>
              <Text style={styles.pickThesis}>{pick.thesis}</Text>
              {isPro && pick.catalyst && (
                <View style={styles.catalystBadge}>
                  <Ionicons name="calendar-outline" size={12} color="#64B5F6" />
                  <Text style={styles.catalystText}>{pick.catalyst}</Text>
                </View>
              )}
            </TouchableOpacity>
          ))}
        </View>
      )}

      {/* Action Items (Pro only) */}
      {isPro && coachSummary && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Action Items</Text>
          {coachSummary.actionItems.map((action, index) => (
            <View key={index} style={styles.actionRow}>
              <Ionicons name="checkmark-circle-outline" size={16} color="#4CAF50" />
              <Text style={styles.actionText}>{action}</Text>
            </View>
          ))}
        </View>
      )}

      {/* Upgrade CTA for Free users */}
      {!isPro && (
        <TouchableOpacity
          style={styles.upgradeCard}
          onPress={() => navigation.navigate('Pricing')}
        >
          <Ionicons name="rocket-outline" size={24} color="#FFD700" />
          <View style={styles.upgradeContent}>
            <Text style={styles.upgradeTitle}>Unlock Full Analysis</Text>
            <Text style={styles.upgradeText}>
              Get pivot levels, detailed conviction scores, and daily reports
            </Text>
          </View>
          <Ionicons name="chevron-forward" size={20} color="#666" />
        </TouchableOpacity>
      )}

      {/* Watchlist Preview */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Your Watchlist</Text>
          <TouchableOpacity onPress={() => navigation.navigate('Watchlist')}>
            <Text style={styles.seeAll}>See all →</Text>
          </TouchableOpacity>
        </View>
        <View style={styles.watchlistPreview}>
          {watchlist.slice(0, 5).map((ticker, index) => (
            <View key={index} style={styles.tickerChip}>
              <Text style={styles.tickerChipText}>{ticker.symbol}</Text>
            </View>
          ))}
          {watchlist.length === 0 && (
            <TouchableOpacity
              style={styles.addTickerButton}
              onPress={() => navigation.navigate('Watchlist')}
            >
              <Ionicons name="add-circle-outline" size={20} color="#64B5F6" />
              <Text style={styles.addTickerText}>Add your first ticker</Text>
            </TouchableOpacity>
          )}
        </View>
      </View>

      <View style={styles.footer}>
        <Text style={styles.timestamp}>
          Last updated: {coachSummary?.generatedAt ? new Date(coachSummary.generatedAt).toLocaleString() : 'N/A'}
        </Text>
      </View>
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
  },
  greeting: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
  },
  subtitle: {
    fontSize: 16,
    color: '#888',
    marginTop: 4,
  },
  regimeCard: {
    backgroundColor: '#252540',
    margin: 16,
    padding: 16,
    borderRadius: 12,
  },
  regimeHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  regimeBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  regimeText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 14,
  },
  regimeScore: {
    color: '#888',
    fontSize: 14,
  },
  headline: {
    color: '#fff',
    fontSize: 16,
    lineHeight: 22,
  },
  section: {
    padding: 16,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 12,
  },
  seeAll: {
    color: '#64B5F6',
    fontSize: 14,
  },
  insightRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 10,
    gap: 8,
  },
  insightText: {
    flex: 1,
    color: '#ccc',
    fontSize: 14,
    lineHeight: 20,
  },
  pickCard: {
    backgroundColor: '#252540',
    padding: 14,
    borderRadius: 10,
    marginBottom: 10,
  },
  pickHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 8,
  },
  pickEmoji: {
    fontSize: 18,
  },
  pickSymbol: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 16,
    flex: 1,
  },
  pickScore: {
    color: '#4CAF50',
    fontWeight: 'bold',
    fontSize: 14,
  },
  pickThesis: {
    color: '#aaa',
    fontSize: 13,
    lineHeight: 18,
  },
  catalystBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    marginTop: 8,
    backgroundColor: '#1a1a2e',
    alignSelf: 'flex-start',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  catalystText: {
    color: '#64B5F6',
    fontSize: 12,
  },
  actionRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 10,
    gap: 8,
  },
  actionText: {
    flex: 1,
    color: '#ccc',
    fontSize: 14,
    lineHeight: 20,
  },
  upgradeCard: {
    backgroundColor: '#2a2a45',
    margin: 16,
    padding: 16,
    borderRadius: 12,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    borderWidth: 1,
    borderColor: '#FFD70033',
  },
  upgradeContent: {
    flex: 1,
  },
  upgradeTitle: {
    color: '#FFD700',
    fontWeight: 'bold',
    fontSize: 16,
  },
  upgradeText: {
    color: '#888',
    fontSize: 13,
    marginTop: 2,
  },
  watchlistPreview: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  tickerChip: {
    backgroundColor: '#252540',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 8,
  },
  tickerChipText: {
    color: '#fff',
    fontWeight: '500',
  },
  addTickerButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  addTickerText: {
    color: '#64B5F6',
    fontSize: 14,
  },
  footer: {
    padding: 16,
    alignItems: 'center',
  },
  timestamp: {
    color: '#555',
    fontSize: 12,
  },
});
