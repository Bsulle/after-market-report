import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { NavigationContainer, DefaultTheme } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createStackNavigator } from '@react-navigation/stack';
import { Ionicons } from '@expo/vector-icons';

import { AuthProvider } from './src/context/AuthContext';
import { WatchlistProvider } from './src/context/WatchlistContext';

import HomeScreen from './src/screens/HomeScreen';
import WatchlistScreen from './src/screens/WatchlistScreen';
import CoachScreen from './src/screens/CoachScreen';
import PricingScreen from './src/screens/PricingScreen';

// Dark theme for navigation
const DarkTheme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    primary: '#64B5F6',
    background: '#1a1a2e',
    card: '#252540',
    text: '#ffffff',
    border: '#333355',
    notification: '#FFD700',
  },
};

const Tab = createBottomTabNavigator();
const Stack = createStackNavigator();

function TabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: keyof typeof Ionicons.glyphMap;

          if (route.name === 'Home') {
            iconName = focused ? 'home' : 'home-outline';
          } else if (route.name === 'Watchlist') {
            iconName = focused ? 'list' : 'list-outline';
          } else if (route.name === 'Coach') {
            iconName = focused ? 'school' : 'school-outline';
          } else if (route.name === 'Settings') {
            iconName = focused ? 'settings' : 'settings-outline';
          } else {
            iconName = 'help-circle-outline';
          }

          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#FFD700',
        tabBarInactiveTintColor: '#888',
        tabBarStyle: {
          backgroundColor: '#252540',
          borderTopColor: '#333355',
          paddingBottom: 8,
          paddingTop: 8,
          height: 60,
        },
        headerShown: false,
      })}
    >
      <Tab.Screen name="Home" component={HomeScreen} />
      <Tab.Screen name="Watchlist" component={WatchlistScreen} />
      <Tab.Screen name="Coach" component={CoachScreen} />
    </Tab.Navigator>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <WatchlistProvider>
        <NavigationContainer theme={DarkTheme}>
          <StatusBar style="light" />
          <Stack.Navigator screenOptions={{ headerShown: false }}>
            <Stack.Screen name="Main" component={TabNavigator} />
            <Stack.Screen
              name="Pricing"
              component={PricingScreen}
              options={{ presentation: 'modal' }}
            />
            <Stack.Screen
              name="TickerDetail"
              component={TickerDetailPlaceholder}
              options={{ headerShown: true, headerTitle: 'Ticker Details' }}
            />
          </Stack.Navigator>
        </NavigationContainer>
      </WatchlistProvider>
    </AuthProvider>
  );
}

// Placeholder for ticker detail screen
function TickerDetailPlaceholder({ route }: any) {
  const { ticker } = route.params || {};
  return (
    <React.Fragment>
      <StatusBar style="light" />
      {/* TODO: Implement full ticker detail screen */}
    </React.Fragment>
  );
}
