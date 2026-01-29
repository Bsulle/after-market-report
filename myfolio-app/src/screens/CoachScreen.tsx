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
import { CoachSummary, mockCoachSummary, getConvictionEmoji } from '../services/api';

export default function CoachScreen({ navigation }: any) {
  const { profile } = useAuth();
  const { watchlist } = useWatchlist();
  const [summary, setSummary] = useState<CoachSummary | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['regime', 'picks']));

  const isPro = profile?.tier === 'PRO';

  useEffect(() => {
    loadSummary();
  }, [watchlist]);

  const loadSummary = async () => {
    // TODO: Replace with actual API call
    setSummary(mockCoachSummary);
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadSummary();
    setRefreshing(false);
  };

  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(section)) {
      newExpanded.delete(section);
    } else {
      newExpanded.add(section);
    }
    setExpandedSections(newExpanded);
  };

  const getRegimeIcon = (regime: string) => {
    switch (regime) {
      case 'Risk-On':
        return 'trending-up';
      case 'Risk-Off':
        return 'trending-down';
      default:
        return 'swap-horizontal';
    }
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

  if (!summary) {
    return (
      <View style={styles.loadingContainer}>
        <Text style={styles.loadingText}>Loading coach analysis...</Text>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>Coach Summary</Text>
        <Text style={styles.date}>
          {new Date(summary.generatedAt).toLocaleDateString('en-US', {
            weekday: 'long',
            month: 'long',
            day: 'numeric',
          })}
        </Text>
      </View>

      {/* Market Regime Section */}
      <TouchableOpacity
        style={styles.sectionHeader}
        onPress={() => toggleSection('regime')}
      >
        <View style={styles.sectionTitleRow}>
          <Ionicons
            name={getRegimeIcon(summary.marketRegime) as any}
            size={24}
            color={getRegimeColor(summary.marketRegime)}
          />
          <Text style={styles.sectionTitle}>Market Regime</Text>
        </View>
        <Ionicons
          name={expandedSections.has('regime') ? 'chevron-up' : 'chevron-down'}
          size={20}
          color="#666"
        />
      </TouchableOpacity>

      {expandedSections.has('regime') && (
        <View style={styles.sectionContent}>
          <View style={styles.regimeDisplay}>
            <View
              style={[styles.regimeBadge, { backgroundColor: getRegimeColor(summary.marketRegime) }]}
            >
              <Text style={styles.regimeText}>{summary.marketRegime}</Text>
            </View>
            <View style={styles.scoreContainer}>
              <Text style={styles.scoreLabel}>Confidence</Text>
              <Text style={styles.scoreValue}>{summary.regimeScore}/10</Text>
            </View>
          </View>
          <Text style={styles.headline}>{summary.headline}</Text>
        </View>
      )}

      {/* Key Insights Section */}
      <TouchableOpacity
        style={styles.sectionHeader}
        onPress={() => toggleSection('insights')}
      >
        <View style={styles.sectionTitleRow}>
          <Ionicons name="bulb-outline" size={24} color="#FFD700" />
          <Text style={styles.sectionTitle}>Key Insights</Text>
        </View>
        <Ionicons
          name={expandedSections.has('insights') ? 'chevron-up' : 'chevron-down'}
          size={20}
          color="#666"
        />
      </TouchableOpacity>

      {expandedSections.has('insights') && (
        <View style={styles.sectionContent}>
          {summary.keyInsights.map((insight, index) => (
            <View key={index} style={styles.insightItem}>
              <View style={styles.bulletPoint} />
              <Text style={styles.insightText}>{insight}</Text>
            </View>
          ))}
        </View>
      )}

      {/* Top Picks Section */}
      <TouchableOpacity
        style={styles.sectionHeader}
        onPress={() => toggleSection('picks')}
      >
        <View style={styles.sectionTitleRow}>
          <Ionicons name="trophy-outline" size={24} color="#4CAF50" />
          <Text style={styles.sectionTitle}>Top Conviction Picks</Text>
        </View>
        <Ionicons
          name={expandedSections.has('picks') ? 'chevron-up' : 'chevron-down'}
          size={20}
          color="#666"
        />
      </TouchableOpacity>

      {expandedSections.has('picks') && (
        <View style={styles.sectionContent}>
          {summary.topPicks.map((pick, index) => (
            <TouchableOpacity
              key={index}
              style={styles.pickCard}
              onPress={() => navigation.navigate('TickerDetail', { ticker: pick.symbol })}
            >
              <View style={styles.pickHeader}>
                <Text style={styles.pickRank}>#{index + 1}</Text>
                <Text style={styles.pickEmoji}>{pick.convictionEmoji}</Text>
                <Text style={styles.pickSymbol}>{pick.symbol}</Text>
                <View style={styles.scoreBadge}>
                  <Text style={styles.scoreText}>{pick.convictionScore.toFixed(1)}</Text>
                </View>
              </View>
              <Text style={styles.pickThesis}>{pick.thesis}</Text>
              <View style={styles.pickMeta}>
                <View style={[styles.riskBadge, styles[`risk${pick.riskLevel}`]]}>
                  <Text style={styles.riskText}>{pick.riskLevel} RISK</Text>
                </View>
                {isPro && pick.catalyst && (
                  <View style={styles.catalystInfo}>
                    <Ionicons name="calendar" size={12} color="#64B5F6" />
                    <Text style={styles.catalystText}>{pick.catalyst}</Text>
                  </View>
                )}
              </View>
            </TouchableOpacity>
          ))}
        </View>
      )}

      {/* Avoid List Section */}
      <TouchableOpacity
        style={styles.sectionHeader}
        onPress={() => toggleSection('avoid')}
      >
        <View style={styles.sectionTitleRow}>
          <Ionicons name="warning-outline" size={24} color="#F44336" />
          <Text style={styles.sectionTitle}>Avoid These</Text>
        </View>
        <Ionicons
          name={expandedSections.has('avoid') ? 'chevron-up' : 'chevron-down'}
          size={20}
          color="#666"
        />
      </TouchableOpacity>

      {expandedSections.has('avoid') && (
        <View style={styles.sectionContent}>
          <View style={styles.avoidList}>
            {summary.avoidList.map((ticker, index) => (
              <View key={index} style={styles.avoidChip}>
                <Text style={styles.avoidEmoji}>🚫</Text>
                <Text style={styles.avoidText}>{ticker}</Text>
              </View>
            ))}
          </View>
        </View>
      )}

      {/* Action Items Section (Pro only) */}
      {isPro && (
        <>
          <TouchableOpacity
            style={styles.sectionHeader}
            onPress={() => toggleSection('actions')}
          >
            <View style={styles.sectionTitleRow}>
              <Ionicons name="checkmark-done-outline" size={24} color="#64B5F6" />
              <Text style={styles.sectionTitle}>Action Items</Text>
              <View style={styles.proBadge}>
                <Text style={styles.proText}>PRO</Text>
              </View>
            </View>
            <Ionicons
              name={expandedSections.has('actions') ? 'chevron-up' : 'chevron-down'}
              size={20}
              color="#666"
            />
          </TouchableOpacity>

          {expandedSections.has('actions') && (
            <View style={styles.sectionContent}>
              {summary.actionItems.map((action, index) => (
                <View key={index} style={styles.actionItem}>
                  <Ionicons name="arrow-forward-circle" size={18} color="#4CAF50" />
                  <Text style={styles.actionText}>{action}</Text>
                </View>
              ))}
            </View>
          )}
        </>
      )}

      {/* Upgrade CTA for Free users */}
      {!isPro && (
        <TouchableOpacity
          style={styles.upgradeCard}
          onPress={() => navigation.navigate('Pricing')}
        >
          <View style={styles.upgradeIcon}>
            <Ionicons name="lock-closed" size={24} color="#FFD700" />
          </View>
          <View style={styles.upgradeContent}>
            <Text style={styles.upgradeTitle}>Unlock Full Coach Analysis</Text>
            <Text style={styles.upgradeText}>
              Get actionable trade ideas, pivot levels, and daily position sizing guidance
            </Text>
          </View>
        </TouchableOpacity>
      )}

      <View style={styles.footer} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a2e',
  },
  loadingContainer: {
    flex: 1,
    backgroundColor: '#1a1a2e',
    alignItems: 'center',
    justifyContent: 'center',
  },
  loadingText: {
    color: '#888',
    fontSize: 16,
  },
  header: {
    padding: 20,
    paddingTop: 60,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
  },
  date: {
    fontSize: 14,
    color: '#888',
    marginTop: 4,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 14,
    backgroundColor: '#252540',
    marginTop: 1,
  },
  sectionTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#fff',
  },
  sectionContent: {
    padding: 16,
    backgroundColor: '#1f1f35',
  },
  regimeDisplay: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  regimeBadge: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
  },
  regimeText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 16,
  },
  scoreContainer: {
    alignItems: 'flex-end',
  },
  scoreLabel: {
    color: '#888',
    fontSize: 12,
  },
  scoreValue: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  headline: {
    color: '#ccc',
    fontSize: 15,
    lineHeight: 22,
  },
  insightItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 12,
    gap: 10,
  },
  bulletPoint: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: '#FFD700',
    marginTop: 7,
  },
  insightText: {
    flex: 1,
    color: '#ccc',
    fontSize: 14,
    lineHeight: 20,
  },
  pickCard: {
    backgroundColor: '#252540',
    borderRadius: 12,
    padding: 14,
    marginBottom: 10,
  },
  pickHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 8,
  },
  pickRank: {
    color: '#888',
    fontSize: 12,
    fontWeight: 'bold',
  },
  pickEmoji: {
    fontSize: 18,
  },
  pickSymbol: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 18,
    flex: 1,
  },
  scoreBadge: {
    backgroundColor: '#4CAF5033',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  scoreText: {
    color: '#4CAF50',
    fontWeight: 'bold',
  },
  pickThesis: {
    color: '#aaa',
    fontSize: 13,
    lineHeight: 18,
    marginBottom: 10,
  },
  pickMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  riskBadge: {
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 4,
  },
  riskLOW: {
    backgroundColor: '#4CAF5033',
  },
  riskMEDIUM: {
    backgroundColor: '#FF980033',
  },
  riskHIGH: {
    backgroundColor: '#F4433633',
  },
  riskText: {
    fontSize: 10,
    fontWeight: 'bold',
    color: '#fff',
  },
  catalystInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  catalystText: {
    color: '#64B5F6',
    fontSize: 12,
  },
  avoidList: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
  },
  avoidChip: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F4433633',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 8,
    gap: 6,
  },
  avoidEmoji: {
    fontSize: 14,
  },
  avoidText: {
    color: '#F44336',
    fontWeight: 'bold',
  },
  proBadge: {
    backgroundColor: '#FFD70033',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 4,
    marginLeft: 8,
  },
  proText: {
    color: '#FFD700',
    fontSize: 10,
    fontWeight: 'bold',
  },
  actionItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 12,
    gap: 10,
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
    padding: 20,
    borderRadius: 12,
    flexDirection: 'row',
    gap: 14,
    borderWidth: 1,
    borderColor: '#FFD70044',
  },
  upgradeIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#FFD70022',
    alignItems: 'center',
    justifyContent: 'center',
  },
  upgradeContent: {
    flex: 1,
  },
  upgradeTitle: {
    color: '#FFD700',
    fontWeight: 'bold',
    fontSize: 16,
    marginBottom: 4,
  },
  upgradeText: {
    color: '#888',
    fontSize: 13,
    lineHeight: 18,
  },
  footer: {
    height: 40,
  },
});
