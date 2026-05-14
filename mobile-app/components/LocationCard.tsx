import React from 'react';
import { View, Text } from 'react-native';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { GlowingCard } from './ui/GlowingCard';

interface LocationCardProps {
  address?: string;
  latitude?: number;
  longitude?: number;
  isLoading?: boolean;
}

export function LocationCard({
  address,
  latitude,
  longitude,
  isLoading,
}: LocationCardProps) {
  return (
    <GlowingCard intensity="md" style={{ padding: 16 }}>
      <View style={{ flexDirection: 'row', alignItems: 'center', gap: 12 }}>
        <MaterialCommunityIcons
          name="map-marker"
          size={24}
          color="#00d9ff"
        />
        <View style={{ flex: 1 }}>
          {isLoading ? (
            <Text style={{ color: '#00d9ff', fontSize: 14 }}>Detecting location...</Text>
          ) : address ? (
            <View>
              <Text style={{ color: '#00d9ff', fontWeight: '600' }}>{address}</Text>
              <Text style={{ color: 'rgba(0, 217, 255, 0.6)', fontSize: 12 }}>
                {latitude?.toFixed(4)}, {longitude?.toFixed(4)}
              </Text>
            </View>
          ) : (
            <Text style={{ color: 'rgba(0, 217, 255, 0.6)' }}>No location detected</Text>
          )}
        </View>
      </View>
    </GlowingCard>
  );
}
