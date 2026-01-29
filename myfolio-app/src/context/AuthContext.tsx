import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import {
  User,
  onAuthStateChanged,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut as firebaseSignOut,
} from 'firebase/auth';
import { doc, getDoc, setDoc } from 'firebase/firestore';
import { auth, db } from '../config/firebase';
import { PricingTier, PRICING_TIERS } from '../config/pricing';

interface UserProfile {
  uid: string;
  email: string;
  displayName?: string;
  tier: PricingTier;
  watchlist: string[];
  createdAt: Date;
}

interface AuthContextType {
  user: User | null;
  profile: UserProfile | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
  updateTier: (tier: PricingTier) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      setUser(firebaseUser);

      if (firebaseUser) {
        // Fetch user profile from Firestore
        const profileDoc = await getDoc(doc(db, 'users', firebaseUser.uid));
        if (profileDoc.exists()) {
          setProfile(profileDoc.data() as UserProfile);
        }
      } else {
        setProfile(null);
      }

      setLoading(false);
    });

    return unsubscribe;
  }, []);

  const signIn = async (email: string, password: string) => {
    await signInWithEmailAndPassword(auth, email, password);
  };

  const signUp = async (email: string, password: string) => {
    const { user: newUser } = await createUserWithEmailAndPassword(auth, email, password);

    // Create user profile in Firestore
    const newProfile: UserProfile = {
      uid: newUser.uid,
      email: newUser.email!,
      tier: 'FREE',
      watchlist: [],
      createdAt: new Date(),
    };

    await setDoc(doc(db, 'users', newUser.uid), newProfile);
    setProfile(newProfile);
  };

  const signOut = async () => {
    await firebaseSignOut(auth);
    setProfile(null);
  };

  const updateTier = async (tier: PricingTier) => {
    if (!user || !profile) return;

    await setDoc(doc(db, 'users', user.uid), { ...profile, tier }, { merge: true });
    setProfile({ ...profile, tier });
  };

  return (
    <AuthContext.Provider value={{ user, profile, loading, signIn, signUp, signOut, updateTier }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
