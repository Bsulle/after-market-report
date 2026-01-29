import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TextInput,
  TouchableOpacity,
  Alert,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useWatchlist } from '../context/WatchlistContext';
import { useAuth } from '../context/AuthContext';
import { getConvictionEmoji } from '../services/api';

export default function WatchlistScreen({ navigation }: any) {
  const { watchlist, addTicker, removeTicker, canAddMore, watchlistLimit, loading } = useWatchlist();
  const { profile } = useAuth();
  const [newTicker, setNewTicker] = useState('');
  const [adding, setAdding] = useState(false);

  const isPro = profile?.tier === 'PRO';

  const handleAddTicker = async () => {
    if (!newTicker.trim()) return;

    if (!canAddMore) {
      Alert.alert(
        'Watchlist Limit Reached',
        `Free tier allows ${watchlistLimit} tickers. Upgrade to Pro for up to 50 tickers!`,
        [
          { text: 'Maybe Later', style: 'cancel' },
          { text: 'Upgrade', onPress: () => navigation.navigate('Pricing') },
        ]
      );
      return;
    }

    setAdding(true);
    const success = await addTicker(newTicker);
    setAdding(false);

    if (success) {
      setNewTicker('');
    } else {
      Alert.alert('Error', 'Ticker already in watchlist or invalid');
    }
  };

  const handleRemoveTicker = (symbol: string) => {
    Alert.alert(
      'Remove Ticker',
      `Remove ${symbol} from your watchlist?`,
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Remove', style: 'destructive', onPress: () => removeTicker(symbol) },
      ]
    );
  };

  const renderTickerItem = ({ item }: { item: any }) => (
    <TouchableOpacity
      style={styles.tickerCard}
      onPress={() => navigation.navigate('TickerDetail', { ticker: item.symbol })}
    >
      <View style={styles.tickerMain}>
        <Text style={styles.tickerSymbol}>{item.symbol}</Text>
        {item.name && <Text style={styles.tickerName}>{item.name}</Text>}
      </View>

      {item.convictionScore && (
        <View style={styles.convictionBadge}>
          <Text style={styles.convictionEmoji}>
            {getConvictionEmoji(item.convictionScore)}
          </Text>
          <Text style={styles.convictionScore}>{item.convictionScore.toFixed(1)}</Text>
        </View>
      )}

      {item.price && (
        <View style={styles.priceInfo}>
          <Text style={styles.price}>${item.price.toFixed(2)}</Text>
          <Text
            style={[
              styles.change,
              { color: item.change >= 0 ? '#4CAF50' : '#F44336' },
            ]}
          >
            {item.change >= 0 ? '+' : ''}{item.changePercent?.toFixed(2)}%
          </Text>
        </View>
      )}

      <TouchableOpacity
        style={styles.removeButton}
        onPress={() => handleRemoveTicker(item.symbol)}
      >
        <Ionicons name="close-circle" size={24} color="#666" />
      </TouchableOpacity>
    </TouchableOpacity>
  );

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>Your Watchlist</Text>
        <Text style={styles.subtitle}>
          {watchlist.length}/{watchlistLimit} tickers
          {!isPro && ' • Upgrade for more'}
        </Text>
      </View>

      {/* Add Ticker Input */}
      <View style={styles.inputContainer}>
        <TextInput
          style={styles.input}
          placeholder="Enter ticker symbol (e.g., AAPL)"
          placeholderTextColor="#666"
          value={newTicker}
          onChangeText={setNewTicker}
          autoCapitalize="characters"
          autoCorrect={false}
          onSubmitEditing={handleAddTicker}
          returnKeyType="done"
        />
        <TouchableOpacity
          style={[styles.addButton, (!newTicker.trim() || adding) && styles.addButtonDisabled]}
          onPress={handleAddTicker}
          disabled={!newTicker.trim() || adding}
        >
          <Ionicons name="add" size={24} color="#fff" />
        </TouchableOpacity>
      </View>

      {/* Watchlist */}
      <FlatList
        data={watchlist}
        renderItem={renderTickerItem}
        keyExtractor={(item) => item.symbol}
        contentContainerStyle={styles.listContainer}
        ListEmptyComponent={
          <View style={styles.emptyState}>
            <Ionicons name="list-outline" size={64} color="#444" />
            <Text style={styles.emptyTitle}>No tickers yet</Text>
            <Text style={styles.emptyText}>
              Add stock symbols above to start tracking them
            </Text>
          </View>
        }
      />

      {/* Upgrade Banner */}
      {!isPro && watchlist.length >= 3 && (
        <TouchableOpacity
          style={styles.upgradeBanner}
          onPress={() => navigation.navigate('Pricing')}
        >
          <View style={styles.upgradeContent}>
            <Text style={styles.upgradeTitle}>Want more tickers?</Text>
            <Text style={styles.upgradeText}>
              Pro gives you 50 tickers + detailed analysis
            </Text>
          </View>
          <Ionicons name="chevron-forward" size={20} color="#FFD700" />
        </TouchableOpacity>
      )}
    </KeyboardAvoidingView>
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
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
  },
  subtitle: {
    fontSize: 14,
    color: '#888',
    marginTop: 4,
  },
  inputContainer: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    marginBottom: 16,
    gap: 10,
  },
  input: {
    flex: 1,
    backgroundColor: '#252540',
    borderRadius: 10,
    paddingHorizontal: 16,
    paddingVertical: 12,
    color: '#fff',
    fontSize: 16,
  },
  addButton: {
    backgroundColor: '#4CAF50',
    borderRadius: 10,
    width: 48,
    alignItems: 'center',
    justifyContent: 'center',
  },
  addButtonDisabled: {
    backgroundColor: '#333',
  },
  listContainer: {
    paddingHorizontal: 16,
    paddingBottom: 100,
  },
  tickerCard: {
    backgroundColor: '#252540',
    borderRadius: 12,
    padding: 16,
    marginBottom: 10,
    flexDirection: 'row',
    alignItems: 'center',
  },
  tickerMain: {
    flex: 1,
  },
  tickerSymbol: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
  },
  tickerName: {
    fontSize: 12,
    color: '#888',
    marginTop: 2,
  },
  convictionBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#1a1a2e',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 8,
    marginRight: 10,
    gap: 4,
  },
  convictionEmoji: {
    fontSize: 14,
  },
  convictionScore: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 14,
  },
  priceInfo: {
    alignItems: 'flex-end',
    marginRight: 10,
  },
  price: {
    color: '#fff',
    fontWeight: '600',
    fontSize: 16,
  },
  change: {
    fontSize: 13,
    marginTop: 2,
  },
  removeButton: {
    padding: 4,
  },
  emptyState: {
    alignItems: 'center',
    paddingTop: 60,
  },
  emptyTitle: {
    color: '#fff',
    fontSize: 20,
    fontWeight: 'bold',
    marginTop: 16,
  },
  emptyText: {
    color: '#666',
    fontSize: 14,
    marginTop: 8,
    textAlign: 'center',
  },
  upgradeBanner: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: '#2a2a45',
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    borderTopWidth: 1,
    borderTopColor: '#FFD70033',
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
  },
});
