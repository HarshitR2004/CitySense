import React from 'react';
import { View, Text, ScrollView } from 'react-native';
import { SuccessIcon } from '../components/SuccessIcon';
import { GlowingButton } from '../components/ui/GlowingButton';
import { GlowingCard } from '../components/ui/GlowingCard';

export function SuccessScreen({ route, navigation }: any) {
  const { trackingId } = route.params;

  const handleReturnHome = () => {
    navigation.reset({
      index: 0,
      routes: [{ name: 'Home' }],
    });
  };

  return (
    <ScrollView style={{ flex: 1, backgroundColor: '#09090b' }}>
      <View style={{ flex: 1, minHeight: '100%', paddingHorizontal: 24, paddingVertical: 64, alignItems: 'center', justifyContent: 'center', gap: 32 }}>
        
        {/* Success Icon */}
        <SuccessIcon />

        {/* Message */}
        <View style={{ alignItems: 'center' }}>
          <Text style={{
            fontFamily: 'Unbounded_700Bold',
            fontSize: 28,
            color: '#E2FF31',
            marginBottom: 8,
            textAlign: 'center',
            textTransform: 'uppercase',
          }}>
            TRANSMISSION{'\n'}SUCCESS
          </Text>
          <Text style={{
            fontFamily: 'PlusJakartaSans_400Regular',
            color: '#A1A1AA',
            fontSize: 16,
          }}>
            Data payload received by authorities.
          </Text>
        </View>

        {/* Details */}
        <View style={{ width: '100%', gap: 16 }}>
          {trackingId && (
            <GlowingCard intensity="md" style={{ padding: 16, alignItems: 'center' }}>
              <Text style={{
                fontFamily: 'PlusJakartaSans_600SemiBold',
                color: '#71717A',
                fontSize: 12,
                marginBottom: 8,
                textTransform: 'uppercase',
                letterSpacing: 1,
              }}>
                TRACKING_ID
              </Text>
              <Text style={{
                color: '#FAFAFA',
                fontSize: 18,
                fontFamily: 'Unbounded_400Regular',
                letterSpacing: 2,
              }}>
                {trackingId}
              </Text>
            </GlowingCard>
          )}
        </View>

        {/* Buttons */}
        <View style={{ width: '100%', gap: 12, marginTop: 16 }}>
          <GlowingButton
            label="RETURN TO MAIN"
            onPress={handleReturnHome}
            size="lg"
            variant="primary"
          />
        </View>
      </View>
    </ScrollView>
  );
}
